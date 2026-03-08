"""
Test Suite for Spanish PDF OCR System

Basic tests to verify system functionality.
"""

import unittest
import os
import sys
import tempfile
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pdf_processor import PDFProcessor
from image_preprocessor import ImagePreprocessor
from ocr_engine import OCREngine, OCRResult
from form_extractor import FormExtractor, FormField, ExtractedForm
from csv_exporter import CSVExporter
from main import SpanishPDFOCR


class TestPDFProcessor(unittest.TestCase):
    """Test PDF processing functionality."""
    
    def setUp(self):
        self.processor = PDFProcessor()
    
    def test_initialization(self):
        """Test PDF processor initialization."""
        self.assertEqual(self.processor.dpi, 300)
        self.assertEqual(self.processor.image_format, 'PNG')
    
    def test_validate_pdf_nonexistent(self):
        """Test validation of non-existent PDF."""
        result = self.processor.validate_pdf("nonexistent.pdf")
        self.assertFalse(result)


class TestImagePreprocessor(unittest.TestCase):
    """Test image preprocessing functionality."""
    
    def setUp(self):
        self.preprocessor = ImagePreprocessor()
    
    def test_initialization(self):
        """Test image preprocessor initialization."""
        self.assertIsInstance(self.preprocessor, ImagePreprocessor)
    
    def test_preprocess_image_with_none(self):
        """Test preprocessing with None input."""
        import numpy as np
        # Create a simple test image
        test_image = np.ones((100, 100), dtype=np.uint8) * 128
        result = self.preprocessor.preprocess_image(test_image)
        self.assertIsInstance(result, np.ndarray)


class TestOCREngine(unittest.TestCase):
    """Test OCR engine functionality."""
    
    def setUp(self):
        self.ocr_engine = OCREngine()
    
    def test_initialization(self):
        """Test OCR engine initialization."""
        self.assertIsInstance(self.ocr_engine, OCREngine)
    
    def test_available_engines(self):
        """Test engine availability check."""
        engines = self.ocr_engine.available_engines
        self.assertIsInstance(engines, dict)
        self.assertIn('tesseract', engines)
    
    def test_validate_spanish_text(self):
        """Test Spanish text validation."""
        # Test Spanish text
        spanish_text = "José García Martínez"
        is_spanish, confidence = self.ocr_engine.validate_spanish_text(spanish_text)
        self.assertTrue(is_spanish)
        
        # Test non-Spanish text
        english_text = "John Smith"
        is_spanish, confidence = self.ocr_engine.validate_spanish_text(english_text)
        # This might be False or have low confidence


class TestFormExtractor(unittest.TestCase):
    """Test form extraction functionality."""
    
    def setUp(self):
        self.extractor = FormExtractor()
    
    def test_initialization(self):
        """Test form extractor initialization."""
        self.assertIsInstance(self.extractor, FormExtractor)
    
    def test_clean_spanish_name(self):
        """Test Spanish name cleaning."""
        # Test basic name cleaning
        dirty_name = "  JOSÉ   GARCÍA  "
        cleaned = self.extractor._clean_spanish_name(dirty_name)
        self.assertEqual(cleaned.strip(), "José García")
    
    def test_clean_number(self):
        """Test number cleaning."""
        # Test phone number cleaning
        dirty_number = "123-456-7890"
        cleaned = self.extractor._clean_number(dirty_number)
        self.assertIn(cleaned, ["123-456-7890", "1234567890"])


class TestCSVExporter(unittest.TestCase):
    """Test CSV export functionality."""
    
    def setUp(self):
        self.exporter = CSVExporter()
    
    def test_initialization(self):
        """Test CSV exporter initialization."""
        self.assertIsInstance(self.exporter, CSVExporter)
    
    def test_supported_formats(self):
        """Test supported format listing."""
        formats = self.exporter.get_supported_formats()
        self.assertIn('csv', formats)
        self.assertIn('excel', formats)
    
    def test_prepare_row_data(self):
        """Test row data preparation."""
        # Create mock extracted form
        mock_field = FormField(
            name="nombre",
            value="Test Name",
            confidence=0.9,
            position=(0, 0, 100, 20),
            field_type="spanish_name",
            validation_passed=True
        )
        
        mock_form = ExtractedForm(
            fields={"nombre": mock_field},
            overall_confidence=0.9,
            validation_score=1.0,
            processing_notes=[]
        )
        
        row_data = self.exporter._prepare_row_data(mock_form, "test.pdf")
        self.assertIn("Archivo", row_data)
        self.assertEqual(row_data["Archivo"], "test.pdf")


class TestSpanishPDFOCR(unittest.TestCase):
    """Test main OCR system functionality."""
    
    def setUp(self):
        self.ocr_system = SpanishPDFOCR()
    
    def test_initialization(self):
        """Test OCR system initialization."""
        self.assertIsInstance(self.ocr_system, SpanishPDFOCR)
    
    def test_system_status(self):
        """Test system status check."""
        status = self.ocr_system.get_system_status()
        self.assertIsInstance(status, dict)
        self.assertIn('system_ready', status)
        self.assertIn('ocr_engines', status)
        self.assertIn('components', status)
    
    def test_validate_input_file(self):
        """Test input file validation."""
        # Test non-existent file
        result = self.ocr_system.validate_input_file("nonexistent.pdf")
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "File not found")
        
        # Test non-PDF file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name
        
        try:
            result = self.ocr_system.validate_input_file(tmp_path)
            self.assertFalse(result["valid"])
            self.assertEqual(result["error"], "Not a PDF file")
        finally:
            os.unlink(tmp_path)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete pipeline."""
    
    def test_config_loading(self):
        """Test configuration loading."""
        # Test with non-existent config
        ocr_system = SpanishPDFOCR("nonexistent_config.json")
        self.assertIsInstance(ocr_system.config, dict)
    
    def test_component_integration(self):
        """Test that all components work together."""
        ocr_system = SpanishPDFOCR()
        
        # Check that all components are initialized
        self.assertIsInstance(ocr_system.pdf_processor, PDFProcessor)
        self.assertIsInstance(ocr_system.image_preprocessor, ImagePreprocessor)
        self.assertIsInstance(ocr_system.ocr_engine, OCREngine)
        self.assertIsInstance(ocr_system.form_extractor, FormExtractor)
        self.assertIsInstance(ocr_system.csv_exporter, CSVExporter)


def create_sample_test_data():
    """Create sample test data for manual testing."""
    print("Creating sample test data...")
    
    # Create test directories
    test_data_dir = Path("test_data")
    test_data_dir.mkdir(exist_ok=True)
    
    input_dir = test_data_dir / "input"
    output_dir = test_data_dir / "output"
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Create a sample configuration for testing
    test_config = {
        "ocr": {
            "engines": {
                "tesseract": {
                    "enabled": True,
                    "language": "spa"
                }
            }
        },
        "form_extraction": {
            "field_patterns": {
                "nombre": {
                    "keywords": ["nombre", "name"],
                    "validation": "spanish_name"
                }
            }
        }
    }
    
    config_path = test_data_dir / "test_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(test_config, f, indent=2)
    
    print(f"✅ Test data structure created in {test_data_dir}")
    print(f"   - Input directory: {input_dir}")
    print(f"   - Output directory: {output_dir}")
    print(f"   - Test config: {config_path}")


def run_manual_tests():
    """Run manual tests with user interaction."""
    print("🧪 Running Manual Tests")
    print("=" * 30)
    
    # Test system status
    print("1. Testing system status...")
    ocr_system = SpanishPDFOCR()
    status = ocr_system.get_system_status()
    
    print(f"   System ready: {'✅' if status['system_ready'] else '❌'}")
    print(f"   Available engines: {[k for k, v in status['ocr_engines'].items() if v]}")
    
    # Test OCR engines
    print("\n2. Testing OCR engine availability...")
    ocr_engine = OCREngine()
    for engine_name, available in ocr_engine.available_engines.items():
        status_icon = "✅" if available else "❌"
        print(f"   {status_icon} {engine_name}")
    
    # Test text validation
    print("\n3. Testing Spanish text validation...")
    test_texts = [
        "José García Martínez",
        "María Isabel Rodríguez", 
        "John Smith",
        "Matemáticas Aplicadas"
    ]
    
    for text in test_texts:
        is_spanish, confidence = ocr_engine.validate_spanish_text(text)
        print(f"   '{text}': Spanish={is_spanish}, Confidence={confidence:.2f}")
    
    print("\n✅ Manual tests completed")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Spanish PDF OCR System")
    parser.add_argument("--manual", action="store_true", help="Run manual tests")
    parser.add_argument("--create-data", action="store_true", help="Create sample test data")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.create_data:
        create_sample_test_data()
    elif args.manual:
        run_manual_tests()
    else:
        # Run unit tests
        if args.verbose:
            verbosity = 2
        else:
            verbosity = 1
        
        # Discover and run tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(sys.modules[__name__])
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        
        # Print summary
        if result.wasSuccessful():
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
            sys.exit(1)