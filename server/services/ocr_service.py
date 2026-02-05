"""
Ticket OCR service: extract train number, name, coach, seat, boarding, destination
from ticket image or PDF using EasyOCR (primary) or Tesseract (fallback).
"""
import os
import re
import io
from typing import Dict, Any, Optional

# Optional: PDF to image
try:
    from pdf2image import convert_from_bytes
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False

try:
    import pytesseract
    from PIL import Image
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False


def _image_from_file(file_data: bytes, filename: str) -> Optional[Any]:
    """Return PIL Image from file bytes (image or first page of PDF)."""
    ext = (filename or "").lower().split(".")[-1]
    if ext == "pdf":
        if not HAS_PDF2IMAGE:
            return None
        pages = convert_from_bytes(file_data, first_page=1, last_page=1)
        return pages[0] if pages else None
    try:
        return Image.open(io.BytesIO(file_data)).convert("RGB")
    except Exception:
        return None


def _ocr_easyocr(image) -> str:
    if not HAS_EASYOCR:
        return ""
    reader = getattr(_ocr_easyocr, "_reader", None)
    if reader is None:
        reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        _ocr_easyocr._reader = reader
    result = reader.readtext(image)
    return " ".join([r[1] for r in result])


def _ocr_tesseract(image) -> str:
    if not HAS_TESSERACT:
        return ""
    return pytesseract.image_to_string(image)


def extract_text(file_data: bytes, filename: str, engine: Optional[str] = None) -> str:
    """
    Extract raw text from ticket image or PDF.
    engine: 'easyocr' | 'tesseract' | None (auto: easyocr then tesseract).
    """
    img = _image_from_file(file_data, filename)
    if img is None:
        return ""
    engine = (engine or os.getenv("OCR_ENGINE", "easyocr")).lower()
    if engine == "tesseract":
        return _ocr_tesseract(img)
    if engine == "easyocr":
        return _ocr_easyocr(img)
    text = _ocr_easyocr(img) if HAS_EASYOCR else ""
    if not text.strip() and HAS_TESSERACT:
        text = _ocr_tesseract(img)
    return text


# Regex patterns for Indian railway ticket text (common formats)
PATTERN_TRAIN_NUMBER = re.compile(r"\b(\d{5})\b|\b(\d{4})\b")  # 5 or 4 digit train number
PATTERN_COACH = re.compile(r"(?:Coach|COACH|Bogie|BOGIE|Compartment)\s*[:\-#]?\s*([A-Z0-9\-]+)", re.I)
PATTERN_SEAT = re.compile(r"(?:Seat|SEAT|Berth|BERTH|No\.?)\s*[:\-#]?\s*([A-Z0-9\-/]+)", re.I)
PATTERN_STATION = re.compile(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Junction|Jn|Central|Jn\.|Terminus|Jct)?")


def parse_train_details(raw_text: str) -> Dict[str, Any]:
    """
    Parse raw OCR text into structured train details.
    Returns: train_number, train_name, coach_number, seat_number, boarding_station, destination_station.
    """
    text = raw_text.replace("\n", " ").replace("\r", " ")
    result = {
        "train_number": None,
        "train_name": None,
        "coach_number": None,
        "seat_number": None,
        "boarding_station": None,
        "destination_station": None,
    }
    # Train number: often 5 digits (IR format)
    nums = PATTERN_TRAIN_NUMBER.findall(text)
    if nums:
        for n in nums:
            num = n[0] or n[1]
            if num and len(num) >= 4:
                result["train_number"] = num
                break
    # Coach
    m = PATTERN_COACH.search(text)
    if m:
        result["coach_number"] = m.group(1).strip()
    # Seat
    m = PATTERN_SEAT.search(text)
    if m:
        result["seat_number"] = m.group(1).strip()
    # Stations: look for "From X To Y" or "Boarding X Destination Y" or station names
    from_to = re.search(r"(?:From|FROM|Boarding)\s*[:\-]?\s*([A-Za-z\s]+?)\s+(?:To|TO|Destination|Dest)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\s|$|Train)", text, re.I)
    if from_to:
        result["boarding_station"] = from_to.group(1).strip()
        result["destination_station"] = from_to.group(2).strip()
    # Train name: often after train number, e.g. "12345 Rajdhani Express"
    if result["train_number"]:
        name_match = re.search(
            r"\b" + re.escape(result["train_number"]) + r"\s+([A-Za-z\s]+(?:Express|Mail|Superfast|Special|Local)?)",
            text,
            re.I,
        )
        if name_match:
            result["train_name"] = name_match.group(1).strip()
    return result


def extract_train_details_from_ticket(file_data: bytes, filename: str) -> Dict[str, Any]:
    """
    Full pipeline: OCR + parse. Returns structured train details and raw_ocr_text.
    """
    raw_text = extract_text(file_data, filename)
    details = parse_train_details(raw_text)
    details["raw_ocr_text"] = raw_text[:2000] if raw_text else None
    details["source"] = "ocr"
    return details
