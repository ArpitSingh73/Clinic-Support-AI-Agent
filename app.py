from fastapi import FastAPI
from agent_app import combined_agent
from langgraph.types import Command

app = FastAPI()


@app.post("/start")
def start_session(session_id: str = "111"):
    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }

    result = combined_agent.invoke({"input": "data"}, config=config)
    result = "Hi, there please let me know how can I help you?\n Share you full name to begin with."
    print(result)
    return {"status": "started", "result": result}


@app.post("/answer")
def resume_session(user_input: str, session_id: str = "111"):
    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }
    cmd = Command(resume=user_input)
    result = combined_agent.invoke(cmd, config=config)
    return {"status": "resumed", "result": result}
