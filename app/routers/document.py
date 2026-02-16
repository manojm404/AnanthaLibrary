from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.repositories.document_repo import DocumentRepository

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/document/{slug}")
def document_detail(request: Request, slug: str):
    repo = DocumentRepository()
    doc = repo.get_by_slug(slug)

    if not doc:
        return templates.TemplateResponse(
            "document.html",
            {"request": request, "content": "Document not found", "slug": slug}
        )

    return templates.TemplateResponse(
        "document.html",
        {"request": request, "content": doc.content, "slug": slug}
    )