from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import uvicorn
import uuid
from worker import processing_pipeline

app = FastAPI(title="SimplifIQ Lead Automation Pipeline")

# Pydantic schema guarantees strict validation at the digital front door
class LeadSchema(BaseModel):
    name: str
    email: EmailStr
    company_name: str
    company_website: str
    industry: Optional[str] = None

@app.post("/api/v1/leads")
async def receive_lead(lead: LeadSchema, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    
    background_tasks.add_task(processing_pipeline, lead, task_id)
    
    return {
        "status": "success",
        "message": "Lead received safely. Asynchronous pipeline triggered.",
        "task_id": task_id
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
