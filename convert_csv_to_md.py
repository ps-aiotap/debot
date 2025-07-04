import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from context_tags import get_context_tags

load_dotenv()

def convert_csv_to_md():
    """Convert test case CSVs to markdown files using Step Action and Step Expected columns."""
    
    excel_dir = os.getenv('EXCEL_DIR', './data/excel')
    mds_dir = os.getenv('MDS_DIR', './data/mds')
    
    excel_path = Path(excel_dir)
    mds_path = Path(mds_dir)
    
    # Create MDS directory if it doesn't exist
    mds_path.mkdir(parents=True, exist_ok=True)
    
    if not excel_path.exists():
        print(f"Excel directory not found: {excel_dir}")
        return
    
    csv_files = list(excel_path.rglob("*.csv"))
    print(f"Found {len(csv_files)} CSV files to convert")
    
    for csv_file in csv_files:
        try:
            print(f"Converting {csv_file.name}...")
            
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Create markdown content with enhanced context
            md_content = f"# Business Requirements: {csv_file.stem.replace('_', ' ')}\n\n"
            md_content += f"**Source:** Test cases from {csv_file.name}\n"
            md_content += f"**Domain:** DHHS Acquisition Tool\n"
            md_content += f"**Module:** {csv_file.stem.split('_')[0] if '_' in csv_file.stem else 'General'}\n\n"
            md_content += "## Overview\n"
            md_content += f"This document contains business requirements extracted from test cases for the {csv_file.stem.replace('_', ' ')} functionality.\n\n"
            
            # Process each row
            requirement_count = 0
            for index, row in df.iterrows():
                step_action = ""
                step_expected = ""
                title = ""
                
                # Extract relevant columns
                if 'Title' in df.columns and pd.notna(row['Title']):
                    title = str(row['Title']).strip()
                
                if 'Step Action' in df.columns and pd.notna(row['Step Action']):
                    step_action = str(row['Step Action']).strip()
                
                if 'Step Expected' in df.columns and pd.notna(row['Step Expected']):
                    step_expected = str(row['Step Expected']).strip()
                
                # Only create requirement if we have action or expected content
                if step_action or step_expected:
                    requirement_count += 1
                    md_content += f"## Business Requirement {requirement_count}\n\n"
                    
                    if title:
                        md_content += f"**Feature:** {title}\n\n"
                    
                    if step_action:
                        md_content += f"**User Workflow:**\n{step_action}\n\n"
                    
                    if step_expected:
                        md_content += f"**System Behavior:**\n{step_expected}\n\n"
                    
                    # Add contextual tags based on content
                    content_text = f"{title} {step_action} {step_expected}"
                    context_tags = get_context_tags(content_text)
                    
                    if context_tags:
                        md_content += f"**Context Tags:** {', '.join(context_tags)}\n\n"
                    
                    md_content += "---\n\n"
            
            # Write markdown file
            if requirement_count > 0:
                md_filename = f"{csv_file.stem}_requirements.md"
                md_filepath = mds_path / md_filename
                
                with open(md_filepath, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                print(f"  Created {md_filename} with {requirement_count} requirements")
            else:
                print(f"  No Step Action/Expected content found in {csv_file.name}")
                
        except Exception as e:
            print(f"Error converting {csv_file.name}: {e}")

if __name__ == "__main__":
    convert_csv_to_md()
    print("\nConversion complete! Run 'python simple_main.py' to index the new markdown files.")