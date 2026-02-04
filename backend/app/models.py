from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime
from sqlalchemy.sql import func
from .database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True, nullable=True)
    experience_years = Column(Float)
    skills = Column(JSON)  # Stores list of skills
    education = Column(JSON)
    extracted_text = Column(Text, nullable=True) # Full text for backup
    upload_date = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    security_question = Column(String)
    security_answer = Column(String) # Stored in lowercase for easier matching
