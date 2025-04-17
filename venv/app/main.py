from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import pipeline_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline_routes.router)

@app.get("/")
def home():
    return {"message": "🚀 FastAPI Deployment Successful!"}
