from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
import os
import base64
import json

from ocr import extract_text_from_image, extract_text_from_pdf

app = FastAPI(title="Nepali OCR AI")
templates = Jinja2Templates(directory="templates")

HISTORY_FILE = "history.json"

# ---------- LOAD HISTORY FROM DISK ----------
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = []

# ---------- SAVE HISTORY TO DISK ----------
def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ext = file.filename.split(".")[-1].lower()

    entry = {
        "filename": file.filename,
        "type": "",
        "text": "",
        "image": None
    }

    if ext in ["png", "jpg", "jpeg"]:
        entry["type"] = "image"
        entry["text"] = extract_text_from_image(temp_path)

        with open(temp_path, "rb") as f:
            entry["image"] = base64.b64encode(f.read()).decode()

    elif ext == "pdf":
        entry["type"] = "pdf"
        entry["text"] = extract_text_from_pdf(temp_path)

    else:
        os.remove(temp_path)
        return {"error": "Unsupported file type"}

    os.remove(temp_path)

    # newest first
    history.insert(0, entry)
    save_history()

    return {
        "extracted_text": entry["text"],
        "history": history
    }

@app.get("/history")
def get_history():
    return history
