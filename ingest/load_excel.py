import pandas as pd
from typing import List, Dict
from pathlib import Path

def load_excel_testcases(excel_dir: str) -> List[Dict[str, str]]:
    """Load test cases from Excel and CSV files as business knowledge."""
    documents = []
    excel_path = Path(excel_dir)
    
    if not excel_path.exists():
        return documents
    
    # Process both Excel and CSV files
    for file_path in list(excel_path.rglob("*.xlsx")) + list(excel_path.rglob("*.csv")):
        try:
            # Handle CSV and Excel files differently
            if file_path.suffix.lower() == '.csv':
                # Read CSV file
                df = pd.read_csv(file_path)
                sheet_name = file_path.stem  # Use filename as sheet name
                sheets_data = [(sheet_name, df)]
            else:
                # Read Excel file with all sheets
                excel_file = pd.ExcelFile(file_path)
                sheets_data = [(sheet_name, pd.read_excel(file_path, sheet_name=sheet_name)) 
                              for sheet_name in excel_file.sheet_names]
            
            for sheet_name, df in sheets_data:
                
                # Create business knowledge document
                content = f"Business Knowledge from Test Cases: {sheet_name}\n"
                content += f"Source: {file_path.name}\n\n"
                
                # Extract business rules and workflows
                content += "BUSINESS REQUIREMENTS AND RULES:\n"
                content += "=" * 40 + "\n\n"
                
                # Process each test case as a business requirement
                for index, row in df.iterrows():
                    test_case = f"Test Case {index + 1}:\n"
                    
                    # Extract key business information
                    has_content = False
                    for col in df.columns:
                        if pd.notna(row[col]) and str(row[col]).strip():
                            col_lower = col.lower()
                            value = str(row[col]).strip()
                            has_content = True
                            
                            # Business-focused field mapping
                            if any(keyword in col_lower for keyword in ['title', 'description', 'scenario', 'requirement', 'feature']):
                                test_case += f"Business Scenario: {value}\n"
                            elif any(keyword in col_lower for keyword in ['step', 'action', 'procedure']):
                                test_case += f"Business Process: {value}\n"
                            elif any(keyword in col_lower for keyword in ['expected', 'result', 'outcome']):
                                test_case += f"Business Rule: {value}\n"
                            elif any(keyword in col_lower for keyword in ['condition', 'criteria', 'validation']):
                                test_case += f"Business Validation: {value}\n"
                            elif any(keyword in col_lower for keyword in ['user', 'role', 'actor', 'assigned']):
                                test_case += f"Business Actor: {value}\n"
                            elif any(keyword in col_lower for keyword in ['data', 'input', 'parameter']):
                                test_case += f"Business Data: {value}\n"
                            elif col_lower not in ['id', 'work item type', 'state']:
                                test_case += f"{col}: {value}\n"
                    
                    # Only add test cases that have meaningful content
                    if has_content:
                        test_case += "\n" + "-" * 50 + "\n\n"
                        content += test_case
                
                # Add summary section
                content += "\nBUSINESS SUMMARY:\n"
                content += f"This module contains {len(df)} business scenarios covering functional requirements.\n"
                content += f"Key business areas: {sheet_name}\n"
                
                documents.append({
                    'content': content,
                    'source': f"{file_path}#{sheet_name}",
                    'filename': f"Business Knowledge - {file_path.name} - {sheet_name}",
                    'type': 'business_knowledge'
                })
                
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
    
    return documents