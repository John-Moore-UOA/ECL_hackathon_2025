import schedule
import time
import random
import requests
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get secrets from .env
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
VITE_API_URL = os.getenv("VITE_API_URL")

# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

import random

def get_random_user_interest():
    """Fetch a random interest ID that belongs to the given user."""
    with driver.session() as session:
        result = session.run(
            "MATCH (u:User)-[:HAS_INTEREST]->(i:Interest) "
            "WITH u, COLLECT(i.id) AS interests "
            "WHERE SIZE(interests) > 0 "
            "RETURN u.id AS user_id, interests "
            "ORDER BY rand() "
            "LIMIT 1"
        )
        interests = [record["interest_id"] for record in result]
        
        if not interests:
            print(f"No interests found for user {result}.")
            return None

        return random.choice(interests)


def fetch_similar_users():
    """Fetch and print similar users for a random interest."""
    interest_id = get_random_user_interest()
    if interest_id is None:
        return
    

    # /api/interests/similar/<interest_id>
    response = requests.get(f"{VITE_API_URL}/interests/similar/{interest_id}")
    
    if response.status_code == 200:
        similar_users = response.json()
        print(f"Similar users for interest {interest_id}: {similar_users}")
    else:
        print(f"Failed to fetch similar users. Status Code: {response.status_code}")

# Schedule the task to run every 5 minutes
#schedule.every(1).minutes.do(fetch_similar_users)

print("Scheduler started. Running every 5 minutes...")

# # Keep the script running
# while True:
#     schedule.run_pending()
#     time.sleep(1)

fetch_similar_users()
