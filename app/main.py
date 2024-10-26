import os
import fitz  # PyMuPDF
import spacy
from fastapi import FastAPI, UploadFile, File
from typing import List, Tuple
import json  # To save data in JSON format

app = FastAPI()

# Load the spaCy NER model
# Print the current working directory
current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")

# Adjust the path if necessary based on your file location
file_path = os.path.join(current_dir, "app/Model/nlp_ner_model2")

# Check if the model file exists
if os.path.exists(file_path):
    print(f"Model found at: {file_path}")
    ner_model = spacy.load(file_path)
    print("Model loaded successfully.")
else:
    print(f"Model not found at: {file_path}")
    exit()
def extract_all_information(nlp, text: str) -> List[Tuple[str, str]]:
    """Extract named entities from the text using the NER model."""
    doc = nlp(text)
    extracted_data = [(ent.label_, ent.text) for ent in doc.ents]
    return extracted_data

def extract_text_from_pdf(uploaded_file: UploadFile) -> str:
    """Extract text from the uploaded PDF file."""
    try:
        # Save the uploaded file locally
        file_path = "uploaded_resume.pdf"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.file.read())

        # Process the PDF using PyMuPDF
        text = ""
        with fitz.open(file_path) as pdf:
            for page_num in range(len(pdf)):
                page = pdf.load_page(page_num)
                text += page.get_text()
        text = " ".join(text.split('\n'))

        # Remove the temporary file
        os.remove(file_path)

        return text
    except Exception as e:
        return f"Error processing the PDF: {e}"

def save_extracted_data(data: List[Tuple[str, str]], filename: str):
    """Save the extracted data to a text file."""
    try:
        # Save data as JSON for easier reading
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving data to file: {e}")

@app.post("/extract-info/")
async def extract_info_from_pdf(file: UploadFile = File(...)):
    """Endpoint to extract information from an uploaded PDF file."""
    resume_text = extract_text_from_pdf(file)
    if "Error" in resume_text:
        return {"error": resume_text}

    # Extract information from resume using NER model
    extracted_info = extract_all_information(ner_model, resume_text)

    # Save extracted data to a text file
    save_extracted_data(extracted_info, "extracted_data.json")

    # Return all extracted entities and their labels
    return {"extracted_info": extracted_info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
