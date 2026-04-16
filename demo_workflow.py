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

    
