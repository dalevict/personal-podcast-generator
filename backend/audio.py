import os

from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import io

from pathlib import Path

from dotenv import load_dotenv



class Audio:
    
    def __init__(self, debug = True, dialog = "", verbose = False, subject=""):
        self.debug = debug
        self.dialog = dialog
        load_dotenv(dotenv_path="backend/env/elevenlabs.env")
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.verbose = verbose
        self.subject = subject

    def result(self):
        combined_audio = AudioSegment.empty()
        voices = {"HOST": "21m00Tcm4TlvDq8ikWAM", 
                "GUEST": "21m00Tcm4TlvDq8ikWAM"} # TODO: fix rachel talking to herself
        for line in self.dialog:
            if self.debug or self.dialog == "" or self.dialog == None:
                break
            if self.verbose:
                print(f"==> {line} <==")
                print(voices)
            audio_stream = self.client.text_to_speech.stream( # TODO: fix occasional audio track being cut off
                text=line['content'],
                voice_id=voices[line['role']],
                model_id="eleven_multilingual_v2"
            )
            if self.verbose:
                print("=======================================================================")
            segment = AudioSegment.from_file(io.BytesIO(b"".join(audio_stream)), format="mp3") # TODO: optimize
            combined_audio += segment + AudioSegment.silent(duration=600)
        path = f"backend/podcasts/{self.subject}.mp3"
        combined_audio.export(path, format="mp3")
        return path

    # def save_local(script):
    #     file_path = "dialog/dialog.txt"
    #     with open(file_path, "w") as f:
    #         for line in script:
    #             f.write(f"{line['role']}: {line['content']}\n")
    #     print(f"Dialog saved to: {file_path}")
    
    def save_local(self):
        output_dir = Path("./podcasts")
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = self.subject
        file_path = output_dir / filename
        self.audio.export(file_path, format="mp3")
        print(f"Podcast saved to: {file_path}")