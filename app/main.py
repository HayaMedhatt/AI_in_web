import os
import fitz  # PyMuPDF
import spacy
from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from typing import List, Tuple
import json  # To save data in JSON format

# Database connection URL
DATABASE_URL = "postgresql://postgres:password@db:5432/nlp_db"

# Set up SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app setup
app = FastAPI()

# Load the spaCy NER model
current_dir = os.getcwd()
file_path = os.path.join(current_dir, "app/Model/nlp_ner_model2")

if os.path.exists(file_path):
    ner_model = spacy.load(file_path)
else:
    print(f"Model not found at: {file_path}")
    exit()

def extract_all_information(nlp, text: str) -> List[Tuple[str, str]]:
    doc = nlp(text)
    extracted_data = [(ent.label_, ent.text) for ent in doc.ents]
    return extracted_data

def extract_text_from_pdf(uploaded_file: UploadFile) -> str:
    try:
        file_path = "uploaded_resume.pdf"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.file.read())

        text = ""
        with fitz.open(file_path) as pdf:
            for page_num in range(len(pdf)):
                page = pdf.load_page(page_num)
                text += page.get_text()
        text = " ".join(text.split('\n'))

        os.remove(file_path)
        return text
    except Exception as e:
        return f"Error processing the PDF: {e}"

def save_to_database(db, data):
    # Assuming a simple model with the columns 'label' and 'text'
    from sqlalchemy import Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    class ExtractedData(Base):
        __tablename__ = 'extracted_data'
        id = Column(Integer, primary_key=True, index=True)
        label = Column(String, index=True)
        text = Column(String)

    db.create_all()  # Create tables if they don't exist

    for label, text in data:
        db.add(ExtractedData(label=label, text=text))
    db.commit()

@app.post("/extract-info/")
async def extract_info_from_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    resume_text = extract_text_from_pdf(file)
    if "Error" in resume_text:
        return {"error": resume_text}

    extracted_info = extract_all_information(ner_model, resume_text)

    save_to_database(db, extracted_info)

    return {"extracted_info": extracted_info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
