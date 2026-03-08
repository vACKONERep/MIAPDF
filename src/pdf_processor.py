"""
PDF Processing Module

Handles conversion of PDF files to images for OCR processing.
Supports multiple PDF libraries and high-resolution conversion.
"""

import logging
from typing import List, Optional, Tuple
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
import os

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Handles PDF file processing and conversion to images.
    
    Supports both PyMuPDF and pdf2image for reliable conversion.
    """
    
    def __init__(self, dpi: int = 300, image_format: str = 'PNG'):
        """
        Initialize PDF processor.
        
        Args:
            dpi: Resolution for image conversion (default: 300)
            image_format: Output image format (default: PNG)
        """
        self.dpi = dpi
        self.image_format = image_format
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def convert_pdf_to_images(self, pdf_path: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Convert PDF pages to images.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save images (optional)
            
        Returns:
            List of image file paths
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If conversion fails
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        self.logger.info(f"Converting PDF to images: {pdf_path}")
        
        try:
            # Try pdf2image first (better quality)
            return self._convert_with_pdf2image(pdf_path, output_dir)
        except Exception as e:
            self.logger.warning(f"pdf2image failed: {e}. Trying PyMuPDF...")
            # Fallback to PyMuPDF
            return self._convert_with_pymupdf(pdf_path, output_dir)
    
    def _convert_with_pdf2image(self, pdf_path: str, output_dir: Optional[str]) -> List[str]:
        """Convert PDF using pdf2image library."""
        images = convert_from_path(
            pdf_path,
            dpi=self.dpi,
            fmt=self.image_format.lower()
        )
        
        image_paths = []
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        for i, image in enumerate(images):
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                image_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.{self.image_format.lower()}")
                image.save(image_path)
                image_paths.append(image_path)
            else:
                # Keep images in memory
                image_paths.append(image)
                
        self.logger.info(f"Converted {len(images)} pages using pdf2image")
        return image_paths
    
    def _convert_with_pymupdf(self, pdf_path: str, output_dir: Optional[str]) -> List[str]:
        """Convert PDF using PyMuPDF library."""
        doc = fitz.open(pdf_path)
        image_paths = []
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        try:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Create transformation matrix for high resolution
                zoom = self.dpi / 72  # 72 DPI is default
                mat = fitz.Matrix(zoom, zoom)
                
                # Render page to pixmap
                pix = page.get_pixmap(matrix=mat)
                
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    image_path = os.path.join(output_dir, f"{base_name}_page_{page_num+1}.{self.image_format.lower()}")
                    pix.save(image_path)
                    image_paths.append(image_path)
                else:
                    # Convert to PIL Image and keep in memory
                    img_data = pix.tobytes(self.image_format.lower())
                    image = Image.open(io.BytesIO(img_data))
                    image_paths.append(image)
                    
                pix = None  # Free memory
                
        finally:
            doc.close()
            
        self.logger.info(f"Converted {len(image_paths)} pages using PyMuPDF")
        return image_paths
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get PDF metadata information.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        try:
            doc = fitz.open(pdf_path)
            info = {
                'page_count': len(doc),
                'metadata': doc.metadata,
                'file_size': os.path.getsize(pdf_path)
            }
            doc.close()
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get PDF info: {e}")
            raise
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate if file is a readable PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            doc = fitz.open(pdf_path)
            is_valid = len(doc) > 0
            doc.close()
            return is_valid
        except:
            return False