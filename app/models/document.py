from sqlalchemy import Column, String, Text
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)
    language = Column(String)
    category = Column(String)
    content = Column(Text)