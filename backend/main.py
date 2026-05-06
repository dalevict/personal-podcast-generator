import os
import random


from audio import Audio
from dialog import Dialog
from researcher import Researcher



max_turns = 1 # total voice lines should be 2 * max_turns + 1 since the host starts and concludes

debug = False
# debug = True

verbose = True

subject = "the rise of AI in day-to-day life"
interests = ['arts', 'cinema', 'DEI', 'dogs', 'food', 'sports', 'travel']
# interests = ['test']
podcast = "Prosper Podcast, a chill podcast for young people in Europe about interesting topics in the world today",


# TODO: fix spaghetti code, other todos

# TODO: make solution.md and README.md populated

# dialogg = Dialog(
#         subject = subject,
#         podcast = podcast,
#         vibe = "chill",
#         interests = interests,
#         debug = debug,
#         turns = max_turns,
#         verbose = verbose,
# ).result()

audioo = Audio(
    subject = subject,
    debug=debug, 
    dialog=[
        {"role": "HOST", "content": "Hello, nice to meet you!"},
        {"role": "GUEST", "content": "Hi, I'm Gary Bobson?"},
        {"role": "HOST", "content": "What year is it?"},
        {"role": "GUEST", "content": "We will ask the questions!"}
    ],
    # dialog = dialogg,
    verbose = verbose,
    guest_desc='You are Milo Varga, a 34-year-old AI culture researcher and digital creator known for breaking down how artificial intelligence quietly shapes everyday life—from recommendation algorithms to creative tools. Originally from Hungary, you now live in Berlin with your partner and your overly dramatic rescue dog, and you spend your free time deep in the arts scene, especially experimental cinema and street exhibitions. You’ve got a laid-back, thoughtful vibe, a soft spot for late-night food runs, and a knack for making complex tech feel human and relatable. '
).result()

# From the project root
# uvicorn backend.api:app --reload --port 8000
# From /frontend/
# npm run dev