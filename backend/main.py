from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SubmitRequest(BaseModel):
    prompt: str
    code: str = ""
    language: str = ""

@app.post("/submit")
async def submit(request: SubmitRequest):
    return {"response": "This is a test response."}