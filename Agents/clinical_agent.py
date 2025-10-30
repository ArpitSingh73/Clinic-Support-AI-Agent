from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

import dotenv, os, getpass

from langchain_tavily import TavilySearch
from Prompts.clinical_agent_prompt import clinic_agent_prompt

dotenv.load_dotenv(".env")
KEY = os.environ.get("GOOGLE_API_KEY")
if not KEY:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Your API Key here :")

from graph_state import *

def set_system_prompt_clinic(state: CombinedAgentState) -> CombinedAgentState:
    """Node to set a default system prompt."""
    try:
        print("\n\nReceptionist: Transferring the chat to Clinical Agent...")
        system_prompt = [SystemMessage(content=clinic_agent_prompt)]
        return {"clinical_messages": system_prompt}
    except Exception as e:
        print("Exception occured while setting prompt -", e)

def take_user_input_clinic(state: CombinedAgentState) -> CombinedAgentState:
    """Node to take input from user"""
    try:
        user_input = input("Clinic: hi, you have been transferred to me, can you explain you issue to me so that i can help you. __ ")
        return {"user_query": user_input, "clinical_messages": HumanMessage(content=user_input)}
    except Exception as e:
        print("Error occured while taking user input - > ", e)


def process_clinic_query(state: CombinedAgentState) -> CombinedAgentState:
    try:
        print("----- in process clinic query")
        llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")
        llm = llm.with_structured_output(schema=ClinicalAgentSchema)
        clinical_messages = list(state.get("clinical_messages", []))
        clinical_messages.append(
            HumanMessage(
                content=f"here is my report for {state["user_name"]}: "
                + str(state["report"])
            )
        )
        clinical_messages.append(HumanMessage(content=state.get("user_query", "")))

        response = llm.invoke(clinical_messages)
        print(response)

        if response.nephrology_rag_tool:
            return {"nephrology_rag_tool": True}
        elif response.web_search_query:
            return {"web_search_query": True}
    except Exception as e:
        print("error occured while exctrating date and time.", e)


def web_search_tool(state: CombinedAgentState) -> CombinedAgentState:
    """Node to perform web search using tavily tool"""
    try:
        print("----- in web search tool")
        tavily_tool = TavilySearch(
            api_key=os.environ.get("TAVILY_API_KEY"), max_results=1
        )
        ans = tavily_tool.invoke({"query": "who is cm of up, india"})["results"][0][
            "content"
        ]
        print("Web Search Tool Result -> ", ans)
        return {"clinical_messages":AIMessage(content=ans)}
    except Exception as e:
        print("Error occured while performing web search - > ", e)

def nephrology_rag_tool(state: CombinedAgentState) -> CombinedAgentState:
    """Node to perform RAG over nephrology reference book"""
    try:
        print("----- in nephrology RAG tool")
        # Placeholder for RAG tool implementation
        rag_answer = "This is a placeholder answer from the nephrology RAG tool."

        print("Nephrology RAG Tool Result -> ", rag_answer)

        return {"clinical_messages": AIMessage(content=rag_answer)}
    except Exception as e:
        print("Error occured while performing nephrology RAG tool - > ", e)

def route_rag_or_web_search(state: CombinedAgentState):
    """Routing Node to check which tool to use"""
    if state.get("nephrology_rag_query"):
        return "nephrology_rag_tool"
    elif state.get("web_search_query"):
        return "web_search_tool"
    else:
        return "clinical_agent"
