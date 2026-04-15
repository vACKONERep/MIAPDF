# Prototipo de Automatización de Notas Académicas

**Proyecto de Titulación**  
Maestría en Inteligencia Artificial Aplicada  
Universidad de Las Américas  

**Autores:** Oppíkofer López Jessica Marisol y Carrillo Barros Juan Carlos  

---

## Descripción del Problema y Solución

Este prototipo aborda el problema del registro manual de notas en rúbricas PDF manuscritas del externado clínico de la Facultad de Medicina. El proceso manual es lento, propenso a errores y consume tiempo valioso del personal académico.

**Solución implementada:**  
Un prototipo modular en Python que automatiza:
- La conversión de PDFs manuscritos a texto mediante OCR
- La extracción de campos relevantes (nombre del estudiante, semestre, hospital, rotación, nota total)
- La anonimización automática de datos sensibles para proteger la privacidad estudiantil
- La predicción del nivel de riesgo académico (Baja/Media/Alta) utilizando modelos de Machine Learning interpretables

El prototipo funciona con datos simulados para demostración y es completamente reproducible para fines académicos.

---

## Características Principales

### Procesamiento OCR
- **Motores OCR**: PaddleOCR (principal), EasyOCR y Tesseract con soporte para español
- **Optimización**: Especializado para handwriting en español médico
- **Precisión**: Aproximadamente 62.5% en pruebas con handwriting real
- **Campos extraídos**: Nombre estudiante, semestre, hospital, rotación, nota total

### Anonimización de Datos
- Reemplazo automático de nombres reales por "Estudiante 1", "Estudiante 2", etc.
- Protección total de la privacidad estudiantil
- Cumplimiento con regulaciones de datos educativos

### Procesamiento de Excel
- Unificación automática de archivos Excel con calificaciones estudiantiles
- Detección inteligente de encabezados y formatos variables
- Conversión a CSV unificado para análisis

### Modelos de Machine Learning
- **Algoritmo**: Random Forest Classifier para predicción de riesgo
- **Variables**: Codificación de semestre, materia y estudiante
- **Categorías de riesgo**:
  - Baja: Nota < 6.0
  - Media: 6.0 ≤ Nota < 8.0
  - Alta: Nota ≥ 8.0
- **Interpretabilidad**: Análisis SHAP y LIME para explicaciones del modelo

### Salida de Datos
- **Formato CSV**: Archivo,Nombre,Semestre,Materia,Nota,Fecha_Procesamiento
- **Anonimización obligatoria**: Los nombres reales nunca aparecen en las salidas
- **Un archivo por estudiante**: Cada PDF genera una fila en el CSV final

---

## Requisitos Técnicos

- **Python**: 3.8 o superior
- **Sistema Operativo**: Windows, Linux o macOS
- **Dependencias**: Ver `requirements.txt`

**Dependencias principales:**
- PyMuPDF, Pillow, OpenCV (procesamiento de PDFs e imágenes)
- PaddleOCR, EasyOCR, PyTesseract (motores OCR)
- Pandas, NumPy (procesamiento de datos)
- Scikit-learn, XGBoost (Machine Learning)
- SHAP, LIME (interpretabilidad)
- Matplotlib, Seaborn (visualizaciones)

---

## Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/vACKONERep/MIAPDF.git
cd MIAPDF
```

### 2. Instalar Dependencias de Python
```bash
pip install -r requirements.txt
```

### 3. Instalar Dependencias del Sistema

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

**Nota**: PaddleOCR requiere PyTorch. Si hay problemas:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

---

## Uso del Prototipo

### Procesamiento Básico de PDFs
```bash
# Procesar todos los PDFs en data/input/ 
python simple_workflow.py
```

### Procesamiento Individual de PDF
```bash
# Extraer campos de un PDF específico
python process_handwritten_pdf.py ruta/al/archivo.pdf salida.csv
```

### Procesamiento de Excel
```bash
# Unificar archivos Excel y anonimizar
python scripts/excel_processor.py
```

### Predicción de Riesgo Académico
```bash
# Ejecutar modelo de predicción interactivo
python scripts/prediction_rf_classifier.py
```

### Análisis de Interpretabilidad
```bash
# Generar explicaciones SHAP y LIME
python scripts/interpretability_analysis.py
```

### Generación de Imágenes para Documentación
```bash
# Crear visualizaciones para el informe de titulación
python scripts/generate_appendix_images.py
```

---

## Estructura del Proyecto

```
MIAPDF/
├── src/                          # Código fuente modular
│   ├── __init__.py              # Inicialización del paquete
│   ├── main.py                  # Orquestador principal
│   ├── pdf_processor.py         # Conversión PDF a imágenes
│   ├── image_preprocessor.py    # Preprocesamiento de imágenes
│   ├── ocr_engine.py            # Motores OCR
│   ├── form_extractor.py        # Extracción de campos
│   ├── csv_exporter.py          # Exportación a CSV
│   └── batch_pdf_processor.py   # Procesamiento por lotes
├── scripts/                     # Scripts de análisis
│   ├── prediction_rf_classifier.py  # Modelo de predicción de riesgo
│   ├── prediction_rf_regressor.py   # Regresor de calificaciones
│   ├── prediction_xgb_classifier.py # XGBoost clasificador
│   ├── prediction_xgb_regressor.py  # XGBoost regresor
│   ├── interpretability_analysis.py # Análisis SHAP/LIME
│   ├── excel_processor.py       # Procesamiento de Excel
│   ├── generate_appendix_images.py # Generación de imágenes
│   └── process_single_pdf.py    # Procesamiento individual
├── data/
│   ├── input/                   # PDFs de entrada
│   └── output/                  # CSVs generados
├── config/
│   └── ocr_config.json          # Configuración OCR
├── interpretability_plots/      # Gráficos SHAP/LIME
├── models/                      # Modelos entrenados (vacío)
├── MiAModelo.ipynb              # Notebook de procesamiento Excel
├── simple_workflow.py           # Script principal de demo
├── process_handwritten_pdf.py   # Script de extracción OCR
├── requirements.txt             # Dependencias Python
├── interpretability_report.md   # Reporte de interpretabilidad
└── README.md                    # Este archivo
```

---

## Detalles Técnicos

### Flujo de Procesamiento
1. **Conversión PDF**: PyMuPDF convierte PDFs a imágenes de alta resolución
2. **Preprocesamiento**: OpenCV mejora contraste, reduce ruido y binariza
3. **OCR**: PaddleOCR procesa imágenes para extraer texto en español
4. **Extracción**: Algoritmos buscan campos específicos en el texto OCR
5. **Anonimización**: Nombres reales se reemplazan por identificadores genéricos
6. **Exportación**: Datos estructurados se guardan en CSV

### Datos de Entrada
- **PDFs manuscritos**: Rúbricas del externado clínico con campos específicos
- **Archivos Excel**: Calificaciones estudiantiles en formatos variables
- **Campos requeridos**: Nombre estudiante, semestre, materia, nota

### Datos de Salida
- **CSV unificado**: `unificado_final_anonimo.csv` con todas las calificaciones
- **Formato**: Nombre_del_estudiante,Semestre,Materia,Nota
- **Anonimización**: Nombres como "Estudiante 1", "Estudiante 2", etc.

### Modelo de Machine Learning
- **Entrenamiento**: Basado en datos históricos anonimizados
- **Características**: Semestre codificado, materia codificada, estudiante codificado
- **Métricas**: Accuracy, precision, recall reportadas en pruebas
- **Interpretabilidad**: SHAP para importancia global, LIME para explicaciones locales

---

## Limitaciones

- **Precisión OCR**: ~62.5% en handwriting español médico
- **Dependencias complejas**: Requiere instalación manual de Tesseract y Poppler
- **Datos simulados**: El prototipo usa datos de demostración, no procesamiento OCR real completo
- **Alcance académico**: Diseñado como prototipo de titulación, no para producción industrial
- **Idioma**: Optimizado exclusivamente para español médico
- **Formato específico**: Funciona con el formato exacto de rúbricas de la Facultad de Medicina


## Licencia

Este proyecto es parte de un trabajo académico de titulación y se distribuye bajo licencia MIT para fines educativos.

---

**Desarrollado para la Maestría en Inteligencia Artificial Aplicada - Universidad de Las Américas**
