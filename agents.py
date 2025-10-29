from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from typing import Annotated
from typing_extensions import TypedDict
import dotenv, os, getpass

from Agents.receptionist_agent import *
from Agents.clinical_agent import *

dotenv.load_dotenv(".env")
KEY = os.environ.get("GOOGLE_API_KEY")
if not KEY:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Your API Key here :")


receptionist_graph_compiler.add_node("set_system_prompt", set_system_prompt)
receptionist_graph_compiler.add_node("take_user_input", take_user_input)
receptionist_graph_compiler.add_node("process_query", process_query)
receptionist_graph_compiler.add_node("db_query", databse_query)
receptionist_graph_compiler.add_node("handle_follow_up_question", handle_follow_up_question)
receptionist_graph_compiler.add_node("clinical_agent", clinical_agent)

receptionist_graph_compiler.add_edge(START, "set_system_prompt")
receptionist_graph_compiler.add_edge("set_system_prompt", "take_user_input")
receptionist_graph_compiler.add_edge("take_user_input", "process_query")

receptionist_graph_compiler.add_conditional_edges(
    "process_query",
    route_database_call_or_clical_agent,
    {
        "db_query": "db_query",
        "clinical_agent": "clinical_agent",
        "take_user_input": "take_user_input",
    },
)

receptionist_graph_compiler.add_edge("db_query", "handle_follow_up_question")

receptionist_graph_compiler.add_conditional_edges(
    "handle_follow_up_question",
    route_followups_or_take_input_or_clinical_agent,
    {"handle_follow_up_question": "handle_follow_up_question", "clinical_agent": "clinical_agent", 
     "take_user_input": "take_user_input"},
)

receptionist_graph_compiler.add_edge("handle_follow_up_question", END)

receptionist_agent = receptionist_graph_compiler.compile()


# for result in receptionist_agent.stream({}):
#     print(result)
try:
    png_bytes = receptionist_agent.get_graph().draw_mermaid_png()

    with open("receptionist_agent.png", "wb") as f:
        f.write(png_bytes)
except Exception:
    # This requires some extra dependencies and is optional
    pass


#  ========================== Clinical Agent =========================


# clinic_graph_compiler.add_node("set_system_prompt_clinic", set_system_prompt_clinic)
# clinic_graph_compiler.add_node("take_user_input_clinic", take_user_input_clinic)
# clinic_graph_compiler.add_node("select_tool_clinic", select_tool_clinic)

# clinic_graph_compiler.add_edge(START, "set_system_prompt_clinic")
# clinic_graph_compiler.add_edge("set_system_prompt_clinic", "take_user_input_clinic")
# clinic_graph_compiler.add_edge("take_user_input_clinic", "select_tool_clinic")
# clinic_graph_compiler.add_edge("select_tool_clinic", "take_user_input_clinic")
# clinic_graph_compiler.add_edge("select_tool_clinic", END)

# clinic_graph_compiler
# clinic_agent = clinic_graph_compiler.compile()


# for result in clinic_agent.stream({}):
#     print(result)
# try:
#     png_bytes = clinic_agent.get_graph().draw_mermaid_png()

#     with open("clinical_agent.png", "wb") as f:
#         f.write(png_bytes)
# except Exception:
#     # This requires some extra dependencies and is optional
#     pass
