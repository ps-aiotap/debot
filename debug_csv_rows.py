import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

excel_dir = os.getenv('EXCEL_DIR', './data/excel')
excel_path = Path(excel_dir)

for csv_file in excel_path.rglob("*.csv"):
    print(f"\n--- Checking all rows in {csv_file.name} ---")
    df = pd.read_csv(csv_file)
    
    step_cols = ['Test Step', 'Step Action', 'Step Expected']
    
    print("Rows with content in step columns:")
    for index, row in df.iterrows():
        has_step_content = False
        step_content = ""
        
        for col in step_cols:
            if col in df.columns and pd.notna(row[col]) and str(row[col]).strip():
                has_step_content = True
                step_content += f"{col}: {str(row[col])[:100]}... "
        
        if has_step_content:
            print(f"Row {index}: {row['Title'][:50]}...")
            print(f"  {step_content}")
            if index >= 5:  # Show first 5 rows with content
                break
    
    # Count non-empty step rows
    non_empty_steps = 0
    for col in step_cols:
        if col in df.columns:
            non_empty_count = df[col].notna().sum() - (df[col] == '').sum()
            print(f"{col}: {non_empty_count} non-empty rows")
            non_empty_steps = max(non_empty_steps, non_empty_count)