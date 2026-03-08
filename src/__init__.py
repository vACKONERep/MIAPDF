"""
Spanish PDF Forms OCR Package

A comprehensive solution for processing handwritten Spanish PDF forms
and extracting data to CSV format.
"""

__version__ = "1.0.0"
__author__ = "PDF OCR Expert"
__email__ = "expert@pdfocr.com"

from .pdf_processor import PDFProcessor
from .ocr_engine import OCREngine
from .image_preprocessor import ImagePreprocessor
from .form_extractor import FormExtractor
from .csv_exporter import CSVExporter

__all__ = [
    'PDFProcessor',
    'OCREngine',
    'ImagePreprocessor',
    'FormExtractor',
    'CSVExporter'
]