from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.researcher import Researcher
import os
from backend.database import init_db, save_user, get_user_interests, log_podcast
from pydantic import BaseModel
from typing import List



class InterestUpdate(BaseModel):
    username: str
    interests: List[str]
    
    
    
app = FastAPI()

init_db()

# Serve your local podcasts folder so React can play the audio files
app.mount("/audio", StaticFiles(directory="backend/podcasts"), name="audio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/update-interests")
def update_interests(data: InterestUpdate):
    # 'data' will now automatically have .username and .interests
    save_user(data.username, data.interests)
    return {"status": "success", "interests": data.interests}

@app.post("/login")
def login(username: str):
    existing = get_user_interests(username) 
    if existing is None:
        save_user(username, [])
        existing = []
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
    folder_path = "backend/podcasts"
    if not os.path.exists(folder_path):
        return {"podcasts": [], "error": "Folder not found"}
    files = [f for f in os.listdir(folder_path) if f.startswith(username)]
    return {"podcasts": files}