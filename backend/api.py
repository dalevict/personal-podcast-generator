from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.researcher import Researcher
import os
from backend.database import init_db, save_user, get_user_interests, log_podcast
from pydantic import BaseModel
from typing import List
from backend.dialog import Dialog
from backend.audio import Audio
import os



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

@app.post("/generate-podcast")
async def generate_podcast(username: str, subject: str):
    debug = False
    verbose = True
    turns = 10
    interests = get_user_interests(username)
    podcast = "Prosper Podcast, a chill podcast for young people in Europe about interesting topics in the world today"
    dialog_instance = Dialog(
        subject=subject,
        podcast=podcast,
        vibe="chill",
        interests=interests,
        debug=debug,
        turns=turns,
        verbose=verbose
    )
    script = dialog_instance.result()
    audio_instance = Audio(
        subject=subject,
        debug=debug,
        dialog=script,
        verbose = verbose,
        guest_desc=dialog_instance.guest_description
    )
    audio_path = audio_instance.result()
    new_filename = f"{username}_{os.path.basename(audio_path)}"
    new_path = os.path.join("backend/podcasts", new_filename)
    os.rename(audio_path, new_path)
    return {"status": "success", "file": new_filename}


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
    interests = get_user_interests(username)
    researcher = Researcher(
        interests=interests,
        podcast="Prosper Podcast, a chill podcast for young people in Europe about interesting topics in the world today",
        debug=False,
        verbose=False
    )
    subjects = researcher.subjects()
    clean_subjects = [s.strip() for s in subjects if s and s.strip()]
    return {"subjects": clean_subjects}

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