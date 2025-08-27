from functools import lru_cache
from langchain_openai import ChatOpenAI
from backend.agents.tools import tools
from langgraph.prebuilt import ToolNode


@lru_cache(maxsize=4)
def _get_model():
    model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    model = model.bind_tools(tools)
    return model

def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


system_prompt = """Be a helpful assistant"""

def call_model(state, config):
    messages = state["messages"]
    messages = [{"role": "system", "content": system_prompt}] + messages
    model = _get_model()
    response = model.invoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(tools)
