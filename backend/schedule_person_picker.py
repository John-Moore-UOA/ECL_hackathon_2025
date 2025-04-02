import schedule
import numpy as np
import time
import random
import requests
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
VITE_API_URL = os.getenv("VITE_API_URL")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def get_random_user_interest():
    print(f'get random user')


    """Fetch a random interest ID and the corresponding user ID."""
    with driver.session() as session:
        result = session.run(
            "MATCH (u:User)-[:INTERESTED_IN]->(i:Interest) "
            "WITH u, COLLECT(i.id) AS interests, u.id AS user_id "
            "WHERE SIZE(interests) > 0 "
            "RETURN user_id, interests "
            "ORDER BY rand() "
            "LIMIT 1"
        )
        record = result.single() # Get the single returned record.

        print(f'record: {record}')


        if record:
            interests = record["interests"] # Access the list of interests
            user_id = record["user_id"] # access the user_id

            print(f'interests: {interests}')

            if interests:
                return random.choice(interests), user_id # return both the interestID and the user_id
            else:
                print("No interests found for the randomly selected user.")
                return None, None
        else:
            print("No users with interests found.")
            return None, None


def fetch_similar_users():
    """Fetch and print similar users for a random interest, ensuring the user ID is unique."""
    interest_id, original_user_id = get_random_user_interest()
    if interest_id is None:
        return

    print(f'interest_id: {interest_id}')


    # /api/interests/similar/<interest_id>
    response = requests.get(f"{VITE_API_URL}/interests/similar/{interest_id}")

    print(f'resp: {response.json()}')

    if response.status_code == 200:
        similar_users_json = response.json()
        print(f'Similar Users Found: {similar_users_json}')
        similar_users = get_user_ids(similar_users_json)
        return similar_users
    else:
        print(f"Failed to fetch similar users. Status Code: {response.status_code}")


def get_user_ids(similar_users):
    user_ids = []
    if 'recommended_users' in similar_users:
        for user in similar_users['recommended_users']:
            user_ids.append(user['user_id'])
    return user_ids



# Schedule the task to run every 5 minutes
#schedule.every(1).minutes.do(fetch_similar_users)

print("Scheduler started. Running every 5 minutes...")

# # Keep the script running
# while True:
#     schedule.run_pending()
#     time.sleep(1)

user_id_list = fetch_similar_users()
print(user_id_list)

