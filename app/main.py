from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import home, browse, document

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AnanthaLibrary")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(home.router)
app.include_router(browse.router)
app.include_router(document.router)