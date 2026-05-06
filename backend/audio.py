import os

from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import io

from pathlib import Path

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI


import random

from elevenlabs import VoiceSettings



class Audio:
    
    def __init__(self, debug = True, dialog = "", verbose = False, subject="", guest_desc=''):
        self.debug = debug
        self.dialog = dialog
        load_dotenv(dotenv_path="backend/env/elevenlabs.env")
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.verbose = verbose
        self.subject = subject
        self.guest_voices = [{'hwnuNyWkl9DjdTFykrN6':'Brazilian Male'},
                            {'RWLFUuahyl6QdlLs8Al5':'Eastern Male'},
                            {'gSYqSbtMajxq5LUT0bNl':'Indian Male'},
                            {'4QLC5fepxZkYmdD2IGRU':'American Male'},
                            {'VHYWoxffK1pFlM1dtRb0':'German Male'},
                            {'y0SYydk17lMbUIUvSf3N':'British Male'},
                            {'VUGQSU6BSEjkbudnJbOj':'White American Female'},
                            {'T3b0vsQ5dQwMZ5ckOwBk':'Middle Eastern American Female'},
                            {'CiwzbDpaN3pQXjTgx3ML':'Italian Female'},
                            {'IKuPqyuiEnnZFcU4OVzH':'Asian American Female'},
                            {'54YYBuRuAG6KJooiOhFI':'Eastern European Female'}
                            ]
        self.guest_desc = guest_desc
        print(guest_desc)

    def result(self):
        combined_audio = AudioSegment.empty() 
        voices = {"HOST": "Z0QKopwR1e0SJMnL0DU0", # 21m00Tcm4TlvDq8ikWAM # sXSV9RZ095VZyL64w3ap  # T3b0vsQ5dQwMZ5ckOwBk
                "GUEST": self.select_voice()}
                # "GUEST" : '4QLC5fepxZkYmdD2IGRU'}
        stability = random.uniform(0.25, 0.5)
        style = random.uniform(0.25, 0.75)
        speed = random.uniform(0.5, 1)
        if self.debug:
            return 'backend/podcasts/'
        else:
            for line in self.dialog:
                if not self.dialog or self.dialog == "" or self.dialog == None:
                    break
                if self.verbose:
                    print(f"==> USING {line} <==")
                    print(voices)
                if line['role'] == 'GUEST':
                    print("VOICE: ", voices[line['role']])
                    audio_stream = self.client.text_to_speech.stream( # TODO: fix occasional audio track being cut off
                        text=line['content'],
                        voice_id=voices[line['role']],
                        model_id="eleven_v3",
                        voice_settings=VoiceSettings(
                            speed = speed,
                            stability=stability,
                            similarity_boost=0.6, 
                            style=style,
                            use_speaker_boost=True
                        )
                    )
                elif line['role'] == 'HOST':
                    print("VOICE: ", voices[line['role']])
                    audio_stream = self.client.text_to_speech.stream(
                        text=line['content'],
                        voice_id=voices[line['role']],
                        model_id="eleven_v3",
                        voice_settings=VoiceSettings(
                            speed = 0.8,
                            stability=0.25,
                            similarity_boost=0.5, 
                            style=0.5,
                            use_speaker_boost=True
                        )
                    )
                else:
                    break
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
        

    def select_voice(self):
        if self.guest_desc is None or self.guest_desc == '':
            if self.verbose:
                print("Empty voices")
            return next(iter(random.choice(self.guest_voices).keys()))
        else:
            load_dotenv(dotenv_path="backend/env/openai.env")
            self.llm = ChatOpenAI(model="gpt-4o")
            prompt = "Here is a charater description (ignore the 2nd person): '"
            prompt += self.guest_desc
            prompt += "' Which voice would you choose out of the following dictionnary?: '"
            prompt += str(self.guest_voices)
            prompt += "' Only output the code. For example, if the character is American, just output '4QLC5fepxZkYmdD2IGRU' (without quotations). "
            response = self.llm.invoke(prompt).content
            if len(response) != len('hwnuNyWkl9DjdTFykrN6'):
                if self.verbose:
                    print("Random voice chosen")
                return next(iter(random.choice(self.guest_voices).keys()))
            else: 
                if self.verbose:
                    print("Voice chosen: ", response)
                return response
            