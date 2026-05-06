## See solution.md for a breakdown of the solution in more detail


# How to run this

This services requires the following API keys, in the `backend/env` folder:
* `elevenlabs.env`
* `openai.env`
* `tavily.env`
The ElevenLabs and OpenAI keys require a paid subscription. To run without any external requests, change this [line](https://github.com/dalevict/personal-podcast-generator/blob/4df25f7ecad29a974457661bce86d13c6c42c012/backend/api.py#L37) to `debug = True`.
Please also note that this was written on an Ubuntu machine and not tested in any other environment.


# Overview

This service produces short, medium and long-form podcasts based on the user's interests. The user can sign into an account, select interests, and then generate topics based on their interests. They can then choose any to generate a podcast and listen to it. They can also listen to their saved podcasts which are saved locally.  
When the user logs in and enters their interests, the service suggest topics for podcasts.  
Once the user has selected their subject, the service generates a guest character to come on the podcast, specialized in the topic and sharing some interests with the user, and with relevant news stories as additional context using Tavily's API. They will interact with the host, whose characteristics are hardcoded as Tina Johnson from South Africa (it fit the most natural sounding voice).  
It then generates the dialog between them using the user's choice of number of converstaion turns (it is referred to as minutes in the frontend since it takes on average one minute for both characters to say one line). The prompt is constructed using the guest and host descriptions, the previous messages and some formatting constraints, and fed into `GPT 4.0 mini`.  
Finally, the dialog is used to generate audio using the host and character. The service uses `GPT 4.0 mini` to choose a voice out of a hardcoded list best suited for the guest's character and reads the lines using the ElevenLabs `eleven_v3` model. The new podcast is opened in the user's library.  
