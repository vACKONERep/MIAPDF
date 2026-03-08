"""
Quick Start Guide

Step-by-step guide to get started with Spanish PDF OCR system.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


def check_system_requirements():
    """Check if system requirements are met."""
    print("🔍 Checking System Requirements...")
    
    requirements = {
        "Python": sys.version_info >= (3, 8),
        "pip": True,  # Assume pip is available if Python is
    }
    
    # Check Python version
    if requirements["Python"]:
        print(f"   ✅ Python {sys.version.split()[0]}")
    else:
        print(f"   ❌ Python version too old. Need 3.8+, have {sys.version.split()[0]}")
    
    # Check for Tesseract
    try:
        import subprocess
        subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
        print("   ✅ Tesseract OCR found")
        tesseract_ok = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ❌ Tesseract OCR not found")
        tesseract_ok = False
    
    # Check Python packages
    required_packages = [
        'pdf2image', 'PyMuPDF', 'pillow', 'opencv-python', 
        'pytesseract', 'pandas', 'numpy'
    ]
    
    print("\n🐍 Checking Python Packages...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    return {
        'python_ok': requirements["Python"],
        'tesseract_ok': tesseract_ok,
        'missing_packages': missing_packages
    }


def install_missing_packages(missing_packages):
    """Guide user through package installation."""
    if not missing_packages:
        print("✅ All required packages are installed!")
        return True
    
    print(f"\n📦 Installing Missing Packages...")
    print("Run the following command to install missing packages:")
    print()
    print(f"pip install {' '.join(missing_packages)}")
    print()
    
    response = input("Would you like to install them automatically? (y/N): ")
    if response.lower() in ['y', 'yes']:
        try:
            import subprocess
            cmd = [sys.executable, '-m', 'pip', 'install'] + missing_packages
            subprocess.run(cmd, check=True)
            print("✅ Packages installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    return False


def setup_directories():
    """Set up project directories."""
    print("\n📁 Setting Up Directories...")
    
    directories = [
        "data/input",
        "data/output", 
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {directory}")


def create_sample_files():
    """Create sample configuration and test files."""
    print("\n📄 Creating Sample Files...")
    
    # Create a simple test script
    test_script = """#!/usr/bin/env python3
'''
Simple test script to verify the system works.
'''

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main import SpanishPDFOCR
    
    print("🚀 Testing Spanish PDF OCR System...")
    
    # Initialize system
    ocr_system = SpanishPDFOCR()
    
    # Check status
    status = ocr_system.get_system_status()
    
    print(f"System Ready: {'✅' if status['system_ready'] else '❌'}")
    print(f"Available OCR Engines: {[k for k, v in status['ocr_engines'].items() if v]}")
    
    if status['system_ready']:
        print("✅ System is ready to process PDF files!")
    else:
        print("❌ System needs additional setup")
        
except Exception as e:
    print(f"❌ Error: {e}")
"""
    
    with open("test_system.py", 'w', encoding='utf-8') as f:
        f.write(test_script)
    print("   ✅ Created: test_system.py")
    
    # Create sample usage instructions
    readme_content = """# Quick Start Instructions

## 1. Test the System
```bash
python test_system.py
```

## 2. Process a Single PDF
```bash
python examples/process_single_pdf.py -i data/input/your_form.pdf -o data/output/results.csv
```

## 3. Batch Process Multiple PDFs  
```bash
python examples/batch_process.py -i data/input/ -o data/output/
```

## 4. View Advanced Examples
```bash
python examples/advanced_usage.py
```

## Next Steps

1. Place your PDF files in the `data/input/` directory
2. Run the processing scripts
3. Check results in `data/output/` directory
4. Customize `config/ocr_config.json` for your needs

## Troubleshooting

- If Tesseract is not found, install it from: https://github.com/tesseract-ocr/tesseract
- For Spanish language support, install: `tesseract-ocr-spa`
- Check logs in the `logs/` directory for detailed error information
"""
    
    with open("QUICKSTART.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("   ✅ Created: QUICKSTART.md")


def run_quick_test():
    """Run a quick system test."""
    print("\n🧪 Running Quick System Test...")
    
    try:
        from main import SpanishPDFOCR
        
        # Initialize system
        ocr_system = SpanishPDFOCR()
        
        # Check status
        status = ocr_system.get_system_status()
        
        print(f"   System Ready: {'✅' if status['system_ready'] else '❌'}")
        
        # Test OCR engines
        available_engines = [k for k, v in status['ocr_engines'].items() if v]
        print(f"   Available OCR Engines: {available_engines}")
        
        if not available_engines:
            print("   ⚠️  No OCR engines available. Install Tesseract or configure cloud APIs.")
            return False
        
        # Test text validation
        from ocr_engine import OCREngine
        ocr_engine = OCREngine()
        
        test_text = "José García"
        is_spanish, confidence = ocr_engine.validate_spanish_text(test_text)
        print(f"   Spanish text validation: {'✅' if is_spanish else '❌'} (confidence: {confidence:.2f})")
        
        print("   ✅ Quick test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Quick test failed: {e}")
        return False


def show_next_steps():
    """Show next steps to the user."""
    print("\n🎯 Next Steps:")
    print("1. Place your PDF files in the 'data/input/' directory")
    print("2. Run: python examples/process_single_pdf.py -i data/input/your_file.pdf -o data/output/results.csv")
    print("3. For multiple files: python examples/batch_process.py -i data/input/ -o data/output/")
    print("4. Check results in the 'data/output/' directory")
    print("5. Customize settings in 'config/ocr_config.json'")
    print("\n📖 Read QUICKSTART.md for detailed instructions")
    print("🆘 Run 'python tests/test_basic.py --manual' for diagnostics")


def main():
    """Main setup function."""
    print("🚀 Spanish PDF OCR - Quick Setup")
    print("=" * 40)
    
    # Check requirements
    requirements = check_system_requirements()
    
    if not requirements['python_ok']:
        print("\n❌ Python version too old. Please upgrade to Python 3.8+")
        return 1
    
    # Install missing packages
    if requirements['missing_packages']:
        success = install_missing_packages(requirements['missing_packages'])
        if not success:
            print("\n❌ Please install required packages manually:")
            print("pip install -r requirements.txt")
            return 1
    
    # Set up directories
    setup_directories()
    
    # Create sample files
    create_sample_files()
    
    # Run quick test
    test_success = run_quick_test()
    
    if test_success:
        print("\n✅ Setup completed successfully!")
        show_next_steps()
    else:
        print("\n⚠️  Setup completed with warnings.")
        print("Some OCR engines may not be available.")
        print("Install Tesseract for basic functionality:")
        print("- Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("- Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-spa")
        print("- macOS: brew install tesseract tesseract-lang")
        show_next_steps()
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)