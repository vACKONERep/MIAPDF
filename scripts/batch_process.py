"""
Batch Processing Example

Demonstrates how to process multiple PDF files in a directory.
"""

import sys
import os
import argparse
from pathlib import Path
import json

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import SpanishPDFOCR


def main():
    parser = argparse.ArgumentParser(description='Batch process PDF forms in a directory')
    parser.add_argument('--input_dir', '-i', required=True, help='Directory containing PDF files')
    parser.add_argument('--output_dir', '-o', required=True, help='Directory for output CSV files')
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--engine', '-e', default='auto',
                       choices=['auto', 'tesseract', 'google_vision', 'azure_vision', 'ensemble'],
                       help='OCR engine to use (default: auto)')
    parser.add_argument('--combine', action='store_true', 
                       help='Create a combined CSV with all results')
    parser.add_argument('--reports', action='store_true',
                       help='Generate validation and summary reports')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
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
        
        # Check input directory
        input_path = Path(args.input_dir)
        if not input_path.exists():
            print(f"❌ Input directory not found: {args.input_dir}")
            return 1
        
        # Find PDF files
        pdf_files = list(input_path.glob("*.pdf"))
        if not pdf_files:
            print(f"❌ No PDF files found in {args.input_dir}")
            return 1
        
        print(f"📁 Found {len(pdf_files)} PDF files to process")
        for pdf_file in pdf_files:
            print(f"   - {pdf_file.name}")
        
        # Create output directory
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Start batch processing
        print(f"\n🔄 Starting batch processing with {args.engine} engine...")
        result = ocr_system.process_batch(args.input_dir, args.output_dir, args.engine)
        
        # Display results
        print(f"\n📊 Batch Processing Results:")
        print(f"   - Total files: {result.get('total_files', 0)}")
        print(f"   - Successfully processed: {result.get('successful_files', 0)}")
        print(f"   - Failed files: {result.get('failed_files', 0)}")
        print(f"   - Total processing time: {result.get('total_processing_time', 0):.1f} seconds")
        
        # Show processed files
        if result.get('files_processed'):
            print(f"\n✅ Successfully processed files:")
            for file_info in result['files_processed']:
                print(f"   - {file_info['filename']} → {Path(file_info['output_file']).name}")
                stats = file_info.get('statistics', {})
                if stats:
                    print(f"     Fields found: {stats.get('total_fields_found', 0)}, "
                          f"Validated: {stats.get('total_fields_validated', 0)}")
        
        # Show errors
        if result.get('errors'):
            print(f"\n❌ Failed files:")
            for error_info in result['errors']:
                print(f"   - {error_info['filename']}: {error_info['error']}")
        
        # Create combined CSV if requested
        if args.combine and result.get('successful_files', 0) > 0:
            print(f"\n📋 Creating combined CSV file...")
            try:
                combined_csv_path = output_path / "combined_results.csv"
                
                # Load and combine all individual CSV files
                import pandas as pd
                all_dataframes = []
                
                for file_info in result.get('files_processed', []):
                    try:
                        df = pd.read_csv(file_info['output_file'])
                        if not df.empty:
                            all_dataframes.append(df)
                    except Exception as e:
                        print(f"⚠️  Could not load {file_info['output_file']}: {e}")
                
                if all_dataframes:
                    combined_df = pd.concat(all_dataframes, ignore_index=True)
                    combined_df.to_csv(combined_csv_path, index=False, encoding='utf-8-sig')
                    print(f"✅ Combined CSV created: {combined_csv_path}")
                    print(f"   Total records: {len(combined_df)}")
                else:
                    print("⚠️  No valid data to combine")
                    
            except Exception as e:
                print(f"❌ Failed to create combined CSV: {e}")
        
        # Generate reports if requested
        if args.reports and result.get('successful_files', 0) > 0:
            print(f"\n📈 Generating reports...")
            try:
                # Create a summary report
                summary_data = {
                    "batch_summary": result,
                    "processing_date": str(pd.Timestamp.now()),
                    "configuration": {
                        "input_directory": str(input_path),
                        "output_directory": str(output_path),
                        "ocr_engine": args.engine
                    }
                }
                
                summary_path = output_path / "batch_report.json"
                with open(summary_path, 'w', encoding='utf-8') as f:
                    json.dump(summary_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Batch report created: {summary_path}")
                
                # Create processing summary CSV
                if result.get('files_processed'):
                    summary_records = []
                    for file_info in result['files_processed']:
                        stats = file_info.get('statistics', {})
                        summary_records.append({
                            'Archivo': file_info['filename'],
                            'Páginas_Totales': stats.get('total_pages', 0),
                            'Páginas_Exitosas': stats.get('successful_pages', 0),
                            'Páginas_Fallidas': stats.get('failed_pages', 0),
                            'Campos_Encontrados': stats.get('total_fields_found', 0),
                            'Campos_Validados': stats.get('total_fields_validated', 0),
                            'Tiempo_Procesamiento': f"{stats.get('processing_time', 0):.1f}s",
                            'Archivo_Salida': Path(file_info['output_file']).name
                        })
                    
                    summary_df = pd.DataFrame(summary_records)
                    summary_csv_path = output_path / "processing_summary.csv"
                    summary_df.to_csv(summary_csv_path, index=False, encoding='utf-8-sig')
                    print(f"✅ Processing summary CSV created: {summary_csv_path}")
                
            except Exception as e:
                print(f"❌ Failed to generate reports: {e}")
        
        # Final summary
        success_rate = (result.get('successful_files', 0) / result.get('total_files', 1)) * 100
        print(f"\n🎯 Batch Processing Summary:")
        print(f"   - Success rate: {success_rate:.1f}%")
        print(f"   - Output directory: {output_path}")
        print(f"   - Results available in individual CSV files")
        
        if args.combine:
            print(f"   - Combined results: combined_results.csv")
        if args.reports:
            print(f"   - Reports: batch_report.json, processing_summary.csv")
    
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


def show_usage_examples():
    """Show usage examples."""
    print("📖 Usage Examples:")
    print()
    print("1. Basic batch processing:")
    print("   python batch_process.py -i data/input/ -o data/output/")
    print()
    print("2. Batch processing with combined output:")
    print("   python batch_process.py -i data/input/ -o data/output/ --combine")
    print()
    print("3. Batch processing with reports:")
    print("   python batch_process.py -i data/input/ -o data/output/ --reports")
    print()
    print("4. Using specific OCR engine:")
    print("   python batch_process.py -i data/input/ -o data/output/ -e google_vision")
    print()
    print("5. Full processing with all options:")
    print("   python batch_process.py -i data/input/ -o data/output/ \\")
    print("      --combine --reports --verbose -e ensemble")


if __name__ == "__main__":
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h']):
        show_usage_examples()
        print()
    
    exit_code = main()
    sys.exit(exit_code)