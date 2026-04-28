import os
import audio
import dialog
from pathlib import Path

def save_local(audio, filename="daily_podcast.mp3"):
    output_dir = Path("./podcasts")
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / filename
    audio.export(file_path, format="mp3")
    print(f"Podcast saved to: {file_path}")

# TODO: add user with interests 

# TODO: make frontend in react for localhost or smth

# TODO: make solution.md and README.md populated

dialogg = dialog.final_state['messages']
audioo = audio.generate_podcast_audio(dialogg)
save_local(audioo)  