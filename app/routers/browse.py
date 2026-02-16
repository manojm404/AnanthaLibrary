from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.repositories.document_repo import DocumentRepository
import math

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/browse")
def browse(
    request: Request,
    q: str = None,
    language: str = None,
    category: str = None,
    page: int = 1
):
    page_size = 6

    repo = DocumentRepository()
    docs, total = repo.search(
        query=q,
        language=language,
        category=category,
        page=page,
        page_size=page_size
    )

    total_pages = math.ceil(total / page_size) if total else 1

    return templates.TemplateResponse(
        "browse.html",
        {
            "request": request,
            "docs": docs,
            "q": q,
            "language": language,
            "category": category,
            "page": page,
            "total": total,
            "total_pages": total_pages
        }
    )