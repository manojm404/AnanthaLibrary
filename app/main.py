from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import home

app = FastAPI(title="AnanthaLibrary")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(home.router)