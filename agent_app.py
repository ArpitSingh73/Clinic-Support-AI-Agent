from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from typing import Annotated
from typing_extensions import TypedDict
import dotenv, os, getpass

from graph_state import *
from Agents.receptionist_agent import set_system_prompt_receptionist, take_user_input, process_reception_query, route_database_call_or_clical_agent, databse_query, handle_follow_up_question, route_followups_or_take_input_or_clinical_agent

from Agents.clinical_agent import set_system_prompt_clinic, take_user_input_clinic, web_search_tool, nephrology_rag_tool, process_clinic_query, route_rag_or_web_search

dotenv.load_dotenv(".env")
KEY = os.environ.get("GOOGLE_API_KEY")
if not KEY:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Your API Key here :")


combined_graph_compiler = StateGraph(CombinedAgentState)

combined_graph_compiler.add_node(
    "set_system_prompt_receptionist", set_system_prompt_receptionist
)
combined_graph_compiler.add_node("take_user_input", take_user_input)
combined_graph_compiler.add_node("process_reception_query", process_reception_query)
combined_graph_compiler.add_node("database_query", databse_query)
combined_graph_compiler.add_node("handle_follow_up_question", handle_follow_up_question)


combined_graph_compiler.add_node("set_system_prompt_clinic", set_system_prompt_clinic)

combined_graph_compiler.add_node("take_user_input_clinic", take_user_input_clinic)
combined_graph_compiler.add_node("web_search_tool", web_search_tool)
combined_graph_compiler.add_node("nephrology_rag_tool", nephrology_rag_tool)
combined_graph_compiler.add_node("process_clinic_query", process_clinic_query)


combined_graph_compiler.add_edge(START, "set_system_prompt_receptionist")
combined_graph_compiler.add_edge(
    "set_system_prompt_receptionist", "take_user_input"
)
combined_graph_compiler.add_edge("take_user_input", "process_reception_query")

combined_graph_compiler.add_conditional_edges(
    "process_reception_query",
    route_database_call_or_clical_agent,
    {
        "database_query": "database_query",
        "set_system_prompt_clinic": "set_system_prompt_clinic",
        "take_user_input": "take_user_input",
    },
)

combined_graph_compiler.add_edge("database_query", "handle_follow_up_question")

combined_graph_compiler.add_conditional_edges(
    "handle_follow_up_question",
    route_followups_or_take_input_or_clinical_agent,
    {"handle_follow_up_question": "handle_follow_up_question", "set_system_prompt_clinic": "set_system_prompt_clinic", 
     "take_user_input": "take_user_input"},
)

combined_graph_compiler.add_edge("set_system_prompt_clinic", "take_user_input_clinic")
combined_graph_compiler.add_edge("take_user_input_clinic", "process_clinic_query")
combined_graph_compiler.add_conditional_edges(
    "process_clinic_query",
    route_rag_or_web_search,
    {
        "nephrology_rag_query": "nephrology_rag_tool",
        "web_search_query": "web_search_tool",
        "take_user_input_clinic": "take_user_input_clinic",
    },
)
try:
    config = {"callbacks": [], "verbose": False}
    combined_agent = combined_graph_compiler.compile()
    for result in combined_agent.invoke({}):
        print(result)
except Exception as e:
    print("Error occured while compiling combined agent - > ", e)
    combined_agent = combined_graph_compiler.compile()
    for result in combined_agent.invoke({}, debug=False):
        print(result)

try:
    png_bytes = combined_agent.get_graph().draw_mermaid_png()

    with open("combined_agent.png", "wb") as f:
        f.write(png_bytes)
except Exception:
    # This requires some extra dependencies and is optional
    pass
