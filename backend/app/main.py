from fastapi import FastAPI
from app.controllers.interaction_controller import router as interaction_router

app = FastAPI(
    title="CodeGPT Assistant API",
    description="API for a VSCode extension that provides AI-driven coding assistance, integrated with LangChain and OpenAI.",
    version="0.0.1",
)

# Register API routes
app.include_router(interaction_router)
