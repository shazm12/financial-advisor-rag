from typing import Dict, List
from langchain.tools import BaseTool
import camelot
import pandas as pd


class TableExtractionTool(BaseTool):
    name: str = "table-extractor"
    description: str = "Extract structured tables from PDF documents"

    def _run(self, pdf_path: str) -> dict:

        tables = {
            "transactions": [],
            "accounts_summary": [],
            "fees_table": [],
            "raw_table": [],
        }

        try:
            camelot_tables = camelot.read_pdf(pdf_path, pages="all")
            for table in camelot_tables:
                df = table.df
                # Classify table type based on headers
                table_type = self._classify_tables(df)
                tables[table_type].append(df)
        except Exception as e:
            print(f"Camelot extraction failed: {e}")

        formatted_tables = self._format_tables(tables)
        return formatted_tables

    def _format_tables(self, tables_data: Dict[str, List[pd.DataFrame]]):

        formatted_tables = {}
        for table_type, dfs in tables_data.items():
            formatted_tables[table_type] = []
            for df in dfs:
                formatted_tables[table_type].append(
                    {"dataframe": df, "csv": df.to_csv(index=False)}
                )
        return formatted_tables

    def _classify_tables(self, df: pd.DataFrame) -> str:
        headers = [str(col).lower() for col in df.columns]

        if any(
            word in "".join(headers)
            for word in ["date", "description", "details", "amount", "balance"]
        ):
            return "transactions"

        elif any(word in "".join(headers) for word in ["summary", "total", "balance"]):
            return "account_summary"

        elif any(word in "".join(headers) for word in ["fee", "charge", "interest"]):
            return "fees_table"
        else:
            return "raw_tables"
