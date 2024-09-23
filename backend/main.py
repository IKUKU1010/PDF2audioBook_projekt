from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PyPDF2 import PdfFileReader
from gtts import gTTS
from io import BytesIO
import os
from pathlib import Path
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi import Request

app = FastAPI()

# Path for storing the static files
audio_path = Path("backend/static/audio")
audio_path.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Template rendering
templates = Jinja2Templates(directory="backend/templates")

# Extract text from PDF
def extract_text_from_pdf(file):
    reader = PdfFileReader(file)
    text = ""
    for page_num in range(reader.numPages):
        text += reader.getPage(page_num).extract_text()
    return text

# Convert text to speech
def text_to_speech(text, filename):
    tts = gTTS(text)
    audio_file_path = audio_path / filename
    tts.save(str(audio_file_path))
    return audio_file_path

# Serve the main page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Upload and convert PDF
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type == "application/pdf":
        pdf_content = await file.read()
        pdf_reader = BytesIO(pdf_content)

        # Extract text and convert to audio
        text = extract_text_from_pdf(pdf_reader)
        audio_file = text_to_speech(text, "audiobook.mp3")

        return {"message": "Conversion successful!", "audio_file": str(audio_file)}

    return {"error": "Only PDF files are allowed"}

# Endpoint to serve the audio file
@app.get("/audio/{file_name}")
async def get_audio(file_name: str):
    file_path = audio_path / file_name
    if file_path.exists():
        return FileResponse(file_path)
    return {"error": "File not found"}
