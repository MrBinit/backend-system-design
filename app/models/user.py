from datetime import datetime
class User:
    def __init__(self, email: str, hashed_password: str, role: str):
        self.email = email
        self.hashed_password = hashed_password
        self.role = role
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return{
            "email": self.email,
            "hashed_password": self.hashed_password,
            "role": self.role,
            "created_at": self.created_at,
        }