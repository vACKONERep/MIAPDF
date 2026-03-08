"""
Advanced Usage Examples

Demonstrates advanced features and customization options.
"""

import sys
import os
from pathlib import Path
import json

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import SpanishPDFOCR
from pdf_processor import PDFProcessor
from image_preprocessor import ImagePreprocessor
from ocr_engine import OCREngine
from form_extractor import FormExtractor
from csv_exporter import CSVExporter


def example_custom_configuration():
    """Example: Using custom configuration"""
    print("🛠️  Example: Custom Configuration")
    
    # Create custom configuration
    custom_config = {
        "ocr": {
            "ensemble": {
                "enabled": True,
                "engines_to_use": ["tesseract", "google_vision"],
                "min_confidence": 0.8
            }
        },
        "form_extraction": {
            "field_patterns": {
                "nombre": {
                    "keywords": ["nombre completo", "estudiante", "alumno"],
                    "position": "below_keyword",
                    "validation": "spanish_name",
                    "required": True
                },
                "email": {
                    "keywords": ["email", "correo", "e-mail"],
                    "position": "right_of_keyword", 
                    "validation": "email",
                    "required": False
                }
            }
        },
        "csv_export": {
            "columns": {
                "filename": "Archivo_PDF",
                "nombre": "Nombre_Estudiante",
                "email": "Correo_Electronico",
                "confidence": "Confianza_OCR"
            }
        }
    }
    
    # Save custom configuration
    config_path = "custom_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(custom_config, f, indent=2)
    
    # Use custom configuration
    ocr_system = SpanishPDFOCR(config_path=config_path)
    
    print(f"✅ Custom configuration created: {config_path}")
    return ocr_system


def example_component_usage():
    """Example: Using individual components"""
    print("\n🔧 Example: Individual Component Usage")
    
    # Initialize components individually
    pdf_processor = PDFProcessor(dpi=400, image_format="PNG")
    preprocessor = ImagePreprocessor()
    ocr_engine = OCREngine()
    form_extractor = FormExtractor()
    csv_exporter = CSVExporter()
    
    # Example processing pipeline (without actual file)
    print("📝 Component pipeline setup:")
    print("   1. PDFProcessor - Convert PDF to high-res images")
    print("   2. ImagePreprocessor - Clean and enhance images")
    print("   3. OCREngine - Extract text with multiple engines")
    print("   4. FormExtractor - Parse and validate form fields")
    print("   5. CSVExporter - Export to various formats")


def example_preprocessing_options():
    """Example: Different preprocessing configurations"""
    print("\n🖼️  Example: Image Preprocessing Options")
    
    preprocessor = ImagePreprocessor()
    
    # Different preprocessing configurations
    configs = [
        {
            "name": "Basic Cleaning",
            "settings": {
                "enhance_contrast": True,
                "denoise": True,
                "binarize": True,
                "deskew": False
            }
        },
        {
            "name": "Aggressive Enhancement",
            "settings": {
                "enhance_contrast": True,
                "denoise": True,
                "binarize": True,
                "deskew": True
            }
        },
        {
            "name": "Handwriting Optimized",
            "settings": {
                "enhance_contrast": True,
                "denoise": True,
                "binarize": True,
                "deskew": True
            }
        }
    ]
    
    print("📋 Available preprocessing configurations:")
    for config in configs:
        print(f"   - {config['name']}: {config['settings']}")


def example_ocr_engine_comparison():
    """Example: Compare different OCR engines"""
    print("\n🔍 Example: OCR Engine Comparison")
    
    ocr_engine = OCREngine()
    status = ocr_engine.available_engines
    
    print("🚀 OCR Engine Status:")
    engines = [
        ("Tesseract", "tesseract", "Free, open-source, good for printed text"),
        ("Google Vision", "google_vision", "Cloud-based, excellent for handwriting"),
        ("Azure Vision", "azure_vision", "Cloud-based, specialized Read API"),
        ("Ensemble", "ensemble", "Combines multiple engines for best results")
    ]
    
    for name, key, description in engines:
        available = "✅" if status.get(key, False) else "❌"
        print(f"   {available} {name}: {description}")


def example_validation_and_reporting():
    """Example: Custom validation and detailed reporting"""
    print("\n📊 Example: Validation and Reporting Features")
    
    csv_exporter = CSVExporter()
    
    # Available export formats
    formats = csv_exporter.get_supported_formats()
    print(f"📁 Supported export formats: {formats}")
    
    # Example report types
    reports = [
        "Standard CSV - Basic extracted data",
        "Validation Report - Field-by-field validation details",
        "Summary Statistics - Processing success rates and metrics",
        "Error Report - Failed extractions with reasons"
    ]
    
    print("📈 Available report types:")
    for report in reports:
        print(f"   - {report}")


def example_batch_with_filters():
    """Example: Batch processing with file filters"""
    print("\n🗂️  Example: Advanced Batch Processing")
    
    example_filters = """
    # Example file filtering and processing options:
    
    1. Process only files modified in last 7 days
    2. Skip files larger than 50MB
    3. Process files matching specific naming patterns
    4. Resume processing from last failure point
    5. Parallel processing with worker pools
    """
    
    print(example_filters)


def example_error_handling():
    """Example: Error handling and recovery"""
    print("\n🔧 Example: Error Handling Strategies")
    
    strategies = [
        "Retry with different OCR engines on failure",
        "Fallback to lower quality settings if processing fails",
        "Skip corrupted pages but continue with others",
        "Log detailed error information for debugging",
        "Generate partial results when some fields fail"
    ]
    
    print("🛡️  Error handling strategies:")
    for strategy in strategies:
        print(f"   - {strategy}")


def example_performance_optimization():
    """Example: Performance optimization techniques"""
    print("\n⚡ Example: Performance Optimization")
    
    tips = [
        "Use appropriate DPI (300-400) - higher isn't always better",
        "Enable parallel processing for batch operations",
        "Use cloud OCR engines for better accuracy on handwriting", 
        "Cache preprocessed images to avoid reprocessing",
        "Use ensemble mode only when accuracy is critical",
        "Optimize image preprocessing based on form quality",
        "Set timeouts to prevent hanging on problematic files"
    ]
    
    print("🚀 Performance optimization tips:")
    for tip in tips:
        print(f"   - {tip}")


def run_system_diagnostics():
    """Run comprehensive system diagnostics"""
    print("\n🏥 System Diagnostics")
    
    try:
        ocr_system = SpanishPDFOCR()
        status = ocr_system.get_system_status()
        
        print(f"🔍 System Analysis:")
        print(f"   - System Ready: {'✅' if status['system_ready'] else '❌'}")
        print(f"   - Configuration Loaded: {'✅' if status.get('configuration_loaded') else '❌'}")
        
        print(f"📦 Components Status:")
        for component, status_text in status.get('components', {}).items():
            icon = "✅" if status_text == "Ready" else "⚠️"
            print(f"   {icon} {component}: {status_text}")
        
        print(f"🔧 OCR Engines:")
        for engine, available in status.get('ocr_engines', {}).items():
            icon = "✅" if available else "❌"
            print(f"   {icon} {engine}")
        
        print(f"🌐 Supported Languages: {status.get('supported_languages', [])}")
        print(f"📁 Export Formats: {status.get('export_formats', [])}")
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")


def main():
    """Run all examples"""
    print("🎓 Spanish PDF OCR - Advanced Usage Examples")
    print("=" * 50)
    
    # Run examples
    example_custom_configuration()
    example_component_usage() 
    example_preprocessing_options()
    example_ocr_engine_comparison()
    example_validation_and_reporting()
    example_batch_with_filters()
    example_error_handling()
    example_performance_optimization()
    run_system_diagnostics()
    
    print("\n🎯 Examples completed!")
    print("\n💡 Next Steps:")
    print("   1. Try process_single_pdf.py with a sample PDF")
    print("   2. Use batch_process.py for multiple files")
    print("   3. Customize config/ocr_config.json for your needs")
    print("   4. Check the logs for detailed processing information")


if __name__ == "__main__":
    main()