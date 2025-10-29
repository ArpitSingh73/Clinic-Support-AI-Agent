from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from typing import Annotated
from typing_extensions import TypedDict
import dotenv, os, getpass

from pydantic import BaseModel
from langchain_tavily import TavilySearch


from Prompts.receptionist_agent_prompt import receptionist_prompt

class State(TypedDict):
    user_query: str
    messages: Annotated[list, add_messages]

receptionist_graph_compiler = StateGraph(State)

dotenv.load_dotenv(".env")
KEY = os.environ.get("GOOGLE_API_KEY")
if not KEY:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Your API Key here :")

class ReceptionistAgentSchema(TypedDict):
    database_query_query: bool = False
    # web_search_query: bool = False
    clinical_query: bool = False

def set_system_prompt(state: State) -> State:
    """Node to set a default system prompt."""
    try:
        system_prompt = [SystemMessage(content=receptionist_prompt)]
        return {"messages": system_prompt}
    except Exception as e:
        print("Exception occured while setting prompt -", e)

def take_user_input(state: State) -> State:
    """Node to take input from user"""
    try:
        user_input = input(
            "hi how may i help you ?  __ "
        )
        return {"user_query": user_input}
    except Exception as e:
        print("Error occured while taking user input - > ", e)

def web_search_tool(state: State) -> State:
    """Node to perform web search using tavily tool"""
    try:
        tavily_tool = TavilySearch(
            api_key=os.environ.get("TAVILY_API_KEY"), max_results=1
        )
        ans = tavily_tool.invoke({"query": "who is cm of up, india"})["results"][0][
            "content"
        ]

        print("Web Search Result -> ", ans)

        # state["messages"].append(HumanMessage(content=state["user_query"]))
        # state["messages"].append(ai_message)

        return {"messages": state["messages"]}
    except Exception as e:
        print("Error occured while performing web search - > ", e)

def tool_or_clical_agent(state: State):
    """Roouting NOde to check if we have date and time"""
    if state["date"] and state["end_time"] and state["start_time"]:
        return "yes"
    return "no"


def select_tool(state: State) -> State:
    try:

        llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")
        llm = llm.with_structured_output(schema=ReceptionistAgentSchema)
        message = [state["messages"][0], (HumanMessage(content=state["user_query"]))]
        response = llm.invoke(message)
        print(response)

        return {"messages": response.content}
    except Exception as e:
        print("error occured while exctrating date and time.", e)

