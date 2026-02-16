from app.database import Base, engine
from app.repositories.document_repo import DocumentRepository

if __name__ == "__main__":
    # Create tables first
    Base.metadata.create_all(bind=engine)

    repo = DocumentRepository()
    repo.create_sample_data()

    print("Database seeded successfully.")