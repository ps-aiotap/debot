import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

excel_dir = os.getenv('EXCEL_DIR', './data/excel')
print(f"Checking CSV files in: {excel_dir}")

excel_path = Path(excel_dir)
if not excel_path.exists():
    print("Excel directory doesn't exist!")
else:
    csv_files = list(excel_path.rglob("*.csv"))
    print(f"Found {len(csv_files)} CSV files:")
    
    for csv_file in csv_files:
        print(f"\n--- {csv_file.name} ---")
        try:
            df = pd.read_csv(csv_file)
            print(f"Columns: {list(df.columns)}")
            print(f"Rows: {len(df)}")
            
            # Show first row content
            if len(df) > 0:
                print("\nFirst row content:")
                for col in df.columns:
                    value = df.iloc[0][col]
                    if pd.notna(value):
                        print(f"  {col}: {str(value)[:100]}...")
                
                # Check if 'Step Expected' or similar columns exist
                step_cols = [col for col in df.columns if 'step' in col.lower() or 'expected' in col.lower()]
                if step_cols:
                    print(f"\nStep/Expected columns found: {step_cols}")
                    for col in step_cols:
                        sample_value = df.iloc[0][col] if pd.notna(df.iloc[0][col]) else "Empty"
                        print(f"  {col} sample: {str(sample_value)[:200]}...")
                
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")