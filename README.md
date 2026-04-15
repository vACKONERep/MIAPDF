# Prototipo - Automatización Inteligente de Notas Académicas

**Proyecto de Titulación**  
Maestría en Inteligencia Artificial Aplicada  
Universidad de Las Américas  

**Autores:** Oppíkofer López Jessica Marisol y Carrillo Barros Juan Carlos  

---

## Descripción del problema y solución

El prototipo resuelve el problema del registro manual de notas en rúbricas PDF manuscritas del externado clínico de la Facultad de Medicina.  

**Solución entregada:**  
Un **prototipo modular** en Python que permite:
- Convertir PDFs manuscritos a texto mediante OCR
- Extraer campos relevantes (nota, semestre, materia)
- Anonimizar datos sensibles
- Predecir el nivel de riesgo académico (Alta / Media / Baja) con un modelo de Machine Learning interpretable

El prototipo es completamente funcional para fines académicos y reproducible.

---

## Requisitos técnicos y dependencias

- Python 3.10 o superior
- Sistema operativo: Windows, Linux o macOS
- Dependencias listadas en `requirements.txt`

**Dependencias principales:**
- OpenCV, pdf2image, EasyOCR, Tesseract (con paquete español)
- pandas, scikit-learn, numpy
- SHAP y LIME (interpretabilidad)
- Joblib (guardado del modelo)

---

## Instalación

```bash
git clone https://github.com/vACKONERep/MIAPDF.git
cd MIAPDF
pip install -r requirements.txt
```

### Instalación de Dependencias del Sistema

**Windows:**
- Instalar Tesseract OCR desde: https://github.com/UB-Mannheim/tesseract/wiki
- Instalar Poppler desde: https://github.com/oschwartz10612/poppler-windows/releases/
- Agregar ambos al PATH del sistema

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-spa poppler-utils
```

**macOS:**
```bash
brew install tesseract tesseract-lang poppler
```

---

## Uso del Prototipo

### Procesamiento de PDFs

```bash
# Procesar un PDF individual
python process_handwritten_pdf.py ruta/al/archivo.pdf salida.csv

# Procesamiento por lotes (demo)
python simple_workflow.py
```

### Predicción de Riesgo Académico

```bash
# Ejecutar modelo de predicción
python scripts/prediction_rf_classifier.py
```

### Análisis de Interpretabilidad

```bash
# Generar explicaciones SHAP y LIME
python scripts/interpretability_analysis.py
```

---

## Estructura del Proyecto

```
MIAPDF/
├── src/                          # Código fuente modular
│   ├── pdf_processor.py         # Conversión PDF a imágenes
│   ├── image_preprocessor.py    # Preprocesamiento de imágenes
│   ├── ocr_engine.py            # Motores OCR (EasyOCR + Tesseract)
│   ├── form_extractor.py        # Extracción de campos
│   └── csv_exporter.py          # Exportación a CSV
├── scripts/                     # Scripts de análisis
│   ├── prediction_rf_classifier.py  # Modelo de predicción de riesgo
│   ├── interpretability_analysis.py # Análisis SHAP/LIME
│   └── excel_processor.py       # Procesamiento de Excel
├── data/
│   ├── input/                   # PDFs de entrada
│   └── output/                  # CSVs generados
├── interpretability_plots/      # Gráficos SHAP/LIME generados
├── appendix_images/             # Imágenes para documentación
├── config/
│   └── ocr_config.json          # Configuración OCR
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

---

## Características Técnicas

### OCR y Procesamiento
- **Motores OCR**: EasyOCR (optimizado para handwriting) + Tesseract (con soporte español)
- **Preprocesamiento**: OpenCV para mejora de imágenes (contraste, ruido, binarización)
- **Precisión**: ~62.5% en handwriting español (reportado en pruebas)
- **Campos extraídos**: Nombre estudiante, semestre, materia, nota total

### Anonimización de Datos
- Reemplazo automático de nombres reales por "Estudiante 1", "Estudiante 2", etc.
- Protección de privacidad estudiantil
- Cumplimiento con regulaciones de datos educativos

### Modelos de Machine Learning
- **Algoritmo**: Random Forest Classifier
- **Predicción**: Nivel de riesgo académico (Alta/Media/Baja)
- **Interpretabilidad**: SHAP y LIME para explicaciones
- **Métricas**: Accuracy, precision, recall reportadas

---

## Limitaciones y Consideraciones

- **Precisión OCR**: Optimizado para handwriting español, pero no perfecto
- **Dependencias**: Requiere instalación manual de Tesseract y Poppler
- **Alcance**: Prototipo académico, no optimizado para producción a gran escala
- **Datos**: Funciona con el formato específico de rúbricas de la Facultad de Medicina

---

## Documentación Académica

- `documento_capstone_mejorado.md`: Documento completo de titulación
- `interpretability_report.md`: Análisis detallado de interpretabilidad
- Scripts para generar anexos y visualizaciones automáticamente

---

## Licencia

Este proyecto es parte de un trabajo académico y se distribuye bajo licencia MIT para fines educativos.

---

**Desarrollado para la Maestría en Inteligencia Artificial Aplicada - Universidad de Las Américas**

---

# Prototype - Intelligent Academic Grade Automation

**Capstone Project**  
Master's in Applied Artificial Intelligence  
Universidad de Las Américas  

**Authors:** Jessica Marisol Oppíkofer López and Juan Carlos Carrillo Barros  

---

## Problem Description and Solution

The prototype solves the problem of manual grade recording in handwritten PDF rubrics from the clinical externship of the Faculty of Medicine.  

**Delivered Solution:**  
A **modular prototype** in Python that allows:
- Convert handwritten PDFs to text using OCR
- Extract relevant fields (grade, semester, subject)
- Anonymize sensitive data
- Predict academic risk level (High / Medium / Low) with an interpretable Machine Learning model

The prototype is fully functional for academic purposes and reproducible.

---

## Technical Requirements and Dependencies

- Python 3.10 or higher
- Operating System: Windows, Linux or macOS
- Dependencies listed in `requirements.txt`

**Main Dependencies:**
- OpenCV, pdf2image, EasyOCR, Tesseract (with Spanish package)
- pandas, scikit-learn, numpy
- SHAP and LIME (interpretability)
- Joblib (model saving)

---

## Installation

```bash
git clone https://github.com/vACKONERep/MIAPDF.git
cd MIAPDF
pip install -r requirements.txt
```

### System Dependencies Installation

**Windows:**
- Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
- Install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases/
- Add both to the system PATH

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-spa poppler-utils
```

**macOS:**
```bash
brew install tesseract tesseract-lang poppler
```

---

## Prototype Usage

### PDF Processing

```bash
# Process a single PDF
python process_handwritten_pdf.py path/to/file.pdf output.csv

# Batch processing (demo)
python simple_workflow.py
```

### Academic Risk Prediction

```bash
# Run prediction model
python scripts/prediction_rf_classifier.py
```

### Interpretability Analysis

```bash
# Generate SHAP and LIME explanations
python scripts/interpretability_analysis.py
```

---

## Project Structure

```
MIAPDF/
├── src/                          # Modular source code
│   ├── pdf_processor.py         # PDF to image conversion
│   ├── image_preprocessor.py    # Image preprocessing
│   ├── ocr_engine.py            # OCR engines (EasyOCR + Tesseract)
│   ├── form_extractor.py        # Field extraction
│   └── csv_exporter.py          # CSV export
├── scripts/                     # Analysis scripts
│   ├── prediction_rf_classifier.py  # Risk prediction model
│   ├── interpretability_analysis.py # SHAP/LIME analysis
│   └── excel_processor.py       # Excel processing
├── data/
│   ├── input/                   # Input PDFs
│   └── output/                  # Generated CSVs
├── interpretability_plots/      # Generated SHAP/LIME plots
├── appendix_images/             # Images for documentation
├── config/
│   └── ocr_config.json          # OCR configuration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## Technical Features

### OCR and Processing
- **OCR Engines**: EasyOCR (optimized for handwriting) + Tesseract (with Spanish support)
- **Preprocessing**: OpenCV for image enhancement (contrast, noise, binarization)
- **Accuracy**: ~62.5% on Spanish handwriting (reported in tests)
- **Extracted Fields**: Student name, semester, subject, total grade

### Data Anonymization
- Automatic replacement of real names with "Student 1", "Student 2", etc.
- Student privacy protection
- Compliance with educational data regulations

### Machine Learning Models
- **Algorithm**: Random Forest Classifier
- **Prediction**: Academic risk level (High/Medium/Low)
- **Interpretability**: SHAP and LIME for explanations
- **Metrics**: Accuracy, precision, recall reported

---

## Limitations and Considerations

- **OCR Accuracy**: Optimized for Spanish handwriting, but not perfect
- **Dependencies**: Requires manual installation of Tesseract and Poppler
- **Scope**: Academic prototype, not optimized for large-scale production
- **Data**: Works with the specific format of Faculty of Medicine rubrics

---

## Academic Documentation

- `documento_capstone_mejorado.md`: Complete capstone document
- `interpretability_report.md`: Detailed interpretability analysis
- Scripts to automatically generate appendices and visualizations

---

## License

This project is part of an academic work and is distributed under the MIT License for educational purposes.

---

**Developed for the Master's in Applied Artificial Intelligence - Universidad de Las Américas**