from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import numpy as np
import gensim
from gensim.models import KeyedVectors
import gensim.downloader as gensim_downloader

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
            
        with self.driver.session() as session:
            # Clear existing interests
            session.run("""
                MATCH (u:User {id: $user_id})-[r:INTERESTED_IN]->()
                DELETE r
            """, user_id=user_id)
            
            # Add new interests with vectors
            for interest in interests:
                # Generate vector for interest
                vector = text_to_vector(interest['name'])

                print(f'vector result: {vector}')

                vector_list = vector.tolist() if isinstance(vector, np.ndarray) else vector

                print(f'\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nsending to database {vector_list}\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')                
                # Check if interest exists, create if not with vector
                session.run("""
                    MERGE (i:Interest {id: $id})
                    ON CREATE SET i.name = $name, i.description = $description, 
                                 i.vector = $vector
                    ON MATCH SET i.name = $name, i.description = $description, 
                              i.vector = $vector
                    WITH i
                    MATCH (u:User {id: $user_id})
                    MERGE (u)-[:INTERESTED_IN]->(i)
                """, id=interest['id'], name=interest['name'], 
                     description=interest['description'], vector=vector_list, 
                     user_id=user_id)
                
            print('successfully sent to databse')
            return True
    
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

        with self.driver.session() as session:
            # Get the source interest vector
            source_query = """
                MATCH (i:Interest)
                WHERE i.id = $interest_id OR i.id = toString($interest_id) OR i.id = toInteger($interest_id)
                RETURN i.id AS id, i.name AS name, i.vector AS vector
            """
            source_result = session.run(source_query, interest_id=interest_id)
            source_record = source_result.single()
            if not source_record:
                print("No source interest found")
                return []
            source_vector = source_record["vector"]
            print(f"Source interest: {source_record}")

            # Pull a random sample of 100 interests with vectors, excluding the source interest
            sample_query = """
                MATCH (other:Interest)
                WHERE other.vector IS NOT NULL AND other.id <> $interest_id
                RETURN other.id AS id, other.name AS name, other.description AS description, other.vector AS vector
                ORDER BY rand()
                LIMIT 100
            """
            sample_result = session.run(sample_query, interest_id=interest_id)
            candidates = list(sample_result)
            print(f"Found {len(candidates)} candidate interests")

            # Compute cosine similarity using numpy
            similarity_threshold = 0.5  # Optional: only keep candidates with similarity above this threshold
            similarities = []
            for candidate in candidates:
                candidate_vector = candidate["vector"]
                sim = self.cosine_similarity(source_vector, candidate_vector)
                similarities.append((candidate, sim))
            
            # Filter and sort candidates based on similarity
            filtered_candidates = [
                (cand, sim) for (cand, sim) in similarities if sim > similarity_threshold
            ]
            sorted_candidates = sorted(filtered_candidates, key=lambda x: x[1], reverse=True)
            top_candidates = sorted_candidates[:limit]

            # Prepare the final result list
            results = []
            for candidate, sim in top_candidates:
                results.append({
                    "id": candidate["id"],
                    "name": candidate["name"],
                    "description": candidate.get("description", ""),
                    "similarity": sim
                })
            
        # Get users with similar interests, with weighted bias towards more similar interests
        similar_interest_ids = [item["id"] for item in results]
        
        # Pull a random sample of users who have any of these interests
        users_query = """
        MATCH (u:User)-[r:INTERESTED_IN]->(i:Interest)
        WHERE i.id IN $interest_ids
        WITH u, i, r
        ORDER BY u.id, i.id
        RETURN u.id AS user_id, u.name AS user_name, 
               collect(distinct {interest_id: i.id, interest_name: i.name}) AS interests
        LIMIT 100
        """
        
        users_result = session.run(users_query, interest_ids=similar_interest_ids)
        users = list(users_result)
        
        # Calculate user scores based on weighted interests
        user_scores = []
        interest_weights = {item["id"]: item["similarity"] for item in results}
        
        for user in users:
            score = 0
            for interest in user["interests"]:
                interest_id = interest["interest_id"]
                if interest_id in interest_weights:
                    score += interest_weights[interest_id]
            
            user_scores.append({
                "user_id": user["user_id"],
                "user_name": user["user_name"],
                "interests": user["interests"],
                "score": score
            })
        
        # Sort users by score and return top results
        sorted_users = sorted(user_scores, key=lambda x: x["score"], reverse=True)
        top_users = sorted_users[:limit]
        
        # Add users to results
        final_results = {
            "similar_interests": results,
            "recommended_users": top_users
        }
        
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
