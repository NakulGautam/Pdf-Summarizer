from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import fitz
import os

# ---------- LOAD ENV VARIABLES ----------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=api_key)

# ---------- CREATE UPLOADS FOLDER ----------

os.makedirs("uploads", exist_ok=True)

# ---------- FASTAPI APP ----------

app = FastAPI(
    title="AI PDF Summarizer API",
    description="Upload a PDF and get an AI-generated summary",
    version="1.0.0"
)

# ---------- CORS ----------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pdf-summarizer-nine-psi.vercel.app/"],  # Change this later in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- PDF TEXT EXTRACTION ----------

def extract_text_from_pdf(pdf_path):
    text = ""

    pdf = fitz.open(pdf_path)

    for page in pdf:
        text += page.get_text()

    pdf.close()

    return text


# ---------- AI SUMMARY ----------

def generate_summary(text):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"""
You are a PDF summarizer.

Summarize the content using ONLY bullet points.

Rules:
- Start every line with •
- Do not use headings
- Do not use markdown symbols like #, *, +, **
- Do not create sections
- Keep each bullet short and clear
- Generate 10-20 bullet points depending on content

PDF Content:
{text}
"""
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


# ---------- HOME ROUTES ----------

@app.get("/", tags=["Home"])
def root():
    return {
        "message": "AI PDF Summarizer API Running Successfully"
    }


@app.get("/about", tags=["Home"])
def about():
    return {
        "message": "Upload a PDF and get an AI-generated summary"
    }


# ---------- PDF UPLOAD ROUTE ----------

@app.post("/upload", tags=["PDF"])
async def upload_file(file: UploadFile = File(...)):

    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        return {
            "error": "Only PDF files are allowed"
        }

    file_path = f"uploads/{file.filename}"

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Extract PDF text
    extracted_text = extract_text_from_pdf(file_path)

    if not extracted_text.strip():
        return {
            "error": "No text found in PDF"
        }

    # Limit text size sent to AI
    summary = generate_summary(extracted_text[:20000])

    return {
        "filename": file.filename,
        "summary": summary
    }


# ---------- USER MODEL ----------

class User(BaseModel):
    name: str
    age: int


# ---------- USER ROUTE ----------

@app.post("/user", tags=["User"])
def create_user(user: User):
    return {
        "name": user.name,
        "age": user.age
    }