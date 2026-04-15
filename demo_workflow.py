#!/usr/bin/env python3
"""
Simple PDF to CSV Demo Script

This script demonstrates the PDF to CSV workflow using mock data.
No OCR or complex processing required.
"""

import sys
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main demo function."""
    print("🚀 Starting Simple PDF to CSV Demo")
    print("=" * 50)

    # Define directories
    input_dir = "data/input"
    output_dir = "data/output"

    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        print("   Please create the directory and add PDF files to process.")
        return 1

    # Find PDF files
    input_path = Path(input_dir)
    pdf_files = list(input_path.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ No PDF files found in {input_dir}")
        print("   Please add PDF files to the input directory.")
        return 1

    print(f"📁 Found {len(pdf_files)} PDF file(s) to process:")
    for pdf_file in pdf_files:
        print(f"   - {pdf_file.name}")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Mock data for demo - each PDF gets specific demo data
    demo_data = [
        {
            'Archivo': 'Cirugia General',
            'Nombre': '',  # Will be anonymized
            'Semestre': 'Noveno',
            'Materia': 'Cirugia General',
            'Nota': '8',
            'Fecha Procesamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'Archivo': 'CIRUGIA',
            'Nombre': '',  # Will be anonymized
            'Semestre': 'Noveno',
            'Materia': 'Cirugia',
            'Nota': 10,
            'Fecha Procesamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'Archivo': 'CIRUGÍA VASCULAR',
            'Nombre': '',  # Will be anonymized
            'Semestre': 'Decimo',
            'Materia': 'Cirugía Vascular',
            'Nota': 10,
            'Fecha Procesamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'Archivo': 'GINECOLOGIA',
            'Nombre': '',  # Will be anonymized
            'Semestre': 'Noveno',
            'Materia': 'Ginecologia',
            'Nota': 10,
            'Fecha Procesamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'Archivo': 'Obstetricia',
            'Nombre': '',  # Will be anonymized
            'Semestre': 'Decimo',
            'Materia': 'Obstetricia',
            'Nota': 10,
            'Fecha Procesamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'Archivo': 'PEDIATRIA',
            'Nombre': '',  # Will be anonymized
            'Semestre': 'Octavo',
            'Materia': 'Pediatria',
            'Nota': 10,
            'Fecha Procesamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'Archivo': 'TRAUMATOLOGIA',
            'Nombre': '',  # Will be anonymized
            'Semestre': 'Decimo',
            'Materia': 'Traumatologia',
            'Nota': 9,
            'Fecha Procesamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'Archivo': 'UROLOGIA (1)',
            'Nombre': '',  # Will be anonymized
            'Semestre': 'Decimo',
            'Materia': 'Urologia',
            'Nota': 10,
            'Fecha Procesamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

    print("
🔄 Processing PDFs with demo data..."    all_data = demo_data

    # Create DataFrame
    df = pd.DataFrame(all_data)

    # Anonymize names (always assign sequential student numbers)
    df_anon = df.copy()
    num_records = len(df_anon)
    student_ids = [f"Estudiante {i+1}" for i in range(num_records)]
    df_anon['Nombre'] = student_ids

    # Save anonymized CSV
    anonymized_csv = output_path / "demo_output.csv"
    df_anon.to_csv(anonymized_csv, index=False, encoding='utf-8-sig')
    print(f"✅ Demo CSV saved: {anonymized_csv}")

    # Show summary
    print("\n📊 Summary:")
    print(f"   - Total students processed: {len(df_anon)}")
    print(f"   - Files processed: {len(pdf_files)}")
    print("   - All student names anonymized as 'Estudiante 1', 'Estudiante 2', etc.")

    print("\n📄 Output file:")
    print(f"   - Anonymized CSV: {anonymized_csv}")
    print("   - Format: Archivo,Nombre,Semestre,Materia,Nota,Fecha Procesamiento")

    print("\n🎉 Demo completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())