from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import dotenv, os, getpass

from Prompts.receptionist_agent_prompt import receptionist_prompt
from Data.database import get_patient_by_name

from graph_state import *

dotenv.load_dotenv(".env")
KEY = os.environ.get("GOOGLE_API_KEY")
if not KEY:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Your API Key here :")

def set_system_prompt_receptionist(state: CombinedAgentState) -> CombinedAgentState:
    """Node to set a default system prompt."""
    try:
        system_prompt = [SystemMessage(content=receptionist_prompt)]
        return {"messages": system_prompt}
    except Exception as e:
        print("Exception occured while setting prompt -", e)

def take_user_input(state: CombinedAgentState) -> CombinedAgentState:
    """Node to take input from user"""
    try:
        user_input = input(
            f"Hey, {state["name"]}, how may I help you today?  "
        )
        return {"user_query": user_input or state["user_query"]}
    except Exception as e:
        print("Error occured while taking user input - > ", e)

def route_database_call_or_clical_agent(state: CombinedAgentState):
    """Roouting NOde to check which tool to use"""
    if state["database_query"] and state["user_name"] != "":
        return "db_query"
    elif state["clinical_query"]:
        return "clinical_agent"
    else:
        return "take_user_input"

def process_reception_query(state: CombinedAgentState) -> CombinedAgentState:
    try:

        llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")
        llm = llm.with_structured_output(schema=ReceptionistAgentSchema)
        message = [state["messages"][0], (HumanMessage(content=state["user_query"]))]
        response = llm.invoke(message)
        print(response)

        if response.user_name and response.database_query:
            return {"user_name": response.user_name, "database_query": True}
        elif response.clinical_query:
            return {"clinical_query": True}
        else:
            return {"user_query": state["user_query"]}
        
    except Exception as e:
        print("error occured while exctrating date and time.", e)

def databse_query(state: CombinedAgentState) -> CombinedAgentState:
    """Node to make database query"""
    try:
        response = get_patient_by_name(state["name"])
        print(f"Hey {state["name"]}, here i your report: \n", response)

    except Exception as e:
        print("Error occured while making database query - > ", e)

def handle_follow_up_question(state: CombinedAgentState) -> CombinedAgentState:
    """Node to handle follow up questions from user"""
    try:

        llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")
        llm = llm.with_structured_output(schema=DatabaseQueryResponse)

        system_promot = "You are a helpful medical receptionist agent.Ask follow-up question based on the discharge information. For any irrlevant queries we will redirect to take user input node. And for clinical queries we will redirect to clinical agent."

        message = [
            SystemMessage(content=system_promot),
            (HumanMessage(content=str(state["report"]))),
        ]

        response = llm.invoke(message)
        if response.take_user_input:
            return {"user_query": state["user_query"]}
        elif response.clinical_agent:
            return {"clinical_query": True}
        elif response.folllow_up_questions:
            return {"follow_up_question": response.folllow_up_question, "messages": AIMessage(content=response.folllow_up_question)}

    except Exception as e:
        print("Error occured while taking follow up questions - > ", e)

def route_followups_or_take_input_or_clinical_agent(state: CombinedAgentState):
    """Routing Node to check which tool to use after database query"""
    if state["follow_up_question"]:
        return "handle_follow_up_question"
    elif state["clinical_query"]:
        return "clinical_agent"
    else:
        return "take_user_input"
