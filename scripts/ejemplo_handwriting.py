#!/usr/bin/env python3
"""
Ejemplo de uso del script process_handwritten_pdf.py

Este ejemplo muestra cómo procesar un PDF con handwriting en español.
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Ruta al PDF (debe tener al menos 9 páginas)
    pdf_path = "data/input/ejemplo.pdf"  # Cambiar a tu PDF
    output_csv = "data/output/resultados.csv"

    # Verificar que el PDF existe
    if not Path(pdf_path).exists():
        print(f"Error: PDF no encontrado en {pdf_path}")
        print("Coloca un PDF de ejemplo en data/input/")
        sys.exit(1)

    # Ejecutar el script
    cmd = [sys.executable, "process_handwritten_pdf.py", pdf_path, output_csv]
    print(f"Ejecutando: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        print("Salida estándar:")
        print(result.stdout)
        if result.stderr:
            print("Errores:")
            print(result.stderr)
        print(f"Código de salida: {result.returncode}")
    except Exception as e:
        print(f"Error ejecutando el script: {e}")

if __name__ == "__main__":
    main()