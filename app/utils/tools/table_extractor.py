from typing import Dict, List
from langchain.tools import BaseTool
import pdfplumber
import pandas as pd
import re


class TableExtractionTool(BaseTool):
    name: str = "table-extractor"
    description: str = "Extract structured tables from PDF documents"

    def _run(self, pdf_path: str) -> dict:
        tables = {
            "transactions": [],
            "account_summary": [],
            "fees_table": [],
            "raw_tables": [],
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_tables = 0

                for page_num, page in enumerate(pdf.pages):

                    page_tables = page.extract_tables()

                    text_tables = self._extract_structured_text(page)

                    all_page_tables = page_tables + text_tables
                    total_tables += len(all_page_tables)

                    for i, table in enumerate(all_page_tables):
                        if table and len(table) > 1:  # Has headers + data
                            df = pd.DataFrame(table[1:], columns=table[0])
                            df = self._clean_dataframe(df)

                            if not df.empty:
                                table_type = self._classify_tables(df)
                                tables[table_type].append(df)

        except Exception as e:
            print(f"pdfplumber extraction failed: {e}")
            import traceback

            traceback.print_exc()

        formatted_tables = self._format_tables(tables)
        return formatted_tables


    def _extract_structured_text(self, page):
        """Enhanced extraction specifically for credit card statements"""
        text = page.extract_text()
        if not text:
            return []

        lines = text.split("\n")
        potential_tables = []

        # Look for transaction sections
        transaction_sections = self._find_transaction_sections(lines)

        for section in transaction_sections:
            table_data = self._parse_transaction_section(section)
            if table_data:
                potential_tables.append(table_data)

        return potential_tables


    def _find_transaction_sections(self, lines):
        """Find sections that contain transaction data"""
        sections = []
        current_section = []
        in_transaction_section = False

        transaction_headers = [
            "YOUR TRANSACTIONS",
            "Purchases, EMIs & Other Debits",
            "Payments & Other Credits",
            "Transaction Details",
        ]

        for line in lines:
            line = line.strip()

            # Check if we're entering a transaction section
            if any(header in line for header in transaction_headers):
                if current_section:  # Save previous section
                    sections.append(current_section)
                current_section = []
                in_transaction_section = True
                continue

            # Check if we're leaving transaction section
            if in_transaction_section and (
                line.startswith("Card Number:")
                or line.startswith("ACTIVE EMI")
                or line.startswith("SPECIAL BENEFITS")
                or len(line) == 0
            ):
                if len(current_section) > 5:  # Only save if it has enough data
                    sections.append(current_section)
                current_section = []
                in_transaction_section = False
                continue

            # Collect lines in transaction sections
            if in_transaction_section and self._looks_like_transaction_row(line):
                current_section.append(line)

        # Don't forget the last section
        if current_section and len(current_section) > 5:
            sections.append(current_section)

        return sections


    def _parse_transaction_section(self, section_lines):
        """Parse a transaction section into table format with simple narratives"""
        if not section_lines:
            return None

        headers = ["Date", "Description", "Amount", "Type", "Narrative"]
        table_data = [headers]

        for line in section_lines:
            row = self._parse_credit_card_transaction(line)
            if row:
                narrative = self._create_simple_narrative(row)
                row.append(narrative)
                table_data.append(row)

        return table_data if len(table_data) > 1 else None

    def _create_simple_narrative(self, transaction_row):
        """Convert transaction data to simple natural language"""
        date, description, amount, txn_type = transaction_row
        
        merchant = description.split(',')[0].strip()
        
        if txn_type == "DR":  # Debit/Expense
            return f"On {date}, spent ₹{amount} at {merchant}"
        else:  # Credit/Income  
            return f"On {date}, received ₹{amount} from {merchant}"

    def _parse_credit_card_transaction(self, line):
        """Parse individual credit card transaction line"""
        # Pattern for date at start: "21 Aug 25" or "21/Aug/2025"
        date_match = re.match(
            r"^(\d{1,2}\s+(Aug|Sep|Oct|Nov|Dec|Jan|Feb|Mar|Apr|May|Jun|Jul)\s+\d{2,4})",
            line,
        )

        if not date_match:
            return None

        date = date_match.group(1)
        remaining = line[len(date):].strip()

        # Look for amount at the end (format: "1,234.56 DR" or "1,234.56 CR")
        amount_match = re.search(r"([\d,]+\.?\d*)\s+(DR|CR)\s*$", remaining)

        if amount_match:
            amount = amount_match.group(1)
            txn_type = amount_match.group(2)
            description = remaining[:amount_match.start()].strip()

            return [date, description, amount, txn_type]

        return None


    def _looks_like_transaction_row(self, line):
        """Enhanced transaction row detection for credit cards"""
        if not line or len(line.strip()) < 10:
            return False

        # Credit card specific patterns
        patterns = [
            r"^\d{1,2}\s+(Aug|Sep|Oct|Nov|Dec|Jan|Feb|Mar|Apr|May|Jun|Jul)\s+\d{2}",  # Date format
            r"(DR|CR)\s*$",  # Ends with DR or CR
        ]

        return any(re.search(pattern, line) for pattern in patterns)

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize the dataframe"""

        df = df.dropna(how="all").dropna(axis=1, how="all")

        # Remove rows where all values are empty strings
        df = df[~df.apply(lambda x: x.astype(str).str.strip().eq("").all(), axis=1)]

        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]

        # Remove duplicate headers that might appear in data
        if len(df) > 1:
            header_row = df.iloc[0].astype(str).str.lower()
            column_names = [str(col).lower() for col in df.columns]

            if header_row.tolist() == column_names:
                df = df.iloc[1:]  # Remove duplicate header row

        return df

    def _format_tables(self, tables_data: Dict[str, List[pd.DataFrame]]):
        formatted_tables = {}
        for table_type, dfs in tables_data.items():
            formatted_tables[table_type] = []
            for df in dfs:
                # Convert DataFrame to JSON-serializable format
                formatted_tables[table_type].append({
                    "dataFrame": df,
                    "text": df.to_string(index=False),
                    "csv": df.to_csv(index=False),
                    "shape": df.shape,
                    "columns": df.columns.tolist()
                })
        return formatted_tables

    def _classify_tables(self, df: pd.DataFrame) -> str:
        headers = [str(col).lower() for col in df.columns]
        header_text = " ".join(headers)

        transaction_keywords = [
            "date",
            "description",
            "details",
            "amount",
            "balance",
            "debit",
            "credit",
        ]
        if any(word in header_text for word in transaction_keywords):
            return "transactions"

        summary_keywords = ["summary", "total", "balance", "opening", "closing"]
        if any(word in header_text for word in summary_keywords):
            return "account_summary"

        fee_keywords = ["fee", "charge", "interest", "penalty"]
        if any(word in header_text for word in fee_keywords):
            return "fees_table"

        return "raw_tables"
