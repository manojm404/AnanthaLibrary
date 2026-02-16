import os

class Settings:
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "documents")
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() == "true"

settings = Settings()