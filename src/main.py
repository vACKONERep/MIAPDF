"""
Main Application Module

Provides a unified interface for the Spanish PDF Forms OCR system.
Orchestrates the complete pipeline from PDF input to CSV output.
"""

import logging
import sys
import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import os
from datetime import datetime

from .pdf_processor import PDFProcessor
from .image_preprocessor import ImagePreprocessor
from .ocr_engine import OCREngine
from .form_extractor import FormExtractor
from .csv_exporter import CSVExporter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pdf_ocr.log')
    ]
)

logger = logging.getLogger(__name__)


class SpanishPDFOCR:
    """
    Main orchestrator for Spanish PDF forms OCR processing.
    
    Provides a unified interface for the complete pipeline:
    PDF → Image → OCR → Form Extraction → CSV Export
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Spanish PDF OCR system.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize components
        self._initialize_components()
        
        self.logger.info("Spanish PDF OCR system initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults."""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info(f"Configuration loaded from {config_path}")
                return config
            except Exception as e:
                self.logger.error(f"Failed to load config from {config_path}: {e}")
        
        # Try to load from default location
        default_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'ocr_config.json')
        if os.path.exists(default_config_path):
            try:
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info(f"Configuration loaded from {default_config_path}")
                return config
            except Exception as e:
                self.logger.warning(f"Failed to load default config: {e}")
        
        # Return minimal default configuration
        self.logger.info("Using minimal default configuration")
        return {"ocr": {}, "image_preprocessing": {}, "form_extraction": {}, "csv_export": {}}
    
    def _initialize_components(self):
        """Initialize all processing components."""
        try:
            # PDF Processor
            pdf_config = self.config.get("image_preprocessing", {}).get("pdf_conversion", {})
            self.pdf_processor = PDFProcessor(
                dpi=pdf_config.get("dpi", 300),
                image_format=pdf_config.get("image_format", "PNG")
            )
            
            # Image Preprocessor
            self.image_preprocessor = ImagePreprocessor()
            
            # OCR Engine
            ocr_config_path = None  # Will use the loaded config
            self.ocr_engine = OCREngine(self.config.get("ocr"))
            
            # Form Extractor
            form_config = self.config.get("form_extraction", {})
            self.form_extractor = FormExtractor(form_config)
            
            # CSV Exporter
            csv_config = self.config.get("csv_export", {})
            self.csv_exporter = CSVExporter(csv_config)
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def process_single_pdf(self, pdf_path: str, output_path: str, 
                          ocr_engine: str = "auto") -> Dict[str, Any]:
        """
        Process a single PDF file and export results to CSV.
        
        Args:
            pdf_path: Path to input PDF file
            output_path: Path for output CSV file
            ocr_engine: OCR engine to use ("auto", "tesseract", "google_vision", "azure_vision")
            
        Returns:
            Dictionary with processing results and statistics
        """
        self.logger.info(f"Processing single PDF: {pdf_path}")
        
        try:
            # Validate input
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            if not self.pdf_processor.validate_pdf(pdf_path):
                raise ValueError(f"Invalid or corrupted PDF file: {pdf_path}")
            
            # Get PDF info
            pdf_info = self.pdf_processor.get_pdf_info(pdf_path)
            self.logger.info(f"PDF has {pdf_info['page_count']} pages")
            
            # Convert PDF to images
            images = self.pdf_processor.convert_pdf_to_images(pdf_path)
            
            # Process each page
            extracted_forms = []
            processing_stats = {
                "total_pages": len(images),
                "successful_pages": 0,
                "failed_pages": 0,
                "total_fields_found": 0,
                "total_fields_validated": 0,
                "processing_time": 0,
                "errors": []
            }
            
            start_time = datetime.now()
            
            for i, image in enumerate(images):
                page_name = f"{Path(pdf_path).stem}_page_{i+1}"
                
                try:
                    self.logger.info(f"Processing page {i+1}/{len(images)}")
                    
                    # Preprocess image
                    preprocessing_config = self.config.get("image_preprocessing", {}).get("enhancement", {})
                    processed_image = self.image_preprocessor.preprocess_image(
                        image,
                        enhance_contrast=preprocessing_config.get("enhance_contrast", True),
                        denoise=preprocessing_config.get("denoise", True),
                        binarize=preprocessing_config.get("binarize", True),
                        deskew=preprocessing_config.get("deskew", True)
                    )
                    
                    # Apply additional enhancements if configured
                    if preprocessing_config.get("remove_lines", False):
                        processed_image = self.image_preprocessor.remove_lines(processed_image)
                    
                    if preprocessing_config.get("enhance_handwriting", True):
                        processed_image = self.image_preprocessor.enhance_handwriting(processed_image)
                    
                    if preprocessing_config.get("crop_to_content", True):
                        processed_image = self.image_preprocessor.crop_to_content(processed_image)
                    
                    # OCR processing
                    ocr_result = self.ocr_engine.process_image(processed_image, engine=ocr_engine)
                    
                    # Form field extraction
                    extracted_form = self.form_extractor.extract_fields(ocr_result)
                    
                    # Add to results
                    extracted_forms.append((extracted_form, page_name))
                    
                    # Update statistics
                    processing_stats["successful_pages"] += 1
                    processing_stats["total_fields_found"] += len(extracted_form.fields)
                    processing_stats["total_fields_validated"] += sum(
                        1 for field in extracted_form.fields.values() if field.validation_passed
                    )
                    
                    self.logger.info(f"Page {i+1} processed successfully - "
                                   f"Found {len(extracted_form.fields)} fields, "
                                   f"Confidence: {extracted_form.overall_confidence:.2%}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process page {i+1}: {e}")
                    processing_stats["failed_pages"] += 1
                    processing_stats["errors"].append(f"Page {i+1}: {str(e)}")
                    continue
            
            end_time = datetime.now()
            processing_stats["processing_time"] = (end_time - start_time).total_seconds()
            
            if not extracted_forms:
                raise ValueError("No pages could be processed successfully")
            
            # Export to CSV
            export_success = self.csv_exporter.export_multiple_forms(extracted_forms, output_path)
            
            if not export_success:
                raise ValueError("Failed to export results to CSV")
            
            self.logger.info(f"Successfully processed PDF and exported to {output_path}")
            
            return {
                "success": True,
                "output_file": output_path,
                "statistics": processing_stats,
                "extracted_forms_count": len(extracted_forms)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process PDF {pdf_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "statistics": processing_stats if 'processing_stats' in locals() else {}
            }
    
    def process_batch(self, input_dir: str, output_dir: str, 
                     ocr_engine: str = "auto") -> Dict[str, Any]:
        """
        Process multiple PDF files in batch.
        
        Args:
            input_dir: Directory containing PDF files
            output_dir: Directory for output CSV files
            ocr_engine: OCR engine to use
            
        Returns:
            Dictionary with batch processing results
        """
        self.logger.info(f"Starting batch processing: {input_dir} -> {output_dir}")
        
        try:
            # Find PDF files
            input_path = Path(input_dir)
            pdf_files = list(input_path.glob("*.pdf"))
            
            if not pdf_files:
                raise ValueError(f"No PDF files found in {input_dir}")
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Process each file
            batch_results = {
                "total_files": len(pdf_files),
                "successful_files": 0,
                "failed_files": 0,
                "total_processing_time": 0,
                "files_processed": [],
                "errors": []
            }
            
            all_extracted_forms = []
            start_time = datetime.now()
            
            for pdf_file in pdf_files:
                try:
                    self.logger.info(f"Processing {pdf_file.name}")
                    
                    # Generate output filename
                    output_csv = output_path / f"{pdf_file.stem}_extracted.csv"
                    
                    # Process file
                    result = self.process_single_pdf(
                        str(pdf_file), 
                        str(output_csv), 
                        ocr_engine
                    )
                    
                    if result["success"]:
                        batch_results["successful_files"] += 1
                        batch_results["files_processed"].append({
                            "filename": pdf_file.name,
                            "output_file": str(output_csv),
                            "statistics": result["statistics"]
                        })
                        
                        # Collect forms for combined output
                        if "extracted_forms_count" in result:
                            # Load the extracted data for combined export
                            # (This is a simplified approach - in practice, you might store forms differently)
                            pass
                            
                    else:
                        batch_results["failed_files"] += 1
                        batch_results["errors"].append({
                            "filename": pdf_file.name,
                            "error": result.get("error", "Unknown error")
                        })
                        
                except Exception as e:
                    self.logger.error(f"Failed to process {pdf_file.name}: {e}")
                    batch_results["failed_files"] += 1
                    batch_results["errors"].append({
                        "filename": pdf_file.name,
                        "error": str(e)
                    })
            
            end_time = datetime.now()
            batch_results["total_processing_time"] = (end_time - start_time).total_seconds()
            
            # Create batch summary report
            summary_path = output_path / "batch_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(batch_results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Batch processing complete. "
                           f"Successful: {batch_results['successful_files']}, "
                           f"Failed: {batch_results['failed_files']}")
            
            return batch_results
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_files": 0,
                "successful_files": 0,
                "failed_files": 0
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status and available capabilities.
        
        Returns:
            Dictionary with system information
        """
        try:
            # Check OCR engine availability
            ocr_status = self.ocr_engine.available_engines
            
            # Check PDF processor
            pdf_status = True
            try:
                self.pdf_processor.get_pdf_info.__doc__  # Simple check
            except:
                pdf_status = False
            
            # System information
            status = {
                "system_ready": all(ocr_status.values()) or any(ocr_status.values()),
                "ocr_engines": ocr_status,
                "pdf_processor": pdf_status,
                "components": {
                    "pdf_processor": "Ready",
                    "image_preprocessor": "Ready",
                    "ocr_engine": "Ready" if any(ocr_status.values()) else "Limited",
                    "form_extractor": "Ready",
                    "csv_exporter": "Ready"
                },
                "configuration_loaded": bool(self.config),
                "supported_languages": ["es", "spa"],
                "supported_formats": ["PDF"],
                "export_formats": ["CSV", "Excel", "TSV", "JSON"]
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {
                "system_ready": False,
                "error": str(e)
            }
    
    def validate_input_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate an input PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with validation results
        """
        try:
            if not os.path.exists(file_path):
                return {"valid": False, "error": "File not found"}
            
            if not file_path.lower().endswith('.pdf'):
                return {"valid": False, "error": "Not a PDF file"}
            
            if not self.pdf_processor.validate_pdf(file_path):
                return {"valid": False, "error": "Invalid or corrupted PDF"}
            
            # Get PDF information
            pdf_info = self.pdf_processor.get_pdf_info(file_path)
            
            return {
                "valid": True,
                "info": pdf_info,
                "recommendations": self._get_processing_recommendations(pdf_info)
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def _get_processing_recommendations(self, pdf_info: Dict) -> List[str]:
        """Generate processing recommendations based on PDF characteristics."""
        recommendations = []
        
        page_count = pdf_info.get('page_count', 0)
        file_size = pdf_info.get('file_size', 0)
        
        if page_count > 10:
            recommendations.append("Large document - consider batch processing")
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            recommendations.append("Large file size - may require additional processing time")
        
        recommendations.append("Use high DPI (300+) for better OCR accuracy")
        recommendations.append("Enable cloud OCR engines for handwritten text")
        
        return recommendations


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Spanish PDF Forms OCR System")
    parser.add_argument("--input", "-i", required=True, help="Input PDF file or directory")
    parser.add_argument("--output", "-o", required=True, help="Output CSV file or directory")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--engine", "-e", default="auto", 
                       choices=["auto", "tesseract", "google_vision", "azure_vision", "ensemble"],
                       help="OCR engine to use")
    parser.add_argument("--batch", "-b", action="store_true", help="Process directory in batch mode")
    parser.add_argument("--batch-simple", action="store_true", help="Use simple batch processor for handwritten PDFs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize system
    ocr_system = SpanishPDFOCR(config_path=args.config)
    
    # Check system status
    status = ocr_system.get_system_status()
    if not status["system_ready"]:
        print("❌ System not ready. Check OCR engine installation.")
        return 1
    
    print("✅ System ready")
    print(f"Available OCR engines: {[k for k, v in status['ocr_engines'].items() if v]}")
    
    # Process files
    if args.batch_simple:
        print(f"🔄 Starting simple batch processing...")
        from .batch_pdf_processor import batch_process_pdfs
        batch_process_pdfs(args.input, args.output)
        print("✅ Simple batch processing completed")
    elif args.batch or os.path.isdir(args.input):
        print(f"🔄 Starting batch processing...")
        result = ocr_system.process_batch(args.input, args.output, args.engine)
    else:
        print(f"🔄 Processing single file...")
        result = ocr_system.process_single_pdf(args.input, args.output, args.engine)
    
    # Print results
    if result.get("success", True):
        print("✅ Processing completed successfully")
        if "statistics" in result:
            stats = result["statistics"]
            print(f"   📊 Statistics:")
            print(f"      - Pages processed: {stats.get('successful_pages', 0)}")
            print(f"      - Fields found: {stats.get('total_fields_found', 0)}")
            print(f"      - Fields validated: {stats.get('total_fields_validated', 0)}")
            print(f"      - Processing time: {stats.get('processing_time', 0):.1f}s")
    else:
        print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())