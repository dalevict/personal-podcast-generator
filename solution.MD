# Overview

This service produces short, medium and long-form podcasts based on the user's interests. The user can sign into an account, select interests, and then generate topics based on their interests. They can then choose any to generate a podcast and listen to it. They can also listen to their saved podcasts which are saved locally.
When the user logs in and enters their interests, the service suggest topics for podcasts.
Once the user has selected their subject, the service generates a guest character to come on the podcast, specialized in the topic and sharing some interests with the user, and with relevant news stories as additional context using Tavily's API. They will interact with the host, whose characteristics are hardcoded as Tina Johnson from South Africa (it fit the most natural sounding voice).
It then generates the dialog between them using the user's choice of number of converstaion turns (it is referred to as minutes in the frontend since it takes on average one minute for both characters to say one line). The prompt is constructed using the guest and host descriptions, the previous messages and some formatting constraints, and fed into `GPT 4.0 mini`.
Finally, the dialog is used to generate audio using the host and character. The service uses `GPT 4.0 mini` to choose a voice out of a hardcoded list best suited for the guest's character and reads the lines using the ElevenLabs `eleven_v3` model. The new podcast is opened in the user's library.



# Backend 

The backend is a simple FastAPI server that orchestrates a pipeline via Python classes `Researcher`, `Dialog`, and `Audio`. 
`Researcher` takes in the user's interests as a list of strings and generates podcast topics using the `subjects` method using `GPT 4.0 mini`, and researches extra context for the guest to use using the `fetch_context` method. 
`Dialog` generates the characters and dialog. Using LangGraph states, the prompts are generated based on the interests of the user and the subject of the podcast. The characters speak one after another, and use tone indicators like `[sighs]`, `[softly]` to prompt the audio generator to make them sound more natural.
Finally, the `Audio` class takes the dialog, as well as the description of the guest to choose their voice, and reads the dialog with alternating voices. These audio clips are then stitched together to produce the final `mp3` file. This file is stored locally in `backend/podcasts`.
The SQLite database decides which podcasts and which interests belong to which user. 



# Frontend

The frontend is a very minimalistic React single-page application that manages state-driven navigation through a `view` variable. It uses `useEffect` hooks to synchronize data, such as automatically fetching podcast topics when the user enters the generation screen. All pages run on the same "link", and the frontend simply changes which view is displayed. During generation, the UI switches to a loading state that renders a terminal-style debug log, because the research, dialog and audio generation take a long time (for 20 lines of conversation, it can take up to a minute). It plays generated audio by targeting a specific `/audio/` route served by the backend, mapping local filenames to HTML5 audio players.
There is also a metrics page.



# Design choices

The choice of using OpenAI and ElevenLabs is motivated by the API keys provided in the prompt [text](https://you.ashbyhq.com/prosper-ai/assignment/cff6a8c9-fb3b-4bfe-be9a-b6db58452b02). 
* While models like `GPT-5` are more creative, `GPT 4.0 mini` is preferred for text generation due to being faster and cheaper, which is important when processing a large volume of text lines.
* The ElevenLabs `eleven_v3` model is used for the audio generation. Using it is crucial because it allows more natural sounding speech and the use of tone indicators. 
* Tavily API is used for generating additional current context about the subject. Without this feature the podcast members will simply talk about the subject and not dive into any specific issue.



# Next steps

So far the project has many limitations:
* The frontend is minimal and counter-intuitive. 
* Error handling is non-existent. If the service runs out of API tokens for example the user will not know that the app has crashed.
* There are no security features: no encryption or passwords for the users. This is intentional as the podcasts are stored locally anyway. This allows them to all be stored in the same folder with the simple format ()
* There can only be two characters. This is somewhat intentional since the Host is always the same and the Guest is the one who has the most information about the topic, but some users may prefer to hear a large discussion rather than an "interview".
* The characters in `Dialog` generate their sentences one at a time, so the flow of conversation is very "turn-based" and they cannot interrupt each other, like in a normal conversation.
* The length of the dialog is set by the user instead of the chatbots deciding when to naturally end the conversation. This was decided in order to prevent tokens being wasted, and allows the user to set approximately how long they want their podcast to be. 
* The metrics page contains mock hardcoded values. This is for simplicity and also because there are very few users.
* In very rare cases, despite the prompts, the dialog may contain garbage such as extra "HOST:" statements, or off-topic remarks. 
* There can also be, very rarely, some audio tracks being cut off before finishing.