from langgraph.graph.message import add_messages

from typing import Annotated
from typing_extensions import TypedDict

class CombinedAgentState(TypedDict):
    user_query: str
    user_name: str
    database_query: bool = False
    clinical_query: bool = False
    report: dict
    folllow_up_question: str
    receptionist_messages: Annotated[list, add_messages]
    clinical_messages: Annotated[list, add_messages]
    follow_up_messages: Annotated[list, add_messages]


class ReceptionistAgentSchema(TypedDict):
    nephrology_rag_query: bool = False
    web_search_query: bool = False


class ReceptionistAgentSchema(TypedDict):
    user_name: str
    database_query: bool = False
    clinical_query: bool = False


class DatabaseQueryResponse(TypedDict):
    folllow_up_question: str
    take_user_input: bool
    clinical_agent: bool
