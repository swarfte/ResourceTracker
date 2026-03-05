"""File parsing utilities for CSV and Excel files."""

from typing import Optional
import pandas as pd


class FileParser:
    """Handle CSV and Excel file parsing."""

    @staticmethod
    def parse_file(uploaded_file) -> Optional[pd.DataFrame]:
        """Parse CSV/XLS/XLSX file with automatic encoding detection.

        Args:
            uploaded_file: Streamlit UploadedFile object

        Returns:
            DataFrame or None if parsing fails
        """
        try:
            if uploaded_file.name.endswith('.csv'):
                # Try multiple encodings for CSV
                for encoding in ['utf-8', 'gbk', 'latin1']:
                    try:
                        uploaded_file.seek(0)  # Reset file pointer
                        df = pd.read_csv(uploaded_file, encoding=encoding)
                        return df
                    except UnicodeDecodeError:
                        continue
                # If all encodings fail
                return None
            else:
                # Excel file (xls or xlsx)
                df = pd.read_excel(uploaded_file)
                return df
        except Exception as e:
            # Return None if parsing fails
            return None
