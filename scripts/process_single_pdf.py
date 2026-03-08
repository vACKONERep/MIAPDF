"""
Single PDF Processing Example

Demonstrates how to process a single PDF file and extract form data to CSV.
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import SpanishPDFOCR


def main():
    parser = argparse.ArgumentParser(description='Process a single PDF form')
    parser.add_argument('--input', '-i', required=True, help='Path to input PDF file')
    parser.add_argument('--output', '-o', required=True, help='Path to output CSV file')
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--engine', '-e', default='auto', 
                       choices=['auto', 'tesseract', 'google_vision', 'azure_vision', 'ensemble'],
                       help='OCR engine to use (default: auto)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging if verbose
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize the OCR system
        print("🚀 Initializing Spanish PDF OCR system...")
        ocr_system = SpanishPDFOCR(config_path=args.config)
        
        # Check system status
        status = ocr_system.get_system_status()
        print(f"📊 System Status:")
        print(f"   - System Ready: {'✅' if status['system_ready'] else '❌'}")
        print(f"   - Available OCR Engines: {[k for k, v in status['ocr_engines'].items() if v]}")
        
        if not status["system_ready"]:
            print("❌ System not ready. Please check OCR engine installation.")
            return 1
        
        # Validate input file
        print(f"🔍 Validating input file: {args.input}")
        validation = ocr_system.validate_input_file(args.input)
        
        if not validation["valid"]:
            print(f"❌ Invalid input file: {validation['error']}")
            return 1
        
        print("✅ Input file is valid")
        if "info" in validation:
            info = validation["info"]
            print(f"   - Pages: {info.get('page_count', 'Unknown')}")
            print(f"   - File size: {info.get('file_size', 0) / (1024*1024):.1f} MB")
        
        if "recommendations" in validation:
            print("💡 Recommendations:")
            for rec in validation["recommendations"]:
                print(f"   - {rec}")
        
        # Create output directory if it doesn't exist
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Process the PDF
        print(f"🔄 Processing PDF with {args.engine} engine...")
        result = ocr_system.process_single_pdf(args.input, args.output, args.engine)
        
        # Display results
        if result["success"]:
            print("✅ Processing completed successfully!")
            print(f"📄 Output saved to: {args.output}")
            
            if "statistics" in result:
                stats = result["statistics"]
                print(f"📊 Processing Statistics:")
                print(f"   - Total pages: {stats.get('total_pages', 0)}")
                print(f"   - Successfully processed: {stats.get('successful_pages', 0)}")
                print(f"   - Failed pages: {stats.get('failed_pages', 0)}")
                print(f"   - Fields found: {stats.get('total_fields_found', 0)}")
                print(f"   - Fields validated: {stats.get('total_fields_validated', 0)}")
                print(f"   - Processing time: {stats.get('processing_time', 0):.1f} seconds")
                
                if stats.get('errors'):
                    print("⚠️  Errors encountered:")
                    for error in stats['errors']:
                        print(f"   - {error}")
            
            # Display sample of extracted data
            print(f"\n📋 Opening output file to display sample results...")
            try:
                import pandas as pd
                df = pd.read_csv(args.output)
                if not df.empty:
                    print(f"📈 Extracted {len(df)} records:")
                    print(df.head().to_string(index=False))
                else:
                    print("⚠️  No data extracted from the PDF")
            except Exception as e:
                print(f"⚠️  Could not display results: {e}")
        
        else:
            print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
            return 1
    
    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)