from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import numpy as np
import gensim
from gensim.models import KeyedVectors
import gensim.downloader as gensim_downloader
import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Neo4j configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Load the Word2Vec model
# Using the smaller 'glove-wiki-gigaword-100' model for demonstration
# Can use larger models like 'word2vec-google-news-300' for better results
print("Loading Word2Vec model...")
try:
    word2vec_model = gensim_downloader.load("glove-wiki-gigaword-100")
    print("Word2Vec model loaded")
except Exception as e:
    print(f"Error loading Word2Vec model: {e}")
    # Fallback to a smaller model if needed
    try:
        word2vec_model = gensim_downloader.load("glove-twitter-25")
        print("Fallback Word2Vec model loaded")
    except:
        print("Could not load any Word2Vec model. Using dummy vectors.")
        word2vec_model = None

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
    
    def user_exists(self, user_id):
        print(f'user_exists: {user_id}')
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User {id: $user_id})
                RETURN count(u) as count
            """, user_id=user_id)
            record = result.single()
            return record and record["count"] > 0
    
    def create_user(self, user_id, user_data=None):
        print(f'update_user_interests: {user_id} - user_data: {user_data}')

        if user_data is None:
            user_data = {}
        
        with self.driver.session() as session:
            session.run("""
                CREATE (u:User {id: $user_id, name: $name, lastUpdated: datetime(),
                               createdAt: datetime()})
            """, user_id=user_id, 
                 name=user_data.get("name", f"User {user_id}"))
            return True
            
    def get_user_interests(self, user_id):
        print(f'get_user_interests: {user_id}')

        # Create user if not exists
        if not self.user_exists(user_id):
            self.create_user(user_id)
            return []  # New user has no interests yet
            
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User {id: $user_id})-[:INTERESTED_IN]->(i:Interest)
                RETURN i.id AS id, i.name AS name, i.description AS description, 
                       i.vector AS vector
            """, user_id=user_id)

            print(f'result from database: {result}')
            return [dict(record) for record in result]
    
    def update_user_interests(self, user_id, interests):
        print(f'update_user_interests: {user_id} - interestings: {interests}')
        # Create user if not exists
        if not self.user_exists(user_id):
            self.create_user(user_id)
        
        # First transaction: Clear existing interests
        with self.driver.session() as session:
            try:
                session.run("""
                    MATCH (u:User {id: $user_id})-[r:INTERESTED_IN]->()
                    DELETE r
                """, user_id=user_id)
            except Exception as e:
                print(f"Error clearing existing interests: {e}")
        
        # Second transaction: Add new interests without duplication
        with self.driver.session() as session:
            try:
                for interest in interests:
                    # Generate vector for interest
                    vector = text_to_vector(interest['name'])
                    print(f'vector result: {vector}')
                    vector_list = vector.tolist() if isinstance(vector, np.ndarray) else vector
                    
                    # Verify user exists before creating relationships
                    verify_user = session.run("""
                        MATCH (u:User {id: $user_id})
                        RETURN count(u) as count
                    """, user_id=user_id).single()
                    
                    if verify_user["count"] == 0:
                        print(f"User {user_id} not found, recreating")
                        self.create_user(user_id)
                    
                    # Use MERGE for both nodes and relationships to prevent duplication
                    result = session.run("""
                        MERGE (i:Interest {id: $id})
                        ON CREATE SET i.name = $name, i.description = $description,
                                    i.vector = $vector
                        ON MATCH SET i.name = $name, i.description = $description,
                                i.vector = $vector
                        WITH i
                        MATCH (u:User {id: $user_id})
                        MERGE (u)-[:INTERESTED_IN]->(i)
                        RETURN count(u) as user_count
                    """, id=interest['id'], name=interest['name'],
                        description=interest['description'], vector=vector_list,
                        user_id=user_id)
                    
                    record = result.single()
                    if record and record["user_count"] == 0:
                        print(f"Warning: Failed to find user: {user_id}")
                
                print('successfully sent to database')
                return True
                
            except Exception as e:
                print(f"Error adding interests: {e}")
                return False
    
    @staticmethod
    def cosine_similarity(a, b):
        a, b = np.array(a), np.array(b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return np.dot(a, b) / (norm_a * norm_b)

    def find_similar_interests(self, interest_id, limit=10):
        print(f'find_similar_interests: {interest_id} - limit: {limit}')

        final_results = {
            "similar_interests": [],
            "recommended_users": [],
            "timestamp": None
        }

        with self.driver.session() as session:
            # Get the source interest vector

            print(f'Types: interest_id: {type(interest_id)}')

            source_query = """
                MATCH (i:Interest)
                WHERE i.id = $interest_id
                RETURN i.id AS id, i.name AS name, i.vector AS vector
            """
            source_result = session.run(source_query, interest_id=int(interest_id))

            print(f'source_result: {source_result}')

            source_record = source_result.single()
            print(f'source_record: {source_record}')
            

            # surely I can just ignore this
            # print(not source_record or "vector" not in source_record or source_record["vector"] is None)
            # if not source_record or "vector" not in source_record or source_record["vector"] is None:
            #     print(f"No source interest found or source interest has no vector for id: {interest_id}")
            #     # Set timestamp even if nothing found
            #     final_results["timestamp"] = datetime.datetime.now(datetime.UTC).isoformat() 
            #     # Removed '+Z' as isoformat() on timezone-aware object includes offset
            #     return final_results
                
            source_vector = source_record["vector"]
            print(f"Source interest: {source_record['id']} - {source_record['name']}")

            # Pull a random sample of interests with vectors, excluding the source interest
            sample_query = """
                MATCH (other:Interest)
                // Ensure the comparison handles potential type differences if needed, like source query
                WHERE other.vector IS NOT NULL AND toString(other.id) <> toString($interest_id) 
                RETURN other.id AS id, other.name AS name, other.description AS description, other.vector AS vector
                ORDER BY rand()
                LIMIT 100 
            """ # Increased limit slightly for better candidate pool before filtering
            sample_result = session.run(sample_query, interest_id=source_record["id"]) # Use the actual ID found
            candidates = list(sample_result)
            print(f"Found {len(candidates)} candidate interests for similarity check")

            # Compute cosine similarity using numpy
            similarity_threshold = 0.5 # Adjust as needed
            similarities = []
            for candidate in candidates:
                candidate_vector = candidate["vector"]
                # Ensure candidate_vector is not None before calculating similarity
                if candidate_vector is not None:
                    sim = self.cosine_similarity(source_vector, candidate_vector)
                    similarities.append((candidate, sim))
                else:
                    print(f"Warning: Candidate interest {candidate['id']} has NULL vector.")
            
            # Filter and sort candidates based on similarity
            filtered_candidates = [
                (cand, sim) for (cand, sim) in similarities if sim > similarity_threshold
            ]
            sorted_candidates = sorted(filtered_candidates, key=lambda x: x[1], reverse=True)
            top_candidates = sorted_candidates[:limit] # Apply limit to similar *interests*

            # Prepare the similar interests result list
            similar_interests_results = []
            for candidate, sim in top_candidates:
                similar_interests_results.append({
                    "id": candidate["id"],
                    "name": candidate["name"],
                    "description": candidate.get("description", ""), # Use .get for safety
                    "similarity": sim
                })
            
            final_results["similar_interests"] = similar_interests_results
            
            # --- Datetime calculation using the new method ---
            current_dt = datetime.datetime.now(datetime.UTC)


            # UNCOMMENT FOR DEBUG / REMOVE ONE HOUR TIME COOLDOWN
            #one_hour_ago_dt = current_dt
            one_hour_ago_dt = current_dt - datetime.timedelta(hours=1)
            
            # Format for Neo4j (ISO 8601 format usually works well)
            current_time_iso = current_dt.isoformat() 
            one_hour_ago_iso = one_hour_ago_dt.isoformat()
            
            # Update the timestamp in the final results
            final_results["timestamp"] = current_time_iso






            # --- Find users ---
            similar_interest_ids = [item["id"] for item in similar_interests_results]
            
            # Proceed only if we found similar interests
            if not similar_interest_ids:
                print("No sufficiently similar interests found to recommend users.")
                return final_results # Return interests found (if any) and timestamp

            users_query = """
            MATCH (u:User)-[r:INTERESTED_IN]->(i:Interest)
            WHERE i.id IN $interest_ids
            // Use standard datetime comparison if u.lastUpdated is stored as DateTime
            AND (u.lastUpdated IS NULL OR u.lastUpdated < datetime($one_hour_ago_iso)) 
            WITH u, i, r
            ORDER BY u.id, i.id // Ordering here might not be necessary if only collecting interests per user
            RETURN u.id AS user_id, u.name AS user_name, 
                collect(distinct {interest_id: i.id, interest_name: i.name}) AS interests
            LIMIT 100 // Limit the number of users fetched initially
            """
            
            users_result = session.run(users_query, 
                                    interest_ids=similar_interest_ids,
                                    one_hour_ago_iso=one_hour_ago_iso)
            users = list(users_result)
            print(f"Found {len(users)} potential users with relevant interests.")
            
            # Calculate user scores based on weighted interests
            user_scores = []
            # Create weight map from the *actual* similar interests found and limited
            interest_weights = {item["id"]: item["similarity"] for item in similar_interests_results} 
            
            for user in users:
                score = 0.0 # Use float for score
                matched_user_interests = [] # Store interests that contributed to score
                for interest in user["interests"]:
                    interest_id = interest["interest_id"]
                    if interest_id in interest_weights:
                        score += interest_weights[interest_id]
                        matched_user_interests.append(interest) # Add this interest
                
                # Only include users who actually matched one of the target interests
                if score > 0: 
                    user_scores.append({
                        "user_id": user["user_id"],
                        "user_name": user["user_name"],
                        "interests": matched_user_interests, # Show only relevant interests? Or all? user["interests"]
                        "score": score
                    })
            
            # Sort users by score and return top results (apply limit to users here)
            sorted_users = sorted(user_scores, key=lambda x: x["score"], reverse=True)
            top_users = sorted_users[:limit] # Apply limit to *users*
            final_results["recommended_users"] = top_users

            # --- Update timestamps for recommended users ---
            top_user_ids = [user["user_id"] for user in top_users]
            
            if top_user_ids:
                # Ensure you are storing datetime objects in Neo4j for this comparison
                update_query = """ 
                MATCH (u:User)
                WHERE u.id IN $user_ids
                SET u.lastUpdated = datetime($current_time_iso) 
                RETURN count(u) as updated_count
                """
                
                try:
                    update_result = session.run(update_query, 
                                            user_ids=top_user_ids,
                                            current_time_iso=current_time_iso)
                    update_count = update_result.single()["updated_count"]
                    print(f"Updated lastUpdated timestamp for {update_count} users")
                except Exception as e:
                    print(f"Error updating user timestamps: {e}")
                    # Decide if you want to fail the whole operation or just log the error

        return final_results
        
def text_to_vector(text):
    print('text_to_vector')

    print(f'Type of text: {type(text)} - Value: {text}')


    """Convert text to a vector using Word2Vec"""
    if not text:
        print('Not Text! return default vec size')
        return [0.0] * (100 if word2vec_model else 25)  # Default vector size
        
    
    if word2vec_model is None:
        print('model is None!')
        # Return a dummy vector if no model is available
        return [0.0] * 25
    
    # words = gensim.utils.simple_preprocess(text)
    try:
        print(text)
        text = text.encode('utf-8').decode('utf-8')
        print(text)
        words = gensim.utils.simple_preprocess(text)
    except Exception as e:
        print(f'Error during preprocessing (encoding issue): {e}')


    print(f'processed - words: {words}')
    vectors = []
    
    for word in words:
        if word in word2vec_model:
            vectors.append(word2vec_model[word])
    
    print('finished appending words')

    if not vectors:
        print('not vectors')
        # Return zeros if no words were found in the model
        return [0.0] * word2vec_model.vector_size
    
    # Average the vectors
    vector = np.mean(vectors, axis=0)
    print(f'vector: {vector}')
    return vector

# Initialize Neo4j connection
neo4j_conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

@app.route('/api/profile/<user_id>', methods=['POST'])
def create_user(user_id):
    print(f'trying to create_user: {user_id}')
    try:
        user_data = request.json or {}
        if neo4j_conn.user_exists(user_id):
            return jsonify({"message": "User already exists"}), 200
            
        success = neo4j_conn.create_user(user_id, user_data)
        if success:
            return jsonify({"message": "User created successfully"})
        else:
            return jsonify({"error": "Failed to create user"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profile/interests/<user_id>', methods=['GET'])
def get_interests(user_id):
    print(f'trying to get_interests: {user_id}')
    try:
        interests = neo4j_conn.get_user_interests(user_id)
        print(f'got interests: {interests}')

        return jsonify(interests)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profile/interests/<user_id>', methods=['PUT'])
def update_interests(user_id):
    print(f'trying to update_interests: {user_id}')
    try:
        print(f'request: {request.json}')
        interests = request.json
        success = neo4j_conn.update_user_interests(user_id, interests)
        if success:
            return jsonify({"message": "Interests updated successfully"})
        else:
            return jsonify({"error": "Failed to update interests"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/interests/similar/<interest_id>', methods=['GET'])
def find_similar_interests(interest_id):
    print(f'Finding interests similar to: {interest_id}')
    try:
        limit = request.args.get('limit', default=10, type=int)
        similar_interests = neo4j_conn.find_similar_interests(interest_id, limit)
        return jsonify(similar_interests)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
