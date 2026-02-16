from app.database import SessionLocal
from app.models.document import Document
import uuid

class DocumentRepository:

    def get_all(self):
        db = SessionLocal()
        docs = db.query(Document).all()
        db.close()
        return docs

    def create(self, title, slug, language, category, content):
        db = SessionLocal()

        doc = Document(
            id=str(uuid.uuid4()),
            title=title,
            slug=slug,
            language=language,
            category=category,
            content=content
        )

        db.add(doc)
        db.commit()
        db.close()

    def get_by_slug(self, slug: str):
        db = SessionLocal()
        doc = db.query(Document).filter(Document.slug == slug).first()
        db.close()
        return doc

    def search(self, query=None, language=None, category=None, page=1, page_size=6):
        db = SessionLocal()
        q = db.query(Document)

        if query:
            q = q.filter(Document.title.ilike(f"%{query}%"))

        if language:
            q = q.filter(Document.language == language)

        if category:
            q = q.filter(Document.category == category)

        total = q.count()

        results = (
            q.offset((page - 1) * page_size)
             .limit(page_size)
             .all()
        )

        db.close()

        return results, total

    def create_sample_data(self):
        db = SessionLocal()

        if db.query(Document).count() == 0:
            samples = [
                ("Vishnu Sahasranamam", "vishnu-sahasranamam", "Sanskrit", "Stotra", "Om Shuklam Bharadaram Vishnum..."),
                ("Bhagavad Gita", "bhagavad-gita", "Sanskrit", "Scripture", "Dharmakshetre Kurukshetre..."),
                ("Shiva Tandava Stotram", "shiva-tandava", "Sanskrit", "Stotra", "Jatatavigalajjala...")
            ]

            for title, slug, lang, cat, content in samples:
                doc = Document(
                    id=str(uuid.uuid4()),
                    title=title,
                    slug=slug,
                    language=lang,
                    category=cat,
                    content=content
                )
                db.add(doc)

            db.commit()

        db.close()

    def get_featured(self, limit=3):
        db = SessionLocal()
        docs = db.query(Document).limit(limit).all()
        db.close()
        return docs