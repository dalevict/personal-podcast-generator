from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import operator
from dotenv import load_dotenv
import re

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field


class PodcastResponse(BaseModel):
    content: str = Field(
        ..., 
        description="ONE continuous paragraph of natural spoken dialogue. You may include tone markers like [sighs], [giggles], [pause], [whispers]. NO newlines, NO role labels."
    )


class PodcastState(TypedDict):
    messages: Annotated[List[dict], operator.add]
    count: int


class Dialog:
    def __init__(
        self, 
        subject="",
        podcast="Chilling Podcast, a chill podcast for young people in Europe about interesting topics in the world today",
        vibe="chill",
        interests=None,
        debug=True,
        turns=10,
        verbose=False,
        context=''
    ):
        self.subject = subject
        self.podcast = podcast
        self.warning_turns = 3
        self.vibe = vibe
        self.interests = interests or []
        self.debug = debug
        self.turns = min(turns, 12)
        self.verbose = verbose
        self.context = context
        self.guest_description = ""
        load_dotenv(dotenv_path="backend/env/openai.env")
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.65)
        self.structured_llm = self.llm.with_structured_output(PodcastResponse)
        if debug:
            self.llm = None
            self.structured_llm = None

    def clean_content(self, text: str) -> str:
        """Remove line breaks and extra whitespace"""
        if not text:
            return ""
        text = text.replace("\n", " ").replace("\r", " ")
        text = " ".join(text.split())
        return text.strip()

    def guest_desc(self):
        prompt = f"""Create a realistic fictional character knowledgeable about {self.subject}.They should be interesting and fit a chill podcast vibe. Format: "You are [Full Name], a [age] year old [profession]..." (3-4 sentences)."""
        if not self.debug:
            result = self.llm.invoke(prompt).content
        else:
            result = 'You are Maya Levi, a 32-year-old cultural influencer and mural artist from Tel Aviv who loves visual arts and sparking meaningful conversations.'
        return result
    def base_system_prompt(self):
        return f"""You are Tina Johnson, host of {self.podcast}, from South Africa and living in Europe. You are warm, curious, and conversational. You know about {self.subject} but not much more than the average person. """

    def host_prompt(self, count: int, history: str):
        prompt = self.base_system_prompt() + "\n\n"
        prompt += f"Guest: {self.guest_description}\n\n"
        if count == 0:
            prompt += "This is the opening message. Warmly introduce yourself and the guest."
        else:
            prompt += "Continue the conversation naturally."

        if self.context:
            prompt += f"\n\nRecent context you can reference: {self.context}"
        lines_left = self.turns - count
        if lines_left == 1:
            prompt += f"\n\nThis is your last turn. Wrap up the conversation."
        elif lines_left <= self.warning_turns:
            prompt += f"\n\nYou have {lines_left} turns left. Start wrapping up the conversation gently."
        if history:
            prompt += f"\n\nPrevious conversation:\n{history}"
        prompt += """\n\nRespond with ONLY natural spoken words in ONE continuous paragraph. You may use tone indicators like [sighs], [giggles], [pause], [whispers], [sadly], [sarcastically] when appropriate. Never use line breaks. Never output any labels like HOST:, GUEST:, TINA:, MAYA: etc."""
        return prompt

    def guest_prompt(self, count: int, history: str):
        prompt = f"Guest description: {self.guest_description}\n\n"
        prompt += f"Host description: {self.base_system_prompt()}\n\n"
        prompt += "Continue the conversation in character, keep it chill and natural.\n\n"
        if self.context:
            prompt += f"Recent context: {self.context}\n\n"
        lines_left = self.turns - count
        if lines_left <= self.warning_turns:
            prompt += f"You have {lines_left} turns left. Wrap up naturally.\n\n"
        if history:
            prompt += f"Previous conversation:\n{history}\n\n"
        prompt += """\n\nRespond with ONLY natural spoken words in ONE continuous paragraph. You may use tone indicators like [sighs], [giggles], [pause], [whispers], [sadly], [sarcastically] when appropriate. Never use line breaks. Never output any labels like HOST:, GUEST:, TINA:, MAYA: etc."""
        return prompt

    def host_node(self, state: PodcastState):
        history = "\n".join([f"{m['role']}: {m['content']}" for m in state['messages']])
        prompt = self.host_prompt(state["count"], history)
        if self.debug:
            content = f"Hi everyone, welcome to the podcast! Today we're talking about {self.subject} with our guest."
        else:
            response = self.structured_llm.invoke(prompt)
            content = self.clean_content(response.content)
        content = re.sub(r'^(HOST|GUEST|TINA|GUEST\sNAME):\s*', '', content, flags=re.IGNORECASE)
        return {
            "messages": [{"role": "HOST", "content": content}],
            "count": state["count"]
        }

    def guest_node(self, state: PodcastState):
        history = "\n".join([f"{m['role']}: {m['content']}" for m in state['messages']])
        prompt = self.guest_prompt(state["count"], history)
        if self.debug:
            content = f"Interesting point! As the guest, here's my thoughts on the topic."
        else:
            response = self.structured_llm.invoke(prompt)
            content = self.clean_content(response.content)
        content = re.sub(r'^(HOST|GUEST|TINA|GUEST\sNAME):\s*', '', content, flags=re.IGNORECASE)
        return {
            "messages": [{"role": "GUEST", "content": content}],
            "count": state["count"] + 1
        }

    def result(self):
        self.guest_description = self.guest_desc()
        self.workflow = StateGraph(PodcastState)
        self.workflow.add_node("host", self.host_node)
        self.workflow.add_node("guest", self.guest_node)
        self.workflow.add_edge(START, "host")
        self.workflow.add_conditional_edges(
            "host",
            lambda s: "guest" if s["count"] < self.turns else END
        )
        self.workflow.add_edge("guest", "host")
        self.app = self.workflow.compile()
        final_state = self.app.invoke({"messages": [], "count": 0})
        if not self.debug:
            self.save_local(final_state['messages'])
        return final_state['messages']

    def save_local(self, script):
        file_path = "backend/dialog/dialog.txt"
        with open(file_path, "w") as f:
            for line in script:
                f.write(f"{line['role']}: {line['content']}\n")