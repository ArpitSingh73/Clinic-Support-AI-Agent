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
        print("Receptionist: Hey, how may I help you today? ")
        return {"receptionist_messages": system_prompt}
    except Exception as e:
        print("Exception occured while setting prompt -", e)

def take_user_input(state: CombinedAgentState) -> CombinedAgentState:
    """Node to take input from user"""
    try:
        user_input = input(
            f"User:  "
        )
        return {"user_query": user_input, "receptionist_messages": HumanMessage(content=user_input)}
    except Exception as e:
        print("Error occured while taking user input - > ", e)


def route_database_call_or_clical_agent(state: CombinedAgentState):
    """Routing Node to check which tool to use"""
    if state.get("database_query") and state.get("user_name") != "":
        return "database_query"
    elif state.get("clinical_query"):
        return "clinical_agent"
    else:
        return "take_user_input"


def process_reception_query(state: CombinedAgentState) -> CombinedAgentState:
    try:
        print("----- in process reception query")
        llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")

        llm = llm.with_structured_output(schema=ReceptionistAgentSchema)
        messages = list(state.get("receptionist_messages", []))
        messages.append(HumanMessage(content=state.get("user_query", "")))
        response = llm.invoke(messages)

        if response.get("user_name") and response.get("database_query"):
            return {"user_name": response.get("user_name"), "database_query": True}
        elif response.get("clinical_query"):
            return {"clinical_query": True}
        else:
            return {"user_query": state["user_query"]}

    except Exception as e:
        print("error occured while extracting processing reception query.", e)


def databse_query(state: CombinedAgentState) -> CombinedAgentState:
    """Node to make database query"""
    try:
        print("------ in database query")
        if state.get("report"):
            return {"report": state["report"]}

        response = get_patient_by_name(state["user_name"])
        if response == None:
            print(f"Sorry, I couldn't find any discharge report for the name {state['user_name']}. Please check if the name is correct.")
            return {"report": None}
        
        return {"report": response}

    except Exception as e:
        print("Error occured while making database query - > ", e)


def handle_follow_up_question(state: CombinedAgentState) -> CombinedAgentState:
    """Node to handle follow up questions from user"""
    try:
        print("------- in handle follow up question")
        llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")
        llm = llm.with_structured_output(schema=DatabaseQueryResponse)

        system_prompt = """You are a helpful medical receptionist agent.Ask follow-up question based on the discharge information. User will provide you the deischarge report / information. For any irrelevant queries we will redirect to take user input node. And for clinical queries we will redirect to clinical agent.   
        
        ##Case 1: If you can find followup question in previous chat then then try to answer that quetion or if feels redirect to clinic agent.
        ##Case 2: If user is asking any irrelevant question then redirect to take user input node.
        ##Case 3: If user is asking any clinical question then redirect to clinical agent.
        ##case 4: If no report is provided then ask user to provide report first or advice him to check is passed name is correct.
          """

        receptionist_message = list(state.get("receptionist_messages", [])) 
        receptionist_message = receptionist_message[1:]
        receptionist_message.append(
            HumanMessage(content=f"here is my report for {state["user_name"]}: " + str(state["report"]))
        )
        receptionist_message.insert(0, SystemMessage(content=system_prompt)) 

        response = llm.invoke(receptionist_message)
        print(response)

        if response.get("follow_up_question"):
            print("Receptionist - ", response.get("follow_up_question"))
            return {
                "follow_up_question": response.get("follow_up_question"),
                "receptionist_messages": AIMessage(
                    content=response.get("follow_up_question")
                ),
            }
        elif response.get("clinical_agent"):
            print("condition met for clinical agent routing")
            return {"clinical_query": True}
        else:
            return {"user_query": state["user_query"]}

    except Exception as e:
        print("Error occured while taking follow up questions - > ", e)


def route_followups_or_take_input_or_clinical_agent(state: CombinedAgentState):
    """Routing Node to check which tool to use after database query"""
    if state.get("follow_up_question"):
        return "handle_follow_up_question"
    elif state.get("clinical_query"):
        return "set_system_prompt_clinic"
    else:
        return "take_user_input"
