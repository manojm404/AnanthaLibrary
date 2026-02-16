from google.cloud import firestore
from app.config import settings

class FirestoreRepository:

    def __init__(self):
        self.client = firestore.Client(project=settings.GCP_PROJECT_ID)
        self.collection = self.client.collection(settings.FIRESTORE_COLLECTION)

    def get_all_documents(self):
        docs = self.collection.stream()
        return [doc.to_dict() for doc in docs]

    def get_document_by_slug(self, slug: str):
        query = self.collection.where("slug", "==", slug).limit(1).stream()
        for doc in query:
            return doc.to_dict()
        return None