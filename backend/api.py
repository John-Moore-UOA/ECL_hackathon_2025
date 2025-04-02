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
                CREATE (u:User {id: $user_id, name: $name, email: $email, 
                               createdAt: datetime()})
            """, user_id=user_id, 
                 name=user_data.get("name", f"User {user_id}"),
                 email=user_data.get("email", ""))
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

                print('sending to database')                
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
    
    def find_similar_interests(self, interest_id, limit=10):
        print(f'find_similar_interests: {interest_id} - limit: {limit}')

        """Find interests similar to the given interest based on vector similarity"""
        with self.driver.session() as session:
            # First get the vector of the source interest
            result = session.run("""
                MATCH (i:Interest {id: $interest_id})
                RETURN i.vector AS vector
            """, interest_id=interest_id)
            
            record = result.single()
            if not record or not record.get("vector"):
                return []
            
            # Then find similar interests using cosine similarity calculation in Neo4j
            result = session.run("""
                MATCH (source:Interest {id: $interest_id})
                MATCH (other:Interest)
                WHERE source <> other AND other.vector IS NOT NULL
                WITH source, other, 
                     gds.similarity.cosine(source.vector, other.vector) AS similarity
                WHERE similarity > 0.5  // Minimum similarity threshold
                RETURN other.id AS id, other.name AS name, 
                       other.description AS description, similarity
                ORDER BY similarity DESC
                LIMIT $limit
            """, interest_id=interest_id, limit=limit)
            
            return [dict(record) for record in result]

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
