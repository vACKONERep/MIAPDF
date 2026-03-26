# excel_processor.py
"""
Excel to CSV Processor for Student Grade Data
Processes Excel files containing student grades and converts them to unified CSV format.
Supports multiple Excel formats and automatic data cleaning.
"""

import pandas as pd
import glob
import re
import os
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelProcessor:
    def __init__(self, input_dir: str = "data/input", output_dir: str = "data/output"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def find_excel_files(self) -> List[str]:
        """Find all Excel files in the input directory."""
        patterns = ["*.xlsx", "*.xls", "*.xlsm"]
        excel_files = []
        for pattern in patterns:
            excel_files.extend(glob.glob(os.path.join(self.input_dir, pattern)))
        return excel_files

    def detect_header_row(self, df: pd.DataFrame) -> Optional[int]:
        """Detect the header row containing student data columns."""
        header_keywords = ['ord.', 'apellidos', 'nombres', 'id banner', 'correo', 'estudiante']
        for i, row in df.iterrows():
            row_str = row.astype(str).str.lower().str.strip()
            if any(keyword in ' '.join(row_str.values) for keyword in header_keywords):
                return i
        return None

    def find_name_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the column containing student names."""
        name_keywords = ['apellidos', 'nombres', 'estudiante', 'nombre del', 'alumnos']
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if any(keyword in col_lower for keyword in name_keywords):
                return col
        return None

    def extract_semester_from_filename(self, filename: str) -> str:
        """Extract semester information from filename."""
        filename_upper = os.path.basename(filename).upper()
        semester_match = re.search(r'(QUINTO|SEXTO|SEPTIMO|OCTAVO|NOVENO|DECIMO)', filename_upper)
        return semester_match.group(1) if semester_match else "Desconocido"

    def process_excel_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Process a single Excel file and return cleaned DataFrame."""
        try:
            logger.info(f"Processing: {os.path.basename(file_path)}")

            # Read Excel file
            df = pd.read_excel(file_path, engine='openpyxl', header=None)

            # Remove empty rows at the beginning
            df = df.dropna(how='all').reset_index(drop=True)

            # Detect header row
            header_row = self.detect_header_row(df)
            if header_row is None:
                logger.warning(f"No headers found in {os.path.basename(file_path)}, using row 0")
                df = pd.read_excel(file_path, header=0, engine='openpyxl')
            else:
                logger.info(f"Headers found in row {header_row}")
                df = pd.read_excel(file_path, header=header_row, engine='openpyxl')

            # Find and rename name column
            name_col = self.find_name_column(df)
            if name_col:
                df = df.rename(columns={name_col: 'Nombre_del_estudiante'})
                logger.info(f"Renamed column '{name_col}' to 'Nombre_del_estudiante'")
            else:
                logger.error(f"No name column found in {os.path.basename(file_path)}")
                return None

            # Add semester from filename
            semester = self.extract_semester_from_filename(file_path)
            df['Semestre'] = semester

            # Prepare ID columns
            id_cols = ['Nombre_del_estudiante', 'Semestre']
            if 'CORREO ELECTRONICO' in df.columns:
                id_cols.append('CORREO ELECTRONICO')
            if 'ID BANNER' in df.columns:
                id_cols.append('ID BANNER')

            # Melt subjects to rows
            df_long = df.melt(id_vars=id_cols, var_name='Materia', value_name='Nota')

            # Clean grades
            df_long['Nota'] = pd.to_numeric(df_long['Nota'], errors='coerce')
            df_long = df_long.dropna(subset=['Nota'])

            logger.info(f"Processed {len(df_long)} grade records")
            return df_long

        except Exception as e:
            logger.error(f"Error processing {os.path.basename(file_path)}: {e}")
            return None

    def process_all_files(self) -> pd.DataFrame:
        """Process all Excel files and combine into single DataFrame."""
        excel_files = self.find_excel_files()
        logger.info(f"Found {len(excel_files)} Excel files")

        all_data = pd.DataFrame()

        for file_path in excel_files:
            df = self.process_excel_file(file_path)
            if df is not None:
                all_data = pd.concat([all_data, df], ignore_index=True)

        if not all_data.empty:
            # Final cleanup
            all_data = all_data.sort_values(by=['Semestre', 'Nombre_del_estudiante', 'Materia'])
            all_data = all_data.drop_duplicates()
            all_data['Nota'] = all_data['Nota'].round(1)

        return all_data

    def save_unified_csv(self, df: pd.DataFrame, filename: str = "unificado.csv") -> str:
        """Save the unified DataFrame to CSV."""
        output_path = os.path.join(self.output_dir, filename)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Unified CSV saved to {output_path}")
        return output_path

    def anonymize_data(self, df: pd.DataFrame, filename: str = "unificado_anonimo.csv") -> str:
        """Anonymize student names and save to CSV."""
        if df.empty:
            logger.warning("No data to anonymize")
            return ""

        # Get unique names and create mapping
        unique_names = sorted(df['Nombre_del_estudiante'].dropna().unique())
        name_mapping = {name: f"Estudiante {i+1}" for i, name in enumerate(unique_names)}

        # Apply anonymization
        df_anon = df.copy()
        df_anon['Nombre_del_estudiante'] = df_anon['Nombre_del_estudiante'].map(name_mapping).fillna("Estudiante Desconocido")

        # Select relevant columns
        df_anon = df_anon[['Nombre_del_estudiante', 'Semestre', 'Materia', 'Nota']]

        # Save anonymized CSV
        output_path = os.path.join(self.output_dir, filename)
        df_anon.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Anonymized CSV saved to {output_path} ({len(name_mapping)} unique students)")
        return output_path

def main():
    """Main function to run the Excel processor."""
    processor = ExcelProcessor()

    # Process all Excel files
    unified_data = processor.process_all_files()

    if not unified_data.empty:
        # Save unified CSV
        processor.save_unified_csv(unified_data)

        # Save anonymized CSV
        processor.anonymize_data(unified_data)

        print(f"Processing complete. {len(unified_data)} total records processed.")
    else:
        print("No data was processed. Check your Excel files.")

if __name__ == "__main__":
    main()