import os
import random
from dotenv import load_dotenv
from pymongo import MongoClient
from faker import Faker
import uuid
from datetime import datetime, timezone

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
mongo_db = os.getenv("MONGO_DB")
collection_name = os.getenv("MONGO_COLLECTION", "production_collection")

client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[collection_name]

faker = Faker()

INTERVIEW_TYPES = ["backend", "ml", "hr", "system_design"]
ROLES = ["interviewer", "participant"]
SENTIMENTS = ["confident", "neutral", "nervous", "excited"]

INTERVIEW_QUESTIONS = [
    "Can you explain how REST differs from RPC?",
    "How would you design a scalable data ingestion pipeline?",
    "What happens during an HTTP preflight request?",
    "How do you handle idempotency in APIs?",
    "Explain caching strategies in distributed systems.",
    "How would you secure a public-facing REST API?",
    "What trade-offs exist between sync and async processing?"
]

INTERVIEW_ANSWERS = [
    "I would separate ingestion from processing using a queue.",
    "I would use idempotency keys and proper HTTP semantics.",
    "Caching should be layered using HTTP headers and Redis.",
    "Security starts with authentication and rate limiting.",
    "Async pipelines help scale without blocking requests."
]

def generate_message(role):
    if role == "interviewer":
        return random.choice(INTERVIEW_QUESTIONS)
    return random.choice(INTERVIEW_ANSWERS)

def generate_document(conversation_id):
    role = random.choice(ROLES)
    return {
        "conversation_id": conversation_id,
        "speaker_name": faker.name(),
        "speaker_email": faker.email(),
        "role": role,
        "interview_type": random.choice(INTERVIEW_TYPES),
        "message": generate_message(role),
        "sentiment": random.choice(SENTIMENTS),
        "created_at": datetime.now(timezone.utc)
    }

def main():
    documents = []

    for _ in range(20):  # 20 conversations
        conversation_id = str(uuid.uuid4())
        turns = random.randint(3, 7)

        for _ in range(turns):
            documents.append(generate_document(conversation_id))

    collection.insert_many(documents)
    print(f"Inserted {len(documents)} interview conversation records")

if __name__ == "__main__":
    main()