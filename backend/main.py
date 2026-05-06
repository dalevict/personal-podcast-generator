import os
import random


from audio import Audio
from dialog import Dialog
from researcher import Researcher



max_turns = 1 # total voice lines should be 2 * max_turns + 1 since the host starts and concludes

debug = False
# debug = True

verbose = True

subject = "israel and palestine"
interests = ['arts', 'cinema', 'DEI', 'dogs', 'food', 'sports', 'travel']
# interests = ['test']
podcast = "Prosper Podcast, a chill podcast for young people in Europe about interesting topics in the world today",


# TODO: fix spaghetti code, other todos

# TODO: make solution.md and README.md populated

researcher = Researcher(
        interests=interests, 
        podcast=podcast, 
        debug=debug, 
        verbose=verbose,
        subject=subject
    )

dialogg = Dialog(
        subject = subject,
        podcast = podcast,
        vibe = "chill",
        interests = interests,
        debug = debug,
        turns = 5,
        verbose = verbose,
        context = researcher.fetch_context()
)
script = dialogg.result()
# audioo = Audio(
#     subject = subject,
#     debug=debug, 
#     # dialog=[
#     #     {"role": "HOST", "content": "Hello, nice to meet you!"},
#     #     {"role": "GUEST", "content": "Hi, I'm Gary Bobson?"},
#     #     {"role": "HOST", "content": "What year is it?"},
#     #     {"role": "GUEST", "content": "We will ask the questions!"}
#     # ],
#     dialog = script,
#     verbose = verbose,
#     guest_desc=dialogg.guest_description
# ).result()

# From the project root
# uvicorn backend.api:app --reload --port 8000
# From /frontend/
# npm run dev