#!/usr/bin/env python3
"""
Installation script for PDF to CSV workflow dependencies.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and show progress."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Install dependencies."""
    print("🔧 Installing PDF to CSV Workflow Dependencies")
    print("=" * 50)

    # Core dependencies (essential)
    core_packages = [
        "pytesseract",
        "pandas",
        "numpy",
        "pillow",
        "opencv-python",
        "PyMuPDF",
        "pdf2image"
    ]

    print("Installing core dependencies...")
    for package in core_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"Failed to install {package}. You may need to install it manually.")
            return 1

    # Optional dependencies (for full functionality)
    optional_packages = [
        "scikit-learn",
        "matplotlib",
        "pyspellchecker"
    ]

    print("\nInstalling optional dependencies...")
    for package in optional_packages:
        run_command(f"pip install {package}", f"Installing {package}")

    print("\n🎉 Installation completed!")
    print("You can now run: python simple_workflow.py")

    return 0

if __name__ == "__main__":
    sys.exit(main())