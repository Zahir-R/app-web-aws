from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models.models import Base
from .routers import auth, chat

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Menopause Support API")

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to your Amplify domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])  # Enable to use routers of auth
app.include_router(chat.router, prefix="/chat", tags=["chat"])  # Enable to use routers of chat

@app.get("/")
def read_root():
    return {"message": "Welcome to the Menopause Support API"}
