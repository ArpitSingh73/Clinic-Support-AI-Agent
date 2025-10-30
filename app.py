from fastapi import FastAPI, Form, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
# from agent_app import combined_agent
RAG_APP = FastAPI()

from RAG.vector_store import search_vector_store
from RAG.save_data_to_vectordb import upload_pdf

@RAG_APP.on_event("startup")
def startup_event():
    print("create a langchain agent ---")

@RAG_APP.post("/get-answer")
def user_query_handler(query: str = Form(...)):
    return search_vector_store(query)


@RAG_APP.post("/upload-file")
def pdf_upload_handler(background_task: BackgroundTasks, file: UploadFile = File(...)):
    try:
        background_task.add_task(upload_pdf, file)
        return JSONResponse(
            status_code=200, content={"message": "File Uploaded Successfully"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
