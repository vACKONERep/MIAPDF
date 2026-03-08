#!/usr/bin/env python3
"""
Script para extraer campos de handwriting en español de PDFs.
Extrae: Nombre del estudiante, Semestre, Hospital, Rotacion, nota_total
Guarda en CSV simple con una fila.

Uso: python process_handwritten_pdf.py <ruta_pdf> <ruta_salida_csv>
"""

import argparse
import logging
import sys
from pathlib import Path
import re
from typing import List, Tuple, Dict, Any, Optional
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
import cv2
import numpy as np
import io

# Intentar importar PaddleOCR, forzar su uso
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    logger.error("PaddleOCR no disponible, instala con: pip install paddlepaddle==2.6.2 paddleocr==2.8.1")
    exit(1)

# Intentar importar EasyOCR como fallback
try:
    import easyocr
    EASY_AVAILABLE = True
except ImportError:
    EASY_AVAILABLE = False

# No usar EasyOCR, forzar PaddleOCR

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Campos a extraer
FIELDS = ['Nombre del estudiante', 'Semestre', 'Hospital', 'Rotacion']

# Correcciones comunes de OCR para español handwriting
OCR_CORRECTIONS = {
    '0': 'o',
    '1': 'l',
    '3': 'e',
    '5': 's',
    '6': 'b',
    '8': 'b',
    'p3p': 'pep',
    'n0v': 'nov',
    'c1r': 'cir',
    '0r': 'or',
    'rug1': 'rug',
    'g3n': 'gen',
    'h4b': 'hab',
    # Agregar más según necesidad
}

# Variaciones de keywords
KEYWORD_VARIATIONS = {
    'Nombre del estudiante': ['nombre del estudiante', 'nombrc dcl cstudIantc', 'Nombre del estudlante', 'nombre'],
    'Semestre': ['semestre', 'Ncveno', 'Noveno', 'semestre: Ncveno', 'sem'],
    'Hospital': ['hospital', 'Hcsoital', 'Hospltal', 'fudre Carollc', 'Padre Carollo', 'hosp'],
    'Rotacion': ['rotacion', 'rotaciön', 'Orcg:a ccnral', 'Cirugia General', 'Orcg:a', 'rot'],
}

def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Preprocesamiento agresivo para handwriting cursivo en formularios."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    # Ecualización fuerte + bilateral para preservar bordes
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    bilateral = cv2.bilateralFilter(enhanced, d=11, sigmaColor=85, sigmaSpace=85)
    
    # Threshold Otsu + inversión (fondo oscuro → texto blanco)
    _, thresh = cv2.threshold(bilateral, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresh = cv2.bitwise_not(thresh)  # Invierte si fondo es oscuro
    
    # Dilatación para conectar letras cursivas + erosión ligera para ruido
    kernel_dilate = np.ones((3,3), np.uint8)
    dilated = cv2.dilate(thresh, kernel_dilate, iterations=2)
    kernel_erode = np.ones((2,2), np.uint8)
    cleaned = cv2.erode(dilated, kernel_erode, iterations=1)
    
    # Remueve líneas horizontales/verticales del formulario (muy útil aquí)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40,1))
    horizontal_lines = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,40))
    vertical_lines = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    lines = cv2.add(horizontal_lines, vertical_lines)
    cleaned = cv2.subtract(cleaned, lines)
    
    return cleaned

def extract_text_with_paddle(image: np.ndarray) -> List[Tuple[str, List[List[int]], float]]:
    """Extrae texto con PaddleOCR."""
    ocr = PaddleOCR(use_textline_orientation=True, lang='es')
    results = ocr.ocr(image, cls=True)
    # Formato: [[bbox, (text, conf)], ...]
    formatted = []
    for line in results[0] if results and results[0] else []:
        bbox, (text, conf) = line
        # Convertir bbox a formato similar a EasyOCR
        bbox_points = [[int(p[0]), int(p[1])] for p in bbox]
        formatted.append((text, bbox_points, float(conf)))
    return formatted

def extract_text_with_easyocr(image: np.ndarray) -> List[Tuple[str, List[List[int]], float]]:
    """Extrae texto con EasyOCR (fallback)."""
    reader = easyocr.Reader(['es'], gpu=False)
    results = reader.readtext(image, detail=1)
    return results

def extract_text_with_ocr(image: np.ndarray) -> List[Tuple[str, List[List[int]], float]]:
    """Extrae texto usando PaddleOCR, con fallback a EasyOCR."""
    logger.info("Usando PaddleOCR para extracción de texto")
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='es')
        results = ocr.ocr(image)
        formatted = []
        if results is not None and isinstance(results, list) and len(results) > 0:
            page_results = results[0]
            if isinstance(page_results, list):
                for line in page_results:
                    if isinstance(line, list) and len(line) == 2:
                        bbox = line[0]
                        text_conf = line[1]
                        if isinstance(text_conf, tuple) and len(text_conf) == 2:
                            text, conf = text_conf
                            bbox_points = [[int(p[0]), int(p[1])] for p in bbox] if isinstance(bbox, list) and len(bbox) >= 4 else []
                            formatted.append((text, bbox_points, float(conf)))
        if formatted:
            return formatted
    except Exception as e:
        logger.error(f"Error con PaddleOCR: {e}")
    
    # Fallback a EasyOCR
    logger.info("Usando EasyOCR como fallback")
    try:
        reader = easyocr.Reader(['es'], gpu=False)
        results = reader.readtext(image, detail=1)
        formatted = []
        for (bbox, text, conf) in results:
            bbox_points = [[int(x), int(y)] for x, y in bbox]
            formatted.append((text, bbox_points, float(conf)))
        return formatted
    except Exception as e:
        logger.error(f"Error con EasyOCR: {e}")
        return []

def post_process_text(text: str) -> str:
    """Corrige errores comunes en texto OCR."""
    if not text:
        return ""
    corrected = text.lower().strip()
    # Aplicar correcciones
    for wrong, right in OCR_CORRECTIONS.items():
        corrected = corrected.replace(wrong, right)
    # Capitalizar nombres
    corrected = ' '.join(word.capitalize() for word in corrected.split())
    return corrected

def find_value_near_keyword(results: List[Tuple[str, List[List[int]], float]], keyword: str) -> Tuple[str, float]:
    """Encuentra el valor más cercano al keyword."""
    keyword_lower = keyword.lower()
    variations = KEYWORD_VARIATIONS.get(keyword, [keyword_lower])
    keyword_bbox = None
    candidates = []

    # Encontrar el keyword o variaciones
    for text, bbox, conf in results:
        text_lower = text.lower()
        if any(var in text_lower for var in variations):
            keyword_bbox = np.mean(bbox, axis=0)
            break

    if not keyword_bbox:
        return "", 0.0

    # Encontrar texto cercano (derecha o abajo)
    for text, bbox, conf in results:
        if any(var in text.lower() for var in variations):
            continue
        center = np.mean(bbox, axis=0)
        # Distancia
        dist = np.linalg.norm(center - keyword_bbox)
        # Dirección: preferir derecha o abajo
        if center[0] > keyword_bbox[0] or center[1] > keyword_bbox[1]:
            candidates.append((text, conf, dist))

    if candidates:
        # Tomar el más cercano
        candidates.sort(key=lambda x: x[2])
        best_text, best_conf, _ = candidates[0]
        return post_process_text(best_text), best_conf

    return "", 0.0

def extract_nota_total(results: List[Tuple[str, List[List[int]], float]]) -> str:

    # Encontrar texto cercano (derecha o abajo)
    for bbox, text, conf in results:
        if text.lower() == keyword_lower:
            continue
        center = np.mean(bbox, axis=0)
        # Distancia
        dist = np.linalg.norm(center - keyword_bbox)
        # Dirección: preferir derecha o abajo
        if center[0] > keyword_bbox[0] or center[1] > keyword_bbox[1]:
            candidates.append((text, conf, dist))

    if candidates:
        # Tomar el más cercano
        candidates.sort(key=lambda x: x[2])
        best_text, best_conf, _ = candidates[0]
        return post_process_text(best_text), best_conf

    return "", 0.0

def extract_nota_total(results: List[Tuple[str, List[List[int]], float]]) -> str:
    """Extrae la nota total de la página."""
    # Buscar números directamente
    numbers = []
    for bbox, text, conf in results:
        # Buscar patrones de nota: dígitos con punto
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            numbers.append((match.group(1), conf))

    if numbers:
        # Tomar el de mayor confianza
        numbers.sort(key=lambda x: x[1], reverse=True)
        return numbers[0][0]

    # Buscar cerca de "nota total"
    return find_value_near_keyword(results, "nota total")[0] or find_value_near_keyword(results, "nota")[0]

def process_pdf(pdf_path: str, output_csv: str):
    """Procesa el PDF y guarda resultados en CSV."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")

    # Abrir PDF con PyMuPDF
    logger.info("Abriendo PDF...")
    doc = fitz.open(pdf_path)
    num_pages = len(doc)

    if num_pages < 2:
        raise ValueError(f"El PDF tiene {num_pages} páginas, se requieren al menos 2.")

    # Tomar las últimas 2 páginas
    pages_to_process = [num_pages - 2, num_pages - 1] if num_pages >= 2 else [0, 1]

    extracted_data = {}

    for page_idx in pages_to_process:
        page_num = page_idx + 1
        logger.info(f"Procesando página {page_num}...")

        # Convertir página a imagen
        page = doc.load_page(page_idx)
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes())).convert('RGB')
        image_np = np.array(img)

        # Preprocesar
        processed_image = preprocess_image(image_np)

        # Extraer texto
        results = extract_text_with_ocr(processed_image)

        # Debug: mostrar texto detectado
        logger.info(f"Texto detectado en página {page_num}:")
        for text, bbox, conf in results:
            logger.info(f"  '{text}' (conf: {conf:.2f}) - bbox: {bbox}")

        # Extraer campos
        for field in FIELDS:
            if field not in extracted_data or extracted_data[field][1] < 0.5:  # Solo si no tiene buen valor
                value, conf = find_value_near_keyword(results, field)
                if value:
                    extracted_data[field] = (value, conf)

        # Extraer nota_total solo de la última página
        if page_num == pages_to_process[-1]:
            nota = extract_nota_total(results)
            if nota:
                extracted_data['nota_total'] = (nota, 1.0)

    doc.close()

    # Preparar fila para CSV
    row = {}
    for field in FIELDS + ['nota_total']:
        value, conf = extracted_data.get(field, ("", 0.0))
        row[field.replace(' ', '_')] = value if conf > 0.3 else "NO DETECTADO"
        if not value:
            logger.warning(f"No se detectó {field}")

    # Guardar CSV
    df = pd.DataFrame([row])
    df.to_csv(output_csv, index=False)
    logger.info(f"Resultados guardados en {output_csv}")
    logger.info(f"Fila extraída: {row}")

def main():
    parser = argparse.ArgumentParser(description="Extrae campos de handwriting de PDF a CSV")
    parser.add_argument("pdf_path", help="Ruta al archivo PDF")
    parser.add_argument("output_csv", help="Ruta para el archivo CSV de salida")
    args = parser.parse_args()

    try:
        process_pdf(args.pdf_path, args.output_csv)
    except Exception as e:
        logger.error(f"Error procesando PDF: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()