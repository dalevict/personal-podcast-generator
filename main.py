import os
import random
from pathlib import Path
import operator


import audio
import dialog


from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

class PodcastState(TypedDict):
    # 'operator.add' appends new messages rather than overwriting
    messages: Annotated[List[dict], operator.add]
    count: int



def guest_desc():
    prompt = f'Create a realistic character knowledgeable about {subject}. They can be an influencer, celebrity, or expert (must be fictional, and cannot be a financial, medical or legal advisor). Give them a distinct interesting personality you think would fit a {vibe} vibe. In their personal life they love {interests[0]}. Introduce them to an actor playing them in a podcast. For example: "You are Alex Roberts, a 55 year old mathematician with expertise in AI, specifically kernel clustering, who loves sports. Originally from the USA, you now live in Europe with your wife and two kids, your favorite food is hot dogs." Use that approximate format, around 3 sentences. Dont talk to the actor or about the actor, you are describing a character.'
    # result = llm.invoke(prompt).content
    result = 'You are Milo Varga, a 34-year-old AI culture researcher and digital creator known for breaking down how artificial intelligence quietly shapes everyday life—from recommendation algorithms to creative tools. Originally from Hungary, you now live in Berlin with your partner and your overly dramatic rescue dog, and you spend your free time deep in the arts scene, especially experimental cinema and street exhibitions. You’ve got a laid-back, thoughtful vibe, a soft spot for late-night food runs, and a knack for making complex tech feel human and relatable. '
    return result

def host_prompt(count=0, messages=''):
    prompt = host_description + "Here is a description of your guest (ignore the 2nd person): '" + guest_description
    if count == 0:
        prompt += f"' Start the conversation by introducing yourself. "
    else:
        prompt += "' Continue the conversation, don't be too AI-sounding (don't exaggerate how good or interesting things are). "
    prompt += f"Just talk to the guest and let parts of your life and personality come through. You are not describing the scene or saying 'GUEST' or 'ROLE'. You just talk, one half sentence or many full ones, with no formatting and no line breaks. "
    lines_left = max_turns - count + 1
    if (lines_left) == 1:
        prompt += f"You are on your last line in this podcast. Say goodbye to the guest and thank them. "
    elif (lines_left) < 5:
        prompt += f"Note that you have {lines_left} voice lines left in the podcast. We are nearing the end, so your dialogue should inch towards concluding. "
    else:
        prompt += f"Note that you have {lines_left} voice lines left in the podcast, and we want to avoid an abrupt end. "
    if count > 0 and debug == False:
        prompt += "Previous conversation: " + messages
    return prompt


def guest_prompt(messages='', count=0):
    prompt = guest_description + "Here is a description of your the host of the podcast you are in (ignore the 2nd person): '" + host_description
    prompt += "' Continue the conversation. Keep it chill and informal don't repeat yourself or describe yourself or the host, don't be too AI-sounding (don't exaggerate how good or interesting things are), just talk to the host and let parts of your life and personality come through. You are not describing the scene or saying 'GUEST' or 'ROLE'. You just talk, one half sentence or many full ones, with no formatting and no line breaks. " 
    lines_left = max_turns - count
    if lines_left == 1:
        prompt += f"You are on your last line in this podcast. Say goodbye to the host and thank them. "
    elif lines_left < 5:
        prompt += f"Note that you have {lines_left} voice lines left in the podcast. We are nearing the end, so your dialogue should inch towards concluding. "
    else:
        prompt += f"Note that you have {lines_left} voice lines left in the podcast, and we want to avoid an abrupt end. "
    prompt += "Previous conversation: "
    if not debug:
        prompt += messages
    return prompt

def host_node(state: PodcastState):
    messages = "\n".join([f"{message['role']}: {message['content']}" for message in state['messages']])
    prompt = host_prompt(state["count"], messages)
    response = prompt
    if debug == False:
        response = llm.invoke(prompt).content
    if verbose:
        print(prompt)
    return {"messages": [{"role": "HOST", "content": response}], "count": state["count"]}

def guest_node(state: PodcastState):
    response = 'default guest prompt'
    messages = "\n".join([f"{message['role']}: {message['content']}" for message in state['messages']])
    prompt = guest_prompt(messages, state["count"])
    response = prompt
    if debug == False:
        response = llm.invoke(prompt).content
    if verbose:
        print(prompt)
    return {"messages": [{"role": "GUEST", "content": response}], "count":state["count"]+1}

def should_continue(state: PodcastState):
    return "guest" if state["count"] < max_turns else END

def save_local(audio, filename="daily_podcast.mp3"):
    output_dir = Path("./podcasts")
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / filename
    audio.export(file_path, format="mp3")
    print(f"Podcast saved to: {file_path}")


max_turns = 5 # total voice lines should be ~ 2 * max_turns + 1 since the host starts and concludes

debug = False
debug = True
verbose = False
# verbose = True

subject = "the rise of AI in day-to-day life"
podcast = "Prosper Podcast, a chill podcast for young people in Europe about interesting topics in the world today"
vibe = "chill"
interests = ['arts', 'cinema', 'DEI', 'dogs', 'food', 'sports', 'travel']

if not debug:
    llm = ChatOpenAI(model="gpt-4o")

guest_description = guest_desc()
host_description = f"You are the host of {podcast}. Your name is Jane Johnson, you are 34 and love dogs. You are Brazilian but lived in Europe your whole life. You know about {subject} but not much more than the average person, and you have only met today's guest once, but he is an expert on the topic. "

workflow = StateGraph(PodcastState)
workflow.add_node("host", host_node)
workflow.add_node("guest", guest_node)

workflow.add_edge(START, "host")
workflow.add_conditional_edges("host", should_continue, {"guest": "guest", END: END})
workflow.add_edge("guest", "host")

app = workflow.compile()
final_state = app.invoke({"messages": [], "count": 0})

# TODO: add user with interests 

# TODO: make frontend in react for localhost or smth

# TODO: fix spaghetti code

# TODO: make solution.md and README.md populated

dialogg = final_state['messages']
audioo = audio.generate_podcast_audio(dialogg)
# save_local(audioo)  