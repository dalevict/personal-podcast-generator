from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.researcher import Researcher
import os
from backend.database import init_db, save_user, get_user_interests, log_podcast

app = FastAPI()

init_db()

# Serve your local podcasts folder so React can play the audio files
app.mount("/audio", StaticFiles(directory="podcasts"), name="audio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/login")
def login(username: str):
    # If user doesn't exist, create them with empty interests
    existing = get_user_interests(username)
    if not existing:
        save_user(username, [])
    return {"username": username, "interests": existing}

@app.get("/subjects")
def get_subjects(username: str):
    # Fetch interests directly from the DB[cite: 1]
    interests = get_user_interests(username)
    # Use your Researcher class to find news
    res = Researcher(interests=interests) 
    return {"subjects": res.subjects()}

@app.post("/generate")
def generate_podcast(subject: str, username: str):
    return {"status": "success", "filename": f"{username}_podcast.mp3"}

@app.get("/my-podcasts")
def list_podcasts(username: str):
    files = [f for f in os.listdir("podcasts") if f.startswith(username)]
    return {"podcasts": files}