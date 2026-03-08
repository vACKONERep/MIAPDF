"""
CSV Export Module

Handles exporting extracted form data to CSV format.
Provides flexible formatting and validation options.
"""

import logging
import csv
import pandas as pd
from typing import List, Dict, Optional, Union, Any
from pathlib import Path
import json
from datetime import datetime
import os

from .form_extractor import ExtractedForm, FormField

logger = logging.getLogger(__name__)


class CSVExporter:
    """
    Exports form data to CSV format with configurable options.
    
    Supports multiple output formats and validation reporting.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize CSV exporter.
        
        Args:
            config: Configuration dictionary for CSV export
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.config = config or self._get_default_config()
        
    def _get_default_config(self) -> Dict:
        """Get default configuration for CSV export."""
        return {
            "output": {
                "encoding": "utf-8-sig",  # BOM for Excel compatibility
                "separator": ",",
                "include_headers": True,
                "include_metadata": False,
                "date_format": "%Y-%m-%d %H:%M:%S"
            },
            "columns": {
                "filename": "Archivo",
                "nombre": "Nombre",
                "numero": "Número",
                "materia": "Materia",
                "confidence": "Confianza",
                "validation_score": "Validación",
                "processing_date": "Fecha Procesamiento",
                "notes": "Notas"
            },
            "validation": {
                "include_failed_validations": True,
                "mark_invalid_fields": True,
                "invalid_field_suffix": " [REVISAR]"
            }
        }
    
    def export_single_form(self, extracted_form: ExtractedForm, 
                          filename: str, output_path: str) -> bool:
        """
        Export a single extracted form to CSV.
        
        Args:
            extracted_form: Extracted form data
            filename: Original filename of the form
            output_path: Path to save CSV file
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Prepare data row
            row_data = self._prepare_row_data(extracted_form, filename)
            
            # Check if file exists to determine if headers are needed
            file_exists = os.path.exists(output_path)
            
            # Write to CSV
            with open(output_path, 'a', newline='', encoding=self.config["output"]["encoding"]) as csvfile:
                writer = csv.DictWriter(csvfile, 
                                      fieldnames=list(self.config["columns"].values()),
                                      delimiter=self.config["output"]["separator"])
                
                # Write headers if file is new
                if not file_exists and self.config["output"]["include_headers"]:
                    writer.writeheader()
                
                # Write data row
                writer.writerow(row_data)
                
            self.logger.info(f"Successfully exported form data to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export single form: {e}")
            return False
    
    def export_multiple_forms(self, forms_data: List[Tuple[ExtractedForm, str]], 
                             output_path: str) -> bool:
        """
        Export multiple extracted forms to a single CSV file.
        
        Args:
            forms_data: List of tuples (ExtractedForm, filename)
            output_path: Path to save CSV file
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Prepare all row data
            all_rows = []
            for extracted_form, filename in forms_data:
                row_data = self._prepare_row_data(extracted_form, filename)
                all_rows.append(row_data)
            
            # Write to CSV
            with open(output_path, 'w', newline='', encoding=self.config["output"]["encoding"]) as csvfile:
                writer = csv.DictWriter(csvfile, 
                                      fieldnames=list(self.config["columns"].values()),
                                      delimiter=self.config["output"]["separator"])
                
                # Write headers
                if self.config["output"]["include_headers"]:
                    writer.writeheader()
                
                # Write all data rows
                writer.writerows(all_rows)
                
            self.logger.info(f"Successfully exported {len(all_rows)} forms to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export multiple forms: {e}")
            return False
    
    def export_with_pandas(self, forms_data: List[Tuple[ExtractedForm, str]], 
                          output_path: str, **pandas_kwargs) -> bool:
        """
        Export using pandas for advanced formatting options.
        
        Args:
            forms_data: List of tuples (ExtractedForm, filename)
            output_path: Path to save CSV file
            **pandas_kwargs: Additional arguments for pandas.to_csv()
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Prepare DataFrame
            all_rows = []
            for extracted_form, filename in forms_data:
                row_data = self._prepare_row_data(extracted_form, filename)
                all_rows.append(row_data)
            
            df = pd.DataFrame(all_rows)
            
            # Set default pandas options
            default_kwargs = {
                'index': False,
                'encoding': self.config["output"]["encoding"],
                'sep': self.config["output"]["separator"]
            }
            default_kwargs.update(pandas_kwargs)
            
            # Export to CSV
            df.to_csv(output_path, **default_kwargs)
            
            self.logger.info(f"Successfully exported {len(all_rows)} forms using pandas")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export with pandas: {e}")
            return False
    
    def _prepare_row_data(self, extracted_form: ExtractedForm, filename: str) -> Dict[str, str]:
        """Prepare a single row of data for CSV export."""
        columns = self.config["columns"]
        validation_config = self.config["validation"]
        
        # Start with filename
        row_data = {
            columns["filename"]: filename
        }
        
        # Add processing date
        if "processing_date" in columns:
            current_time = datetime.now().strftime(self.config["output"]["date_format"])
            row_data[columns["processing_date"]] = current_time
        
        # Add form fields
        for field_name in ["nombre", "numero", "materia"]:
            column_name = columns.get(field_name, field_name.capitalize())
            
            if field_name in extracted_form.fields:
                field = extracted_form.fields[field_name]
                field_value = field.value
                
                # Mark invalid fields if configured
                if (validation_config["mark_invalid_fields"] and 
                    not field.validation_passed):
                    field_value += validation_config["invalid_field_suffix"]
                
                row_data[column_name] = field_value
            else:
                row_data[column_name] = ""
        
        # Add confidence scores if configured
        if "confidence" in columns:
            confidence_pct = f"{extracted_form.overall_confidence:.1%}"
            row_data[columns["confidence"]] = confidence_pct
            
        if "validation_score" in columns:
            validation_pct = f"{extracted_form.validation_score:.1%}"
            row_data[columns["validation_score"]] = validation_pct
        
        # Add processing notes if configured
        if "notes" in columns and extracted_form.processing_notes:
            notes_text = "; ".join(extracted_form.processing_notes)
            row_data[columns["notes"]] = notes_text
        
        return row_data
    
    def create_validation_report(self, forms_data: List[Tuple[ExtractedForm, str]], 
                               output_path: str) -> bool:
        """
        Create a detailed validation report CSV.
        
        Args:
            forms_data: List of tuples (ExtractedForm, filename)
            output_path: Path to save validation report
            
        Returns:
            True if report was created successfully, False otherwise
        """
        try:
            report_rows = []
            
            for extracted_form, filename in forms_data:
                # Overall form statistics
                base_row = {
                    "Archivo": filename,
                    "Confianza General": f"{extracted_form.overall_confidence:.2%}",
                    "Puntuación Validación": f"{extracted_form.validation_score:.2%}",
                    "Campos Extraídos": len(extracted_form.fields),
                    "Campos Válidos": sum(1 for f in extracted_form.fields.values() if f.validation_passed)
                }
                
                # Add field-specific details
                for field_name, field in extracted_form.fields.items():
                    field_row = base_row.copy()
                    field_row.update({
                        "Campo": field_name.capitalize(),
                        "Valor": field.value,
                        "Confianza Campo": f"{field.confidence:.2%}",
                        "Validación": "VÁLIDO" if field.validation_passed else "INVÁLIDO",
                        "Tipo": field.field_type,
                        "Posición": f"{field.position}"
                    })
                    report_rows.append(field_row)
                
                # Add notes if any
                if extracted_form.processing_notes:
                    notes_row = base_row.copy()
                    notes_row.update({
                        "Campo": "NOTAS",
                        "Valor": "; ".join(extracted_form.processing_notes),
                        "Confianza Campo": "",
                        "Validación": "",
                        "Tipo": "notes",
                        "Posición": ""
                    })
                    report_rows.append(notes_row)
            
            # Export validation report
            df = pd.DataFrame(report_rows)
            df.to_csv(output_path, 
                     index=False,
                     encoding=self.config["output"]["encoding"],
                     sep=self.config["output"]["separator"])
            
            self.logger.info(f"Validation report created: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create validation report: {e}")
            return False
    
    def create_summary_statistics(self, forms_data: List[Tuple[ExtractedForm, str]], 
                                 output_path: str) -> bool:
        """
        Create summary statistics CSV.
        
        Args:
            forms_data: List of tuples (ExtractedForm, filename)
            output_path: Path to save summary statistics
            
        Returns:
            True if statistics were created successfully, False otherwise
        """
        try:
            if not forms_data:
                self.logger.warning("No data provided for summary statistics")
                return False
            
            # Calculate statistics
            total_forms = len(forms_data)
            total_fields = sum(len(form.fields) for form, _ in forms_data)
            valid_fields = sum(sum(1 for field in form.fields.values() if field.validation_passed) 
                             for form, _ in forms_data)
            
            avg_confidence = sum(form.overall_confidence for form, _ in forms_data) / total_forms
            avg_validation = sum(form.validation_score for form, _ in forms_data) / total_forms
            
            # Field-specific statistics
            field_stats = {}
            for field_name in ["nombre", "numero", "materia"]:
                found_count = sum(1 for form, _ in forms_data if field_name in form.fields)
                valid_count = sum(1 for form, _ in forms_data 
                                if field_name in form.fields and 
                                   form.fields[field_name].validation_passed)
                
                field_stats[field_name] = {
                    "encontrados": found_count,
                    "válidos": valid_count,
                    "porcentaje_encontrado": f"{found_count/total_forms:.1%}",
                    "porcentaje_válido": f"{valid_count/found_count:.1%}" if found_count > 0 else "0.0%"
                }
            
            # Create summary data
            summary_data = [
                {"Métrica": "Total de Formularios", "Valor": str(total_forms)},
                {"Métrica": "Total de Campos", "Valor": str(total_fields)},
                {"Métrica": "Campos Válidos", "Valor": str(valid_fields)},
                {"Métrica": "Confianza Promedio", "Valor": f"{avg_confidence:.2%}"},
                {"Métrica": "Validación Promedio", "Valor": f"{avg_validation:.2%}"},
                {"Métrica": "", "Valor": ""},  # Separator
                {"Métrica": "ESTADÍSTICAS POR CAMPO", "Valor": ""},
            ]
            
            for field_name, stats in field_stats.items():
                summary_data.extend([
                    {"Métrica": f"{field_name.capitalize()} - Encontrados", "Valor": stats["porcentaje_encontrado"]},
                    {"Métrica": f"{field_name.capitalize()} - Válidos", "Valor": stats["porcentaje_válido"]},
                ])
            
            # Export summary
            df = pd.DataFrame(summary_data)
            df.to_csv(output_path, 
                     index=False,
                     encoding=self.config["output"]["encoding"],
                     sep=self.config["output"]["separator"])
            
            self.logger.info(f"Summary statistics created: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create summary statistics: {e}")
            return False
    
    def update_config(self, new_config: Dict) -> None:
        """
        Update exporter configuration.
        
        Args:
            new_config: New configuration dictionary
        """
        self.config.update(new_config)
        self.logger.info("CSV exporter configuration updated")
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats."""
        return ["csv", "excel", "tsv", "json"]
    
    def export_to_format(self, forms_data: List[Tuple[ExtractedForm, str]], 
                        output_path: str, format_type: str = "csv") -> bool:
        """
        Export to different formats.
        
        Args:
            forms_data: List of tuples (ExtractedForm, filename)
            output_path: Path to save file
            format_type: Output format (csv, excel, tsv, json)
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Prepare DataFrame
            all_rows = []
            for extracted_form, filename in forms_data:
                row_data = self._prepare_row_data(extracted_form, filename)
                all_rows.append(row_data)
            
            df = pd.DataFrame(all_rows)
            
            if format_type.lower() == "csv":
                df.to_csv(output_path, index=False, encoding=self.config["output"]["encoding"])
            elif format_type.lower() == "excel":
                df.to_excel(output_path, index=False)
            elif format_type.lower() == "tsv":
                df.to_csv(output_path, index=False, sep='\t', encoding=self.config["output"]["encoding"])
            elif format_type.lower() == "json":
                df.to_json(output_path, orient='records', force_ascii=False, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            self.logger.info(f"Successfully exported to {format_type.upper()}: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export to {format_type}: {e}")
            return False