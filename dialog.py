import operator
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI



class PodcastState(TypedDict):
    # 'operator.add' appends new messages rather than overwriting
    messages: Annotated[List[dict], operator.add]
    count: int  # To track turns and stop the podcast

max_turns = 2

# TODO: add lists of interests

llm = ChatOpenAI(model="gpt-4o")

def host_node(state: PodcastState):
    prompt = f"You are the podcast host. Keep it natural. Context: {state['messages']}"
    response = llm.invoke(prompt)
    return {"messages": [{"role": "Host", "content": response.content}], "count": state["count"] + 1}

def guest_node(state: PodcastState):
    prompt = f"You are the expert guest. React to the host. Context: {state['messages']}"
    response = llm.invoke(prompt)
    return {"messages": [{"role": "Guest", "content": response.content}]}

def should_continue(state: PodcastState):
    return "guest" if state["count"] < max_turns else END # TODO: fix abrupt end to conversation





workflow = StateGraph(PodcastState)
workflow.add_node("host", host_node)
workflow.add_node("guest", guest_node)

workflow.add_edge(START, "host")
workflow.add_conditional_edges("host", should_continue, {"guest": "guest", END: END})
workflow.add_edge("guest", "host")

app = workflow.compile()
final_state = app.invoke({"messages": [], "count": 0})