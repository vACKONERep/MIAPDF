# Spanish PDF Forms OCR Project

A comprehensive Python solution for processing handwritten Spanish PDF forms, extracting data to CSV format using advanced OCR techniques, and predicting student grades with machine learning models.

## 🌟 Features

- **Multi-engine OCR**: Supports Tesseract, Google Vision API, and Azure Computer Vision
- **Spanish Language Optimized**: Specialized for Spanish handwritten text recognition
- **Advanced Image Preprocessing**: Noise reduction, contrast enhancement, deskewing, and binarization
- **Intelligent Form Extraction**: Automated detection and extraction of names, numbers, and subjects
- **Flexible CSV Export**: Multiple export formats with validation reporting
- **High Accuracy**: Ensemble OCR approach for maximum accuracy
- **Production Ready**: Comprehensive error handling, logging, and validation
- **Batch Processing**: Process multiple PDFs at once with simple or advanced modes
- **Grade Prediction**: Machine learning models (Random Forest, XGBoost) for predicting student grades and risk assessment

## 📋 Requirements

### System Dependencies
- **Tesseract OCR** with Spanish language pack
- **Poppler** (for PDF to image conversion)
- **Python 3.8+**

### Installation

1. **Install System Dependencies**:
   
   **Windows**:
   ```bash
   # Install Tesseract
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   # Add to PATH
   
   # Install Poppler
   # Download from: https://github.com/oschwartz10612/poppler-windows/releases/
   # Add to PATH
   ```
   
   **Ubuntu/Debian**:
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr tesseract-ocr-spa poppler-utils
   ```
   
   **macOS**:
   ```bash
   brew install tesseract tesseract-lang poppler
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: For machine learning predictions, additional libraries are included:
   - scikit-learn, xgboost for ML models
   - matplotlib, ipywidgets for interactive dashboards

   Nota: EasyOCR requiere PyTorch. Si hay problemas, instalar manualmente:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   pip install easyocr
   ```

   **Nota**: El script usa PyMuPDF para convertir PDFs a imágenes, pero el procesador por lotes simple usa pdf2image que requiere Poppler.

3. **Optional Cloud OCR Setup**:
   
   **Google Vision API**:
   - Create a Google Cloud Project
   - Enable Vision API
   - Download service account key
   - Set environment variable: `GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json`
   
   **Azure Computer Vision**:
   - Create Azure Computer Vision resource
   - Set environment variables:
     - `AZURE_COMPUTER_VISION_KEY=your_key`
     - `AZURE_COMPUTER_VISION_ENDPOINT=your_endpoint`

## 🚀 Quick Start

### Basic Usage

```python
from src import PDFProcessor, ImagePreprocessor, OCREngine, FormExtractor, CSVExporter

# Initialize components
pdf_processor = PDFProcessor(dpi=300)
preprocessor = ImagePreprocessor()
ocr_engine = OCREngine()
form_extractor = FormExtractor()
csv_exporter = CSVExporter()

# Process a single PDF
pdf_path = "data/input/form.pdf"

# Convert PDF to images
images = pdf_processor.convert_pdf_to_images(pdf_path)

# Process each page
extracted_forms = []
for i, image in enumerate(images):
    # Preprocess image
    processed_image = preprocessor.preprocess_image(image)
    
    # Extract text with OCR
    ocr_result = ocr_engine.process_image(processed_image, engine="auto")
    
    # Extract form fields
    extracted_form = form_extractor.extract_fields(ocr_result)
    
    extracted_forms.append((extracted_form, f"form_page_{i+1}.pdf"))

# Export to CSV
csv_exporter.export_multiple_forms(extracted_forms, "data/output/extracted_data.csv")
```

### Quick Prediction Example

```python
# After processing PDFs to CSV, run predictions
# Run in Jupyter or interactive environment
python scripts/prediction_rf_regressor.py
```

### Command Line Usage (see scripts/)

```bash
# Single PDF processing
python scripts/process_single_pdf.py --input data/input/form.pdf --output data/output/results.csv

# Advanced batch processing
python scripts/batch_process.py --input_dir data/input/ --output_dir data/output/

# Simple batch processing for handwritten PDFs (NEW)
python -m src.main --input data/input/ --output data/output/batch_extracted_data.csv --batch-simple

# Handwritten PDF processing
python scripts/ejemplo_handwriting.py
```

## ✏️ Handwritten PDF Processing

Para procesar PDFs con handwriting en español, enfocado en páginas 8 y 9, extrayendo campos específicos:

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

**Importante para Windows**: Instalar Poppler manualmente:
1. Descargar poppler desde: https://github.com/oschwartz10612/poppler-windows/releases/
2. Elegir la versión para Windows (ej. poppler-23.11.0-1.zip)
3. Extraer el contenido en una carpeta (ej. C:\poppler)
4. Agregar la carpeta `bin` al PATH del sistema:
   - Buscar "Variables de entorno" en Windows
   - Editar "Path" en Variables del sistema
   - Agregar `C:\poppler\bin`
5. Reiniciar la terminal o VS Code

Nota: EasyOCR requiere PyTorch. Si hay problemas, instalar manualmente:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install easyocr
```

### Uso desde Línea de Comandos

```bash
python process_handwritten_pdf.py ruta/al/archivo.pdf salida.csv
```

### Campos Extraídos

- **Nombre del estudiante**: Texto manuscrito cercano al label
- **Semestre**: Texto manuscrito cercano
- **Hospital**: Texto manuscrito cercano
- **Rotacion**: Texto manuscrito cercano
- **Nota Total**: Número manuscrito en página 9 (cerca de "Nota Total")

### Salida CSV

Columnas:
- `page_number`: Número de página (8 o 9)
- `field_name`: Nombre del campo
- `extracted_text`: Texto extraído y corregido
- `confidence`: Confianza del OCR (0-1)
- `nota_total`: Número extraído de página 9 (solo presente en filas de página 9)

### Manejo de Variaciones

- **Diferentes handwritings**: El script usa EasyOCR optimizado para handwriting y aplica correcciones básicas.
- **Posiciones ligeramente distintas**: Busca texto cercano (derecha/abajo) al label usando bounding boxes.
- **Errores comunes**: Corrige caracteres mal reconocidos (ej. 'a' por 'o').
- **PDFs con menos páginas**: Error si menos de 9 páginas.

### Limitaciones

- Asume labels impresos y handwriting adyacente.
- Funciona localmente sin internet después de instalar dependencias.
- Optimizado para español.

## 🔄 Batch Processing for Multiple PDFs

For processing multiple handwritten PDFs at once:

```bash
# Using the simple batch processor
python -m src.main --input data/input/ --output data/output/batch_extracted_data.csv --batch-simple

# Or run directly
python src/batch_pdf_processor.py
```

This will process all PDFs in `data/input/`, extract data from the last 2 pages of each PDF, and save to a single CSV file.

## 📊 Grade Prediction and Risk Assessment

The project includes machine learning models for predicting student grades and assessing performance risk based on historical data.

### Available Prediction Scripts:
- `scripts/prediction_rf_regressor.py` - Random Forest regression for grade prediction
- `scripts/prediction_xgb_regressor.py` - XGBoost regression for grade prediction  
- `scripts/prediction_rf_classifier.py` - Random Forest classification for risk assessment
- `scripts/prediction_xgb_classifier.py` - XGBoost classification for risk assessment

### Usage:
```bash
# Run in Jupyter notebook or Python environment with GUI support
python scripts/prediction_rf_regressor.py
```

These scripts provide interactive dashboards for:
- Selecting students and subjects
- Viewing historical performance charts
- Predicting future grades with confidence scores
- Assessing performance risk categories (Low <6, Medium 6-8, High ≥8)

### Requirements for Prediction:
- Processed CSV data from batch processing
- Interactive Python environment (Jupyter, VS Code with Python extension)
- Libraries: scikit-learn, xgboost, matplotlib, ipywidgets

## 📁 Project Structure

```
PDFintoCSV/
├── src/                          # Main source code
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Main orchestrator and CLI
│   ├── batch_pdf_processor.py   # Simple batch PDF processing
│   ├── pdf_processor.py         # PDF to image conversion
│   ├── image_preprocessor.py    # Image enhancement and preprocessing
│   ├── ocr_engine.py            # Multi-engine OCR processing
│   ├── form_extractor.py        # Form field extraction and validation
│   └── csv_exporter.py          # CSV export with multiple formats
├── config/
│   └── ocr_config.json          # Configuration settings
├── data/
│   ├── input/                   # Input PDF files
│   └── output/                  # Generated CSV files and reports
├── scripts/                    # Usage scripts
│   ├── prediction_rf_regressor.py    # Random Forest grade prediction
│   ├── prediction_xgb_regressor.py   # XGBoost grade prediction
│   ├── prediction_rf_classifier.py   # Random Forest risk classification
│   ├── prediction_xgb_classifier.py  # XGBoost risk classification
│   ├── process_single_pdf.py    # Single PDF processing example
│   ├── batch_process.py         # Advanced batch processing example
│   └── ...
├── tests/                       # Unit tests
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## ⚙️ Configuration

The system is highly configurable through [config/ocr_config.json](config/ocr_config.json):

- **OCR Engines**: Configure Tesseract, Google Vision, Azure settings
- **Image Preprocessing**: Adjust enhancement parameters
- **Form Extraction**: Define field patterns and validation rules
- **CSV Export**: Customize output format and columns
- **Processing**: Set batch sizes, timeouts, and retry settings

## 🎯 Supported Form Fields

The system is optimized to extract:

- **Names (Nombres)**: Spanish names with proper capitalization and spell-checking
- **Numbers (Números)**: Phone numbers, ID numbers, student IDs
- **Subjects (Materias)**: Course names and academic subjects

## 📊 Output Formats

### Standard CSV Output
- Filename, Name, Number, Subject
- Confidence scores and validation status
- Processing timestamps and notes

### Additional Reports
- **Validation Report**: Detailed field-by-field analysis
- **Summary Statistics**: Processing success rates and metrics
- **Error Report**: Failed extractions with reasons

## 🔧 Advanced Usage

### Custom Field Patterns

```python
# Define custom field extraction patterns
custom_config = {
    "field_patterns": {
        "email": {
            "keywords": ["email", "correo", "e-mail"],
            "position": "right_of_keyword",
            "validation": "email",
            "required": False
        }
    }
}

form_extractor = FormExtractor(config=custom_config)
```

### Ensemble OCR Configuration

```python
# Configure multiple OCR engines with voting
ocr_config = {
    "ensemble": {
        "enabled": True,
        "engines_to_use": ["google_vision", "azure_vision", "tesseract"],
        "min_confidence": 0.8
    }
}

ocr_engine = OCREngine(config=ocr_config)
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📈 Performance Tips

1. **Use high DPI (300+)** for PDF conversion
2. **Enable GPU acceleration** if available for OpenCV
3. **Use cloud OCR services** for better handwriting recognition
4. **Batch processing** for multiple files
5. **Preprocess images** for better OCR accuracy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

**Tesseract not found**:
- Ensure Tesseract is installed and in PATH
- Install Spanish language pack: `tesseract-ocr-spa`

**PDF conversion fails**:
- Install Poppler utilities
- Check PDF file is not corrupted or password protected

**Poor OCR accuracy**:
- Increase DPI for PDF conversion (try 400-600)
- Enable image preprocessing steps
- Use cloud OCR services for handwritten text
- For batch processing, try the simple processor with pdf2image

**Spanish characters not recognized**:
- Verify Spanish language pack is installed
- Check Unicode encoding in configuration
- Enable spell checking for Spanish names

**Prediction models not working**:
- Ensure CSV data is properly formatted with required columns
- Check that scikit-learn and xgboost are installed
- Run in interactive environment (Jupyter/VS Code) for widget support

## 📞 Support

For questions and support:
- Check the [scripts/](scripts/) directory for usage patterns
- Review [config/ocr_config.json](config/ocr_config.json) for all configuration options
- Run with `logging.level: "DEBUG"` for detailed processing information
- For prediction features, see the ML model scripts in [scripts/](scripts/)
- Batch processing scripts available in [src/batch_pdf_processor.py](src/batch_pdf_processor.py)

---

**Made with ❤️ for Spanish form processing**