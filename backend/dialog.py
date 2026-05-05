from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import operator
from dotenv import load_dotenv



class PodcastState(TypedDict):
    # 'operator.add' appends new messages rather than overwriting
    messages: Annotated[List[dict], operator.add]
    count: int


class Dialog:
    def __init__(
        self, 
        subject = "the rise of AI in day-to-day life",
        podcast = "Prosper Podcast, a chill podcast for young people in Europe about interesting topics in the world today",
        vibe = "chill",
        interests = ['arts', 'cinema', 'DEI', 'dogs', 'food', 'sports', 'travel'],
        debug = True,
        turns = 5,
        verbose = False,
    ):
        self.subject = subject
        self.podcast = podcast
        self.vibe = vibe
        self.interests = interests
        self.debug = debug
        self.turns = turns
        self.verbose = verbose
        load_dotenv(dotenv_path="backend/env/openai.env")
        self.llm = ChatOpenAI(model="gpt-4o")
        if debug:
            self.llm = None
                
    def result(self):
        self.guest_description = self.guest_desc()
        self.host_description = f"You are the host of {self.podcast}. Your name is Jane Johnson, you are 34 and love dogs. You are Brazilian but lived in Europe your whole life. You know about {self.subject} but not much more than the average person, and you have only met today's guest once, but he is an expert on the topic. "
        self.workflow = StateGraph(PodcastState)
        self.workflow.add_node("host", self.host_node)
        self.workflow.add_node("guest", self.guest_node)
        self.workflow.add_edge(START, "host")
        self.workflow.add_conditional_edges("host", self.should_continue, {"guest": "guest", END: END})
        self.workflow.add_edge("guest", "host")
        self.app = self.workflow.compile() 
        # TODO: fix extra role mentions in last messages like "HOST: HOST: ..." especially in the last few
        # TODO: fix host yapping about pets
        self.final_state = self.app.invoke({"messages": [], "count": 0})
        if not self.debug:
            self.save_local(self.final_state['messages'])
        return self.final_state['messages']
    
    def save_local(self, script):
        file_path = "backend/dialog/dialog.txt"
        with open(file_path, "w") as f:
            for line in script:
                f.write(f"{line['role']}: {line['content']}\n")
        print(f"Dialog saved to: {file_path}")

    def guest_desc(self): # Guest has to be a male because using male voice
        prompt = f'Create a realistic male character knowledgeable about {self.subject}. They can be an influencer, celebrity, or expert (must be fictional, and cannot be a financial, medical or legal advisor). Give them a distinct interesting personality you think would fit a {self.vibe} vibe. In their personal life they love {self.interests[0]}. Introduce them to an actor playing them in a podcast. For example: "You are Alex Roberts, a 55 year old mathematician with expertise in AI, specifically kernel clustering, who loves sports. Originally from the USA, you now live in Europe with your wife and two kids, your favorite food is hot dogs." Use that approximate format, around 3 sentences. Dont talk to the actor or about the actor, you are describing a character.'
        if not self.debug:
            result = self.llm.invoke(prompt).content
        else:
            result = 'You are Milo Varga, a 34-year-old AI culture researcher and digital creator known for breaking down how artificial intelligence quietly shapes everyday life—from recommendation algorithms to creative tools. Originally from Hungary, you now live in Berlin with your partner and your overly dramatic rescue dog, and you spend your free time deep in the arts scene, especially experimental cinema and street exhibitions. You’ve got a laid-back, thoughtful vibe, a soft spot for late-night food runs, and a knack for making complex tech feel human and relatable. '
        return result

    def host_prompt(self, count=0, messages=''):
        prompt = self.host_description + "Here is a description of your guest (ignore the 2nd person): '" + self.guest_description
        if count == 0:
            prompt += f"' Start the conversation by introducing yourself. "
        else:
            prompt += "' Continue the conversation, don't be too AI-sounding (don't exaggerate how good or interesting things are). "
        prompt += f"Just talk to the guest and let parts of your life and personality come through. You are not describing the scene or saying 'GUEST' or 'ROLE'. You just talk, one half sentence or many full ones, with no formatting and no line breaks. "
        lines_left = self.turns - count + 1
        if (lines_left) == 1:
            prompt += f"You are on your last line in this podcast. Say goodbye to the guest and thank them. "
        elif (lines_left) < 5:
            prompt += f"Note that you have {lines_left} voice lines left in the podcast. We are nearing the end, so your dialogue should inch towards concluding. "
        else:
            prompt += f"Note that you have {lines_left} voice lines left in the podcast, and we want to avoid an abrupt end. "
        if count > 0 and self.debug == False:
            prompt += "Previous conversation: " + messages
        return prompt


    def guest_prompt(self, messages='', count=0):
        prompt = self.guest_description + "Here is a description of your the host of the podcast you are in (ignore the 2nd person): '" + self.host_description
        prompt += "' Continue the conversation. Keep it chill and informal don't repeat yourself or describe yourself or the host, don't be too AI-sounding (don't exaggerate how good or interesting things are), just talk to the host and let parts of your life and personality come through. You are not describing the scene or saying 'GUEST' or 'ROLE'. You just talk, one half sentence or many full ones, with no formatting and no line breaks. " 
        lines_left = self.turns - count
        if lines_left == 1:
            prompt += f"You are on your last line in this podcast. Say goodbye to the host and thank them. "
        elif lines_left < 5:
            prompt += f"Note that you have {lines_left} voice lines left in the podcast. We are nearing the end, so your dialogue should inch towards concluding. "
        else:
            prompt += f"Note that you have {lines_left} voice lines left in the podcast, and we want to avoid an abrupt end. "
        prompt += "Previous conversation: "
        if not self.debug:
            prompt += messages
        return prompt

    def host_node(self, state: PodcastState):
        messages = "\n".join([f"{message['role']}: {message['content']}" for message in state['messages']])
        prompt = self.host_prompt(state["count"], messages)
        response = prompt
        if self.debug == False:
            response = self.llm.invoke(prompt).content
        if self.verbose:
            print(prompt)
        return {"messages": [{"role": "HOST", "content": response}], "count": state["count"]}

    def guest_node(self, state: PodcastState):
        response = 'default guest prompt'
        messages = "\n".join([f"{message['role']}: {message['content']}" for message in state['messages']])
        prompt = self.guest_prompt(messages, state["count"])
        response = prompt
        if self.debug == False:
            response = self.llm.invoke(prompt).content
        if self.verbose:
            print(prompt)
        return {"messages": [{"role": "GUEST", "content": response}], "count":state["count"]+1}

    def should_continue(self, state: PodcastState):
        return "guest" if state["count"] < self.turns else END