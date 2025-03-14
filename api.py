import asyncio
import sys
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from agents import Runner, trace
from src.agent_center import dispatcher_agent

app = FastAPI(title="AI Agent API", description="API for interacting with AI agents")

class QuestionRequest(BaseModel):
    question: str
    workflow_name: str
    group_id: str

@app.post("/callback")
async def ask_question(request: QuestionRequest):
    """處理用戶問題"""
    try:
        with trace(workflow_name=request.workflow_name, group_id=request.group_id):
            result = await Runner.run(dispatcher_agent, request.question)
            return {"answer": result.final_output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)