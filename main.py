import os
import random


from audio import Audio
from dialog import Dialog



max_turns = 5 # total voice lines should be ~ 2 * max_turns + 1 since the host starts and concludes

debug = False
# debug = True

verbose = True
verbose = False

subject = "the rise of AI in day-to-day life",


# TODO: add user with interests 

# TODO: make frontend in react for localhost or smth

# TODO: fix spaghetti code, other todos

# TODO: make solution.md and README.md populated


dialogg = Dialog(
    subject = subject,
    podcast = "Prosper Podcast, a chill podcast for young people in Europe about interesting topics in the world today",
    vibe = "chill",
    interests = ['arts', 'cinema', 'DEI', 'dogs', 'food', 'sports', 'travel'],
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