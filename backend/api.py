from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Neo4j configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
    
    def user_exists(self, user_id):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User {id: $user_id})
                RETURN count(u) as count
            """, user_id=user_id)
            record = result.single()
            return record and record["count"] > 0
    
    def create_user(self, user_id, user_data=None):
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
        # Create user if not exists
        if not self.user_exists(user_id):
            self.create_user(user_id)
            return []  # New user has no interests yet
            
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User {id: $user_id})-[:INTERESTED_IN]->(i:Interest)
                RETURN i.id AS id, i.name AS name, i.description AS description
            """, user_id=user_id)
            return [dict(record) for record in result]
    
    def update_user_interests(self, user_id, interests):
        # Create user if not exists
        if not self.user_exists(user_id):
            self.create_user(user_id)
            
        with self.driver.session() as session:
            # Clear existing interests
            session.run("""
                MATCH (u:User {id: $user_id})-[r:INTERESTED_IN]->()
                DELETE r
            """, user_id=user_id)
            
            # Add new interests
            for interest in interests:
                # Check if interest exists, create if not
                session.run("""
                    MERGE (i:Interest {id: $id})
                    ON CREATE SET i.name = $name, i.description = $description
                    ON MATCH SET i.name = $name, i.description = $description
                    WITH i
                    MATCH (u:User {id: $user_id})
                    MERGE (u)-[:INTERESTED_IN]->(i)
                """, id=interest['id'], name=interest['name'], 
                     description=interest['description'], user_id=user_id)
            
            return True

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
        return jsonify(interests)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profile/interests/<user_id>', methods=['PUT'])
def update_interests(user_id):
    print(f'trying to update_interests: {user_id}')
    try:
        interests = request.json
        success = neo4j_conn.update_user_interests(user_id, interests)
        if success:
            return jsonify({"message": "Interests updated successfully"})
        else:
            return jsonify({"error": "Failed to update interests"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
