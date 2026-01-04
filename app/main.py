from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.interview import router as interview_router
from app.api.v1.participants import router as participants_router
from app.api.v1.messages import router as messages_router

app = FastAPI(title="FastAPI Backend")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(interview_router)
app.include_router(participants_router)
app.include_router(messages_router)