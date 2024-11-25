from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["codegpt"]
collection = db["interactions"]

class SubmitRequest(BaseModel):
    prompt: str
    code: str = ""
    language: str = ""

class Interaction(BaseModel):
    prompt: str
    response: str

@app.post("/submit")
async def submit(request: SubmitRequest):
    # Itt történik az AI válaszának generálása
    response_text = "Ez egy példa válasz"
    
    # Mentés az adatbázisba
    interaction = {
        "prompt": request.prompt,
        "response": response_text,
        # "user_id": request.user_id  # Ha van felhasználói azonosító
    }
    collection.insert_one(interaction)
    
    return {"response": response_text}

@app.get("/history", response_model=List[Interaction])
async def get_history(user_id: str = None):
    query = {}
    if user_id:
        query["user_id"] = user_id
    interactions = list(collection.find(query, {"_id": 0}))
    return interactions