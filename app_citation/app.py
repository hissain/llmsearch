# app.py

from fastapi import FastAPI
from routes import home, references

app = FastAPI()

# Include routes
app.include_router(home.router)
app.include_router(references.router)
