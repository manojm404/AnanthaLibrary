import os
import re
from app.database import Base, engine
from app.repositories.document_repo import DocumentRepository

BOOKS_DIR = "books"


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def format_title(filename):
    name = filename.replace(".txt", "")
    name = name.replace("_", " ")
    return name.title()


def clean_text(text):
    text = text.strip()
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def import_books():
    Base.metadata.create_all(bind=engine)

    repo = DocumentRepository()

    for language in os.listdir(BOOKS_DIR):
        language_path = os.path.join(BOOKS_DIR, language)

        if not os.path.isdir(language_path):
            continue

        for filename in os.listdir(language_path):
            if not filename.endswith(".txt"):
                continue

            filepath = os.path.join(language_path, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                content = clean_text(f.read())

            title = format_title(filename)
            slug = slugify(f"{language}-{title}")

            if repo.get_by_slug(slug):
                print("Already exists:", slug)
                continue

            repo.create(
                title=title,
                slug=slug,
                language=language,
                category="Stotra",
                content=content
            )

            print("Imported:", title)


if __name__ == "__main__":
    import_books()