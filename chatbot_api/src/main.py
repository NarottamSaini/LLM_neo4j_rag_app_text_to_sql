from fastapi import FastAPI
from agents.hospital_rag_agent import hospital_rag_agent_executor
from models.hospital_rag_query import HospitalQueryInput, HospitalQueryOutput
from utils.async_utils import async_retry


app = FastAPI(
    title="RAG Based Hospital Chatbot",
    description="FASTAPI based Endpoints for a hospital graph RAG based chatbot for hospital queries",
)

@async_retry(max_retries =10, delay = 1)
async def invoke_agent_with_retry(input: str):

    """
    Retry teh agent if a toll fails to execute
    
    This can help when there are intermittent connection issues to external APIs
    """

    return await hospital_rag_agent_executor.ainvoke({"input": input})

@app.get("/")
async def get_status():
    return {"status": "running"}

@app.post("/hospital-rag-agent")
async def query_hospital_agent(query:HospitalQueryInput) -> HospitalQueryOutput:
    response = await invoke_agent_with_retry(query.text)
    response["intermediate_steps"] = [str(s) for s in response["intermediate_steps"]]
    
    return response

