"""
Form Field Extraction Module

Handles extraction and validation of specific form fields from OCR results.
Specialized for Spanish handwritten forms with name, number, and subject field processing.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from dataclasses import dataclass
from spellchecker import SpellChecker
import unicodedata

logger = logging.getLogger(__name__)


@dataclass
class FormField:
    """Structure for a form field."""
    name: str
    value: str
    confidence: float
    position: Tuple[int, int, int, int]  # x1, y1, x2, y2
    field_type: str
    validation_passed: bool = False


@dataclass
class ExtractedForm:
    """Structure for extracted form data."""
    fields: Dict[str, FormField]
    overall_confidence: float
    validation_score: float
    processing_notes: List[str]


class FormExtractor:
    """
    Extracts and validates form fields from OCR results.
    
    Specialized for Spanish forms with handwritten content.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize form extractor.
        
        Args:
            config: Configuration dictionary for field extraction
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.config = config or self._get_default_config()
        
        # Initialize Spanish spell checker
        try:
            self.spell_checker = SpellChecker(language='es')
            self.logger.info("Spanish spell checker initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Spanish spell checker: {e}")
            self.spell_checker = None
            
        # Load Spanish name patterns
        self._load_spanish_patterns()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration for form extraction."""
        return {
            "field_patterns": {
                "nombre": {
                    "keywords": ["nombre", "name", "apellido", "apellidos"],
                    "position": "below_keyword",
                    "validation": "spanish_name",
                    "required": True
                },
                "numero": {
                    "keywords": ["número", "numero", "telefono", "teléfono", "cedula", "cédula", "id"],
                    "position": "right_of_keyword",
                    "validation": "number",
                    "required": True
                },
                "materia": {
                    "keywords": ["materia", "subject", "asunto", "tema", "curso"],
                    "position": "below_keyword",
                    "validation": "spanish_text",
                    "required": True
                }
            },
            "validation": {
                "min_name_length": 2,
                "max_name_length": 50,
                "min_confidence": 0.6,
                "number_patterns": [
                    r'\d{7,12}',  # ID numbers
                    r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # Phone numbers
                    r'\d{1,4}[-.\s]?\d{3}[-.\s]?\d{3}'  # Other number formats
                ]
            },
            "text_processing": {
                "normalize_unicode": True,
                "remove_extra_spaces": True,
                "capitalize_names": True,
                "spell_check_names": True
            }
        }
    
    def _load_spanish_patterns(self):
        """Load Spanish language patterns for validation."""
        self.spanish_name_prefixes = {
            "de", "del", "de la", "von", "van", "mc", "mac", "o'", "san", "santa"
        }
        
        self.spanish_name_suffixes = {
            "jr", "sr", "hijo", "hija", "junior", "senior"
        }
        
        self.common_spanish_names = {
            # Common first names
            "josé", "juan", "antonio", "francisco", "manuel", "carlos", "luis", "miguel", "pedro", "pablo",
            "maría", "carmen", "ana", "isabel", "pilar", "dolores", "teresa", "rosa", "mercedes", "cristina",
            # Common surnames
            "garcía", "rodríguez", "gonzález", "fernández", "lópez", "martínez", "sánchez", "pérez", "gómez", "martín",
            "jiménez", "ruiz", "hernández", "díaz", "moreno", "muñoz", "álvarez", "romero", "alonso", "gutiérrez"
        }
        
        self.spanish_subjects = {
            "matemáticas", "español", "historia", "ciencias", "física", "química", "biología", "geografía",
            "literatura", "inglés", "francés", "educación", "arte", "música", "deportes", "informática",
            "filosofía", "economía", "derecho", "medicina", "ingeniería", "psicología", "sociología"
        }
    
    def extract_fields(self, ocr_result, image_shape: Optional[Tuple[int, int]] = None) -> ExtractedForm:
        """
        Extract form fields from OCR results.
        
        Args:
            ocr_result: OCR result object with text and bounding boxes
            image_shape: Original image dimensions (height, width)
            
        Returns:
            ExtractedForm with extracted and validated fields
        """
        self.logger.info("Starting form field extraction")
        
        text = ocr_result.text
        bounding_boxes = ocr_result.bounding_boxes
        
        # Parse text into lines and words
        lines = self._parse_text_structure(text, bounding_boxes)
        
        # Extract fields based on patterns
        extracted_fields = {}
        processing_notes = []
        
        for field_name, field_config in self.config["field_patterns"].items():
            try:
                field = self._extract_field(field_name, field_config, lines, text)
                if field:
                    extracted_fields[field_name] = field
                    self.logger.debug(f"Extracted field '{field_name}': {field.value}")
                else:
                    processing_notes.append(f"Field '{field_name}' not found")
                    
            except Exception as e:
                self.logger.error(f"Failed to extract field '{field_name}': {e}")
                processing_notes.append(f"Error extracting '{field_name}': {str(e)}")
        
        # Calculate overall confidence and validation score
        overall_confidence = self._calculate_overall_confidence(extracted_fields)
        validation_score = self._calculate_validation_score(extracted_fields)
        
        return ExtractedForm(
            fields=extracted_fields,
            overall_confidence=overall_confidence,
            validation_score=validation_score,
            processing_notes=processing_notes
        )
    
    def _parse_text_structure(self, text: str, bounding_boxes: List[Tuple]) -> List[Dict]:
        """Parse OCR text into structured lines with position information."""
        lines = text.split('\n')
        parsed_lines = []
        
        for i, line in enumerate(lines):
            if line.strip():
                # Estimate bounding box for line (simplified)
                bbox = bounding_boxes[min(i, len(bounding_boxes) - 1)] if bounding_boxes else (0, 0, 0, 0)
                
                parsed_lines.append({
                    'text': line.strip(),
                    'words': line.split(),
                    'line_number': i,
                    'bbox': bbox
                })
        
        return parsed_lines
    
    def _extract_field(self, field_name: str, field_config: Dict, lines: List[Dict], full_text: str) -> Optional[FormField]:
        """Extract a specific field using its configuration."""
        keywords = field_config.get('keywords', [])
        position = field_config.get('position', 'below_keyword')
        validation_type = field_config.get('validation', 'text')
        
        # Find keyword matches
        keyword_matches = []
        for line_info in lines:
            line_lower = line_info['text'].lower()
            for keyword in keywords:
                if keyword.lower() in line_lower:
                    keyword_matches.append((keyword, line_info))
                    break
        
        if not keyword_matches:
            return None
        
        # Use the first match
        matched_keyword, keyword_line = keyword_matches[0]
        
        # Extract field value based on position
        field_value = self._extract_value_by_position(
            position, matched_keyword, keyword_line, lines
        )
        
        if not field_value:
            return None
        
        # Clean and validate the extracted value
        cleaned_value = self._clean_field_value(field_value, validation_type)
        confidence = self._calculate_field_confidence(cleaned_value, validation_type)
        validation_passed = self._validate_field(cleaned_value, validation_type)
        
        return FormField(
            name=field_name,
            value=cleaned_value,
            confidence=confidence,
            position=keyword_line['bbox'],
            field_type=validation_type,
            validation_passed=validation_passed
        )
    
    def _extract_value_by_position(self, position: str, keyword: str, keyword_line: Dict, lines: List[Dict]) -> str:
        """Extract field value based on its position relative to the keyword."""
        if position == "below_keyword":
            # Look for value in the next line(s)
            keyword_line_num = keyword_line['line_number']
            for line_info in lines:
                if line_info['line_number'] > keyword_line_num:
                    # Check if this line contains the value
                    line_text = line_info['text'].strip()
                    if line_text and not any(kw.lower() in line_text.lower() 
                                           for kw in self.config["field_patterns"].keys()):
                        return line_text
                    
        elif position == "right_of_keyword":
            # Look for value in the same line after the keyword
            line_text = keyword_line['text']
            keyword_pos = line_text.lower().find(keyword.lower())
            if keyword_pos != -1:
                after_keyword = line_text[keyword_pos + len(keyword):].strip()
                # Remove common separators
                after_keyword = re.sub(r'^[:\-_\s]+', '', after_keyword)
                if after_keyword:
                    return after_keyword
                    
        elif position == "same_line":
            # Value is in the same line as keyword
            line_text = keyword_line['text']
            # Remove the keyword and extract remaining text
            cleaned_line = re.sub(rf'\b{re.escape(keyword)}\b', '', line_text, flags=re.IGNORECASE)
            cleaned_line = re.sub(r'^[:\-_\s]+', '', cleaned_line).strip()
            if cleaned_line:
                return cleaned_line
        
        return ""
    
    def _clean_field_value(self, value: str, field_type: str) -> str:
        """Clean and normalize field value."""
        if not value:
            return ""
        
        # Basic cleaning
        cleaned = value.strip()
        
        # Unicode normalization
        if self.config["text_processing"]["normalize_unicode"]:
            cleaned = unicodedata.normalize('NFKC', cleaned)
        
        # Remove extra spaces
        if self.config["text_processing"]["remove_extra_spaces"]:
            cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Field-specific cleaning
        if field_type == "spanish_name":
            cleaned = self._clean_spanish_name(cleaned)
        elif field_type == "number":
            cleaned = self._clean_number(cleaned)
        elif field_type == "spanish_text":
            cleaned = self._clean_spanish_text(cleaned)
        
        return cleaned
    
    def _clean_spanish_name(self, name: str) -> str:
        """Clean and format Spanish names."""
        if not name:
            return ""
        
        # Remove non-alphabetic characters except spaces, hyphens, apostrophes
        cleaned = re.sub(r"[^a-záéíóúñüA-ZÁÉÍÓÚÑÜ\s\-']", "", name)
        
        # Normalize spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Capitalize if configured
        if self.config["text_processing"]["capitalize_names"]:
            words = cleaned.split()
            capitalized_words = []
            
            for word in words:
                word_lower = word.lower()
                if word_lower in self.spanish_name_prefixes:
                    # Keep prefixes lowercase
                    capitalized_words.append(word_lower)
                else:
                    # Capitalize first letter
                    capitalized_words.append(word.capitalize())
            
            cleaned = " ".join(capitalized_words)
        
        # Spell check if enabled and available
        if (self.config["text_processing"]["spell_check_names"] and 
            self.spell_checker):
            cleaned = self._spell_check_name(cleaned)
        
        return cleaned
    
    def _clean_number(self, number: str) -> str:
        """Clean and format number fields."""
        if not number:
            return ""
        
        # Extract only digits and common separators
        cleaned = re.sub(r'[^\d\-.\s]', '', number)
        
        # Remove extra spaces
        cleaned = re.sub(r'\s+', '', cleaned)
        
        # Validate against number patterns
        validation_config = self.config["validation"]
        for pattern in validation_config["number_patterns"]:
            if re.match(pattern, cleaned):
                return cleaned
        
        # If no pattern matches, return digits only
        digits_only = re.sub(r'[^\d]', '', cleaned)
        return digits_only
    
    def _clean_spanish_text(self, text: str) -> str:
        """Clean Spanish text fields."""
        if not text:
            return ""
        
        # Basic cleaning while preserving Spanish characters
        cleaned = re.sub(r'[^\w\sáéíóúñüÁÉÍÓÚÑÜ]', ' ', text)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Capitalize first letter of each word
        words = cleaned.split()
        capitalized = [word.capitalize() for word in words]
        
        return " ".join(capitalized)
    
    def _spell_check_name(self, name: str) -> str:
        """Apply spell checking to Spanish names."""
        words = name.split()
        corrected_words = []
        
        for word in words:
            word_lower = word.lower()
            
            # Skip if it's a known prefix/suffix or common Spanish name
            if (word_lower in self.spanish_name_prefixes or 
                word_lower in self.spanish_name_suffixes or
                word_lower in self.common_spanish_names):
                corrected_words.append(word)
                continue
            
            # Check spelling
            if word_lower not in self.spell_checker:
                candidates = self.spell_checker.candidates(word_lower)
                if candidates:
                    # Choose the best candidate
                    best_candidate = min(candidates, 
                                       key=lambda x: self.spell_checker.distance(word_lower, x))
                    corrected_words.append(best_candidate.capitalize())
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)
        
        return " ".join(corrected_words)
    
    def _calculate_field_confidence(self, value: str, field_type: str) -> float:
        """Calculate confidence score for a field."""
        if not value:
            return 0.0
        
        base_confidence = 0.5
        
        if field_type == "spanish_name":
            # Check against known Spanish names
            words = value.lower().split()
            known_words = sum(1 for word in words if word in self.common_spanish_names)
            name_score = known_words / len(words) if words else 0
            base_confidence += name_score * 0.4
            
        elif field_type == "number":
            # Check if matches expected patterns
            validation_config = self.config["validation"]
            for pattern in validation_config["number_patterns"]:
                if re.match(pattern, value):
                    base_confidence += 0.3
                    break
                    
        elif field_type == "spanish_text":
            # Check for Spanish subject words
            words = value.lower().split()
            subject_words = sum(1 for word in words if word in self.spanish_subjects)
            if subject_words > 0:
                base_confidence += 0.3
        
        return min(base_confidence, 1.0)
    
    def _validate_field(self, value: str, field_type: str) -> bool:
        """Validate field value according to its type."""
        if not value:
            return False
        
        validation_config = self.config["validation"]
        
        if field_type == "spanish_name":
            # Check length
            if len(value) < validation_config["min_name_length"]:
                return False
            if len(value) > validation_config["max_name_length"]:
                return False
            
            # Check for valid characters
            if not re.match(r"^[a-záéíóúñüA-ZÁÉÍÓÚÑÜ\s\-']+$", value):
                return False
                
            return True
            
        elif field_type == "number":
            # Check against patterns
            for pattern in validation_config["number_patterns"]:
                if re.match(pattern, value):
                    return True
            return False
            
        elif field_type == "spanish_text":
            # Basic text validation
            return len(value) > 0 and len(value) <= 100
        
        return True
    
    def _calculate_overall_confidence(self, fields: Dict[str, FormField]) -> float:
        """Calculate overall confidence for all extracted fields."""
        if not fields:
            return 0.0
        
        confidences = [field.confidence for field in fields.values()]
        return sum(confidences) / len(confidences)
    
    def _calculate_validation_score(self, fields: Dict[str, FormField]) -> float:
        """Calculate validation score based on field validation results."""
        if not fields:
            return 0.0
        
        passed_validations = sum(1 for field in fields.values() if field.validation_passed)
        return passed_validations / len(fields)
    
    def get_missing_required_fields(self, extracted_form: ExtractedForm) -> List[str]:
        """Get list of required fields that are missing."""
        missing_fields = []
        
        for field_name, field_config in self.config["field_patterns"].items():
            if field_config.get("required", False):
                if field_name not in extracted_form.fields:
                    missing_fields.append(field_name)
                elif not extracted_form.fields[field_name].validation_passed:
                    missing_fields.append(f"{field_name} (validation failed)")
        
        return missing_fields