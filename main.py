import cv2 as cv
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import easyocr
from rapidfuzz import process, fuzz
import re
import mysql.connector

app = FastAPI(title="Prescription Pipeline API")


def get_db_connection():
    """Establishes connection to the local MySQL database."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="medicines"
    )


# Initialize OCR and load database into memory on startup
print("Initializing System...")
db_conn = get_db_connection()
db_cursor = db_conn.cursor()
db_cursor.execute("SELECT name FROM medicines")
real_medicine_db = [row[0] for row in db_cursor.fetchall()]
db_cursor.close()
db_conn.close()

reader = easyocr.Reader(['en'], gpu=False)
print("System Ready.")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)


def clean_image_for_api(image_bytes):
    """Applies OpenCV filters to enhance image for OCR extraction."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv.imdecode(nparr, cv.IMREAD_COLOR)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    thresh = cv.adaptiveThreshold(
        blurred, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 21, 10)
    return thresh


def fuzzy_match_medicine(ocr_text, database):
    """Performs whole-word fuzzy matching against the medicines database."""
    cleaned_ocr_text = re.sub(r'[^a-zA-Z0-9\s]', '', ocr_text)
    result = process.extractOne(
        cleaned_ocr_text, database, scorer=fuzz.token_set_ratio)

    if not result:
        return None, 0.0
    return result[0], result[1]


def get_medicine_details(brand_name):
    """Queries MySQL for the verified medicine's price and its substitutes."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT price, substitute0, substitute1, substitute2 FROM medicines WHERE name = %s LIMIT 1", (
            brand_name,)
    )
    med_data = cursor.fetchone()

    if not med_data:
        cursor.close()
        conn.close()
        return None, []

    original_price = med_data['price']
    subs = [med_data['substitute0'],
            med_data['substitute1'], med_data['substitute2']]
    valid_subs = [s for s in subs if s and s.strip()]
    alternatives = []

    if valid_subs:
        format_strings = ','.join(['%s'] * len(valid_subs))
        query = f"SELECT name, price FROM medicines WHERE name IN ({format_strings})"
        cursor.execute(query, tuple(valid_subs))

        for row in cursor.fetchall():
            alternatives.append({
                "name": row['name'],
                "price": row['price'],
                "savings": original_price - row['price'] if original_price > row['price'] else 0
            })

    cursor.close()
    conn.close()
    return original_price, alternatives


@app.post("/process-prescription/")
async def process_prescription(file: UploadFile = File(...)):
    """Master endpoint to process prescription images and return medicine details."""
    try:
        image_bytes = await file.read()
        cleaned_image = clean_image_for_api(image_bytes)
        raw_text_list = reader.readtext(cleaned_image, detail=0)

        best_overall_match = None
        highest_confidence = 0.0

        for messy_line in raw_text_list:
            messy_lower = messy_line.lower()

            # Filter out standard dosage instructions
            dosage_keywords = ['take', 'daily', 'twice', 'thrice',
                               'after', 'before', 'food', 'morning', 'night', 'hours']
            if any(word in messy_lower for word in dosage_keywords):
                continue

            # Remove generic pharmaceutical terms to isolate the brand name
            generic_words = ['tablet', 'tab', 'capsule',
                             'cap', 'syrup', 'mg', 'ml', 'liquid', 'drop']
            cleaned_line = messy_lower
            for word in generic_words:
                cleaned_line = re.sub(rf'\b{word}\b', '', cleaned_line)

            # Ignore strings that lack sufficient alphabetical characters
            just_letters = re.sub(r'[^a-zA-Z]', '', cleaned_line)
            if len(just_letters) < 3:
                continue

            match, confidence = fuzzy_match_medicine(
                cleaned_line, real_medicine_db)

            if confidence > highest_confidence:
                highest_confidence = confidence
                best_overall_match = match

        # Verify against the safety threshold (75.0)
        if highest_confidence >= 75.0:
            original_price, alternatives = get_medicine_details(
                best_overall_match)

            return {
                "status": "success",
                "verified_medicine": best_overall_match,
                "original_price": original_price,
                "confidence_score": round(highest_confidence, 2),
                "cheaper_alternatives": alternatives
            }
        else:
            return {
                "status": "warning",
                "verified_medicine": None,
                "confidence_score": round(highest_confidence, 2),
                "message": "Handwriting too messy."
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}
