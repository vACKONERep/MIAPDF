"""
OCR Engine Module

Handles multiple OCR engines for Spanish handwritten text recognition.
Supports Tesseract, Google Vision API, and Azure Computer Vision.
"""

import logging
import os
from typing import List, Dict, Optional, Union, Tuple
import numpy as np
from PIL import Image
import pytesseract
from dataclasses import dataclass
import json

# Optional imports for cloud OCR services
try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False

try:
    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
    from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
    from msrest.authentication import CognitiveServicesCredentials
    import time
    AZURE_VISION_AVAILABLE = True
except ImportError:
    AZURE_VISION_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Structure for OCR results."""
    text: str
    confidence: float
    bounding_boxes: List[Tuple[int, int, int, int]]
    engine_used: str
    language_detected: Optional[str] = None


class OCREngine:
    """
    Multi-engine OCR processor optimized for Spanish handwritten text.
    
    Supports multiple OCR engines with fallback capabilities and confidence scoring.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize OCR engine with configuration.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.config = self._load_config(config_path)
        
        # Initialize available engines
        self.available_engines = self._check_available_engines()
        self.logger.info(f"Available OCR engines: {list(self.available_engines.keys())}")
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load OCR configuration."""
        default_config = {
            "tesseract": {
                "language": "spa",
                "oem": 3,
                "psm": 6,
                "config": "--oem 3 --psm 6 -l spa -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚáéíóúÑñ "
            },
            "google_vision": {
                "language_hints": ["es"],
                "enable_handwriting": True
            },
            "azure_vision": {
                "language": "es",
                "detect_orientation": True
            },
            "ensemble": {
                "enabled": True,
                "min_confidence": 0.7,
                "engines_to_use": ["tesseract", "google_vision"]
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")
                
        return default_config
    
    def _check_available_engines(self) -> Dict[str, bool]:
        """Check which OCR engines are available."""
        engines = {}
        
        # Check Tesseract
        try:
            pytesseract.get_tesseract_version()
            engines['tesseract'] = True
        except Exception:
            engines['tesseract'] = False
            self.logger.warning("Tesseract not available")
            
        # Check Google Vision
        engines['google_vision'] = GOOGLE_VISION_AVAILABLE and os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not engines['google_vision']:
            self.logger.warning("Google Vision API not available (missing credentials)")
            
        # Check Azure Vision
        engines['azure_vision'] = AZURE_VISION_AVAILABLE and os.getenv('AZURE_COMPUTER_VISION_KEY')
        if not engines['azure_vision']:
            self.logger.warning("Azure Computer Vision not available (missing credentials)")
            
        return engines
    
    def process_image(self, image: Union[np.ndarray, Image.Image], 
                     engine: str = "auto") -> OCRResult:
        """
        Process image with OCR engine(s).
        
        Args:
            image: Input image (numpy array or PIL Image)
            engine: OCR engine to use ("auto", "tesseract", "google_vision", "azure_vision")
            
        Returns:
            OCRResult with extracted text and metadata
        """
        self.logger.info(f"Processing image with engine: {engine}")
        
        # Convert to PIL Image if numpy array
        if isinstance(image, np.ndarray):
            pil_image = Image.fromarray(image)
        else:
            pil_image = image
            
        if engine == "auto":
            return self._process_with_best_engine(pil_image)
        elif engine == "ensemble":
            return self._process_with_ensemble(pil_image)
        else:
            return self._process_with_single_engine(pil_image, engine)
    
    def _process_with_single_engine(self, image: Image.Image, engine: str) -> OCRResult:
        """Process with a single OCR engine."""
        if engine == "tesseract":
            return self._process_with_tesseract(image)
        elif engine == "google_vision":
            return self._process_with_google_vision(image)
        elif engine == "azure_vision":
            return self._process_with_azure_vision(image)
        else:
            raise ValueError(f"Unknown engine: {engine}")
    
    def _process_with_tesseract(self, image: Image.Image) -> OCRResult:
        """Process with Tesseract OCR."""
        if not self.available_engines.get('tesseract', False):
            raise RuntimeError("Tesseract not available")
            
        config = self.config['tesseract']
        custom_config = f"--oem {config['oem']} --psm {config['psm']} -l {config['language']}"
        
        # Add character whitelist for Spanish
        if 'config' in config:
            custom_config = config['config']
            
        try:
            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # Get detailed data for confidence and bounding boxes
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract bounding boxes for words
            bounding_boxes = []
            for i, conf in enumerate(data['conf']):
                if int(conf) > 30:  # Only include high-confidence detections
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    bounding_boxes.append((x, y, x + w, y + h))
            
            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence / 100.0,
                bounding_boxes=bounding_boxes,
                engine_used="tesseract",
                language_detected="es"
            )
            
        except Exception as e:
            self.logger.error(f"Tesseract processing failed: {e}")
            raise
    
    def _process_with_google_vision(self, image: Image.Image) -> OCRResult:
        """Process with Google Vision API."""
        if not self.available_engines.get('google_vision', False):
            raise RuntimeError("Google Vision API not available")
            
        try:
            client = vision.ImageAnnotatorClient()
            
            # Convert PIL image to bytes
            import io
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            vision_image = vision.Image(content=img_byte_arr)
            
            # Configure for Spanish handwriting
            image_context = vision.ImageContext(
                language_hints=self.config['google_vision']['language_hints']
            )
            
            # Use document text detection (better for handwriting)
            response = client.document_text_detection(
                image=vision_image,
                image_context=image_context
            )
            
            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")
                
            # Extract text and confidence
            full_text = response.full_text_annotation.text if response.full_text_annotation else ""
            
            # Calculate average confidence from pages
            confidences = []
            bounding_boxes = []
            
            if response.full_text_annotation:
                for page in response.full_text_annotation.pages:
                    for block in page.blocks:
                        # Get block bounding box
                        vertices = block.bounding_box.vertices
                        if vertices:
                            x_coords = [v.x for v in vertices]
                            y_coords = [v.y for v in vertices]
                            bbox = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
                            bounding_boxes.append(bbox)
                            
                        # Get confidence from paragraphs
                        for paragraph in block.paragraphs:
                            confidences.append(paragraph.confidence)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.8
            
            return OCRResult(
                text=full_text.strip(),
                confidence=avg_confidence,
                bounding_boxes=bounding_boxes,
                engine_used="google_vision",
                language_detected="es"
            )
            
        except Exception as e:
            self.logger.error(f"Google Vision processing failed: {e}")
            raise
    
    def _process_with_azure_vision(self, image: Image.Image) -> OCRResult:
        """Process with Azure Computer Vision API."""
        if not self.available_engines.get('azure_vision', False):
            raise RuntimeError("Azure Computer Vision not available")
            
        try:
            # Initialize client
            key = os.getenv('AZURE_COMPUTER_VISION_KEY')
            endpoint = os.getenv('AZURE_COMPUTER_VISION_ENDPOINT')
            
            credentials = CognitiveServicesCredentials(key)
            client = ComputerVisionClient(endpoint, credentials)
            
            # Convert PIL image to bytes
            import io
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Use Read API for handwriting
            read_response = client.read_in_stream(img_byte_arr, raw=True)
            read_operation_location = read_response.headers["Operation-Location"]
            operation_id = read_operation_location.split("/")[-1]
            
            # Wait for the operation to complete
            while True:
                read_result = client.get_read_result(operation_id)
                if read_result.status not in [OperationStatusCodes.running]:
                    break
                time.sleep(1)
                
            # Extract results
            text_lines = []
            bounding_boxes = []
            confidences = []
            
            if read_result.status == OperationStatusCodes.succeeded:
                for text_result in read_result.analyze_result.read_results:
                    for line in text_result.lines:
                        text_lines.append(line.text)
                        
                        # Get bounding box
                        bbox = line.bounding_box
                        if len(bbox) >= 8:  # Should have 8 coordinates (4 points x 2 coords)
                            x_coords = [bbox[i] for i in range(0, 8, 2)]
                            y_coords = [bbox[i] for i in range(1, 8, 2)]
                            box = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
                            bounding_boxes.append(box)
                        
                        # Azure doesn't provide confidence for Read API, assume high confidence
                        confidences.append(0.9)
            
            full_text = "\n".join(text_lines)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.9
            
            return OCRResult(
                text=full_text.strip(),
                confidence=avg_confidence,
                bounding_boxes=bounding_boxes,
                engine_used="azure_vision",
                language_detected="es"
            )
            
        except Exception as e:
            self.logger.error(f"Azure Vision processing failed: {e}")
            raise
    
    def _process_with_best_engine(self, image: Image.Image) -> OCRResult:
        """Process with the best available engine."""
        # Priority order: Google Vision -> Azure -> Tesseract
        engines_by_priority = [
            ("google_vision", self.available_engines.get('google_vision', False)),
            ("azure_vision", self.available_engines.get('azure_vision', False)),
            ("tesseract", self.available_engines.get('tesseract', False))
        ]
        
        for engine_name, available in engines_by_priority:
            if available:
                try:
                    return self._process_with_single_engine(image, engine_name)
                except Exception as e:
                    self.logger.warning(f"Engine {engine_name} failed: {e}")
                    continue
                    
        raise RuntimeError("No OCR engines available")
    
    def _process_with_ensemble(self, image: Image.Image) -> OCRResult:
        """Process with multiple engines and combine results."""
        config = self.config['ensemble']
        engines_to_use = config.get('engines_to_use', ['tesseract'])
        min_confidence = config.get('min_confidence', 0.7)
        
        results = []
        
        for engine_name in engines_to_use:
            if self.available_engines.get(engine_name, False):
                try:
                    result = self._process_with_single_engine(image, engine_name)
                    if result.confidence >= min_confidence:
                        results.append(result)
                except Exception as e:
                    self.logger.warning(f"Ensemble engine {engine_name} failed: {e}")
                    continue
        
        if not results:
            # Fallback to best available engine
            return self._process_with_best_engine(image)
        
        # Choose result with highest confidence
        best_result = max(results, key=lambda r: r.confidence)
        best_result.engine_used = f"ensemble({best_result.engine_used})"
        
        return best_result
    
    def validate_spanish_text(self, text: str) -> Tuple[bool, float]:
        """
        Validate if text appears to be Spanish.
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (is_spanish, confidence_score)
        """
        if not text.strip():
            return False, 0.0
            
        # Spanish character indicators
        spanish_chars = set("ñáéíóúÑÁÉÍÓÚ")
        spanish_words = {
            "nombre", "apellido", "fecha", "lugar", "dirección", "teléfono",
            "ciudad", "estado", "país", "edad", "sexo", "masculino", "femenino",
            "sí", "no", "si", "con", "sin", "para", "por", "del", "las", "los"
        }
        
        text_lower = text.lower()
        words = text_lower.split()
        
        # Count Spanish indicators
        spanish_char_count = sum(1 for char in text if char in spanish_chars)
        spanish_word_count = sum(1 for word in words if word in spanish_words)
        
        # Calculate confidence
        char_score = min(spanish_char_count / max(len(text), 1) * 10, 1.0)
        word_score = spanish_word_count / max(len(words), 1)
        
        confidence = (char_score + word_score) / 2
        is_spanish = confidence > 0.1 or any(word in spanish_words for word in words)
        
        return is_spanish, confidence