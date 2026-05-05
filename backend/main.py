import os
import random


from audio import Audio
from dialog import Dialog
from researcher import Researcher



max_turns = 5 # total voice lines should be 2 * max_turns + 1 since the host starts and concludes

debug = False
debug = True

verbose = True

# subject = "the rise of AI in day-to-day life"
# interests = ['arts', 'cinema', 'DEI', 'dogs', 'food', 'sports', 'travel']
interests = ['saturnian mysticism']
podcast = "Prosper Podcast, a chill podcast for young people in Europe about interesting topics in the world today",


# TODO: fix spaghetti code, other todos

# TODO: make solution.md and README.md populated

subjects = Researcher(
    interests=interests,
    debug = debug,
    podcast=podcast,
    verbose = verbose
).subjects()


subject = subjects[0]


dialogg = Dialog(
    subject = subject,
    podcast = podcast,
    vibe = "chill",
    interests = interests,
    debug = debug,
    max_turns = max_turns,
    verbose = verbose,
).result()

audioo = Audio(
    subject=subject,
    debug=debug, 
    dialog=dialogg,
    verbose = verbose
).result()

# From the project root
# uvicorn backend.api:app --reload --port 8000