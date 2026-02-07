import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
from pdf2image import convert_from_path
from PIL import Image

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system",
             "content": "You are an OCR engine. Extract all text exactly, preserve Nepali characters, do not summarize.Also make sure the language should be same . For Example Nepali text document"
             "should extract nepali as it is written in the image . Also, keep the formatting as it is. Dont chnage format. Dont summarise."},
            {"role": "user",
             "content": [
                 {"type": "text", "text": "Extract text from this document."},
                 {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
             ]}
        ],
        temperature=0
    )
    return response.choices[0].message.content

def extract_text_from_pdf(pdf_path: str) -> str:
    images = convert_from_path(pdf_path)
    all_text = ""
    for i, img in enumerate(images):
        temp_path = f"temp_page_{i}.png"
        img.save(temp_path, "PNG")
        all_text += extract_text_from_image(temp_path) + "\n"
        os.remove(temp_path)
    return all_text




