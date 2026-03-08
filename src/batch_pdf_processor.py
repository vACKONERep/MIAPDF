# batch_pdf_processor.py
"""
Batch PDF Processor for extracting text from PDFs using OCR.
Based on the provided script, adapted for the project structure.
"""

from pdf2image import convert_from_path
from paddleocr import PaddleOCR
import re
import pandas as pd
import cv2
import numpy as np
import os
import glob
from tqdm import tqdm
from pathlib import Path

# Initialize OCR (once)
ocr = PaddleOCR(use_angle_cls=True, lang='es')

def preprocess_image(img_path):
    """Preprocess image for better OCR."""
    img = cv2.imread(img_path)  # Keep color
    bilateral = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
    lab = cv2.cvtColor(bilateral, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    cv2.imwrite(img_path, enhanced)
    return img_path

def ocr_page(pages, page_idx):
    """OCR a single page."""
    img_path = f'page_{page_idx}.jpg'
    pages[page_idx].save(img_path, 'JPEG')
    preprocess_image(img_path)

    result = ocr.ocr(img_path, cls=True)
    if result and result[0]:
        return '\n'.join([line[1][0].strip() for line in result[0] if line[1][0].strip()])
    return ""

def extract_after(text, keyword):
    """Extract text after keyword."""
    pattern = rf'(?i){re.escape(keyword)}\s*[:=]?\s*([^:\n]+?)(?=\s*(?:Tutor|Semestre|Hospital|Rotacion|Rotación|Unidad|Periodo|Período|NOTA|NÚMERO|Banner|Facultad|RESPONSABLE|$)|\n\n)'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        val = match.group(1).strip()
        return re.sub(r'\s+', ' ', val)
    return "NO DETECTADO"

def extract_nota(text):
    """Extract nota_total."""
    pattern = rf'(?i)nota\s*total\s*[:=]?\s*(\d+[\.,]?\d*)'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        val = match.group(1).replace(',', '.')
        return val
    # Fallback: last number in text
    numbers = re.findall(r'\d+[\.,]?\d*', text)
    if numbers:
        return numbers[-1].replace(',', '.')
    return "NO DETECTADO"

def process_pdf(pdf_file):
    """Process a single PDF."""
    try:
        pages = convert_from_path(pdf_file, dpi=450)
        total_pages = len(pages)
        if total_pages < 2:
            print(f"{pdf_file} has only {total_pages} pages → skipped")
            return None

        # Last 2 pages
        text_last1 = ocr_page(pages, total_pages - 1)
        text_last2 = ocr_page(pages, total_pages - 2)

        combined_text = text_last2 + "\n\n" + text_last1

        return {
            'archivo_pdf': os.path.basename(pdf_file),
            'Nombre_del_estudiante': extract_after(combined_text, 'Nombre del estudiante'),
            'Semestre': extract_after(combined_text, 'Semestre'),
            'Hospital': extract_after(combined_text, 'Unidad Asistencial Docente'),
            'Rotacion': extract_after(combined_text, 'Rotacion'),
            'nota_total': extract_nota(combined_text)
        }
    except Exception as e:
        print(f"Error {pdf_file}: {e}")
        return None

def batch_process_pdfs(input_folder, output_csv):
    """Process all PDFs in input_folder and save to output_csv."""
    pdf_files = sorted(glob.glob(os.path.join(input_folder, '*.pdf')))
    print(f"Found {len(pdf_files)} PDFs")

    results = []
    for pdf in tqdm(pdf_files, desc="Processing PDFs"):
        row = process_pdf(pdf)
        if row:
            results.append(row)

    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"\nCSV generated ({len(df)} rows): {output_csv}")
        print(df)
    else:
        print("No PDFs processed.")

if __name__ == "__main__":
    # Default paths
    INPUT_FOLDER = 'data/input'
    OUTPUT_CSV = 'data/output/batch_extracted_data.csv'

    # Ensure directories exist
    Path(INPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(os.path.dirname(OUTPUT_CSV)).mkdir(parents=True, exist_ok=True)

    batch_process_pdfs(INPUT_FOLDER, OUTPUT_CSV)