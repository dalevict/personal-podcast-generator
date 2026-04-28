import os

from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import io
from dotenv import load_dotenv

load_dotenv(dotenv_path="openai.env")
load_dotenv(dotenv_path="elevenlabs.env")

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def generate_podcast_audio(script):
    save_local(script)
    combined_audio = AudioSegment.empty()
    voices = {"Host": "21m00Tcm4TlvDq8ikWAM", "Guest": "21m00Tcm4TlvDq8ikWAM"} # TODO: fix rachel talking to herself

    for line in script:
        audio_stream = client.text_to_speech.stream(
            text=line['content'],
            voice_id=voices[line['role']],
            model_id="eleven_multilingual_v2"
        )
        segment = AudioSegment.from_file(io.BytesIO(b"".join(audio_stream)), format="mp3") # TODO: optimize
        combined_audio += segment + AudioSegment.silent(duration=600)
    return combined_audio

def save_local(script):
    file_path = "dialog/dialog.txt"
    with open(file_path, "w") as f:
        for line in script:
            f.write(f"{line['role']}: {line['content']}\n")
    print(f"Dialog saved to: {file_path}")