from app.db.mongo import db

def create_indexes():
    db.interviews.create_index(["created_at", -1])
    db.interviews.create_index(["status", 1])
    db.interviews.create_index(["interview_type", -1])
    db.interviews.create_index([("status", -1), ("created_at", -1)])

    #participants
    db.participants.create_index(
        [("interview_id", 1), ("user_email", 1)],
        unique = True
    )

    #messages
    db.messages.create_index(
        [("interview_id", 1), ("created_at", 1)]
    )

if __name__ == "__main__":
    create_indexes()
    print("Indexes created successfully")
