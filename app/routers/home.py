from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.repositories.document_repo import DocumentRepository

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def home(request: Request):
    repo = DocumentRepository()
    featured = repo.get_featured()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "featured": featured
        }
    )