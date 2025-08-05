#!/usr/bin/env python3
"""
Quick script to check if new files are indexed in DeBot
"""
import os
import glob
from persona_manager import PersonaManager

def check_persona_files():
    """Check files in each persona directory"""
    pm = PersonaManager()
    
    for persona in pm.get_available_personas():
        pm.set_persona(persona)
        data_dir = pm.get_data_dir()
        
        print(f"\n📁 {persona.upper()} PERSONA:")
        print(f"   Data Directory: {data_dir}")
        
        # Check each subdirectory
        for subdir in ['mds', 'docs', 'pdfs']:
            dir_path = os.path.join(data_dir, subdir)
            if os.path.exists(dir_path):
                files = glob.glob(f"{dir_path}/*")
                print(f"   {subdir}/: {len(files)} files")
                
                # List recent files (last 5)
                if files:
                    files.sort(key=os.path.getmtime, reverse=True)
                    print(f"   Recent files:")
                    for f in files[:3]:
                        filename = os.path.basename(f)
                        print(f"     - {filename}")

def check_specific_file(filename):
    """Check if a specific file exists in any persona"""
    pm = PersonaManager()
    found = False
    
    for persona in pm.get_available_personas():
        pm.set_persona(persona)
        data_dir = pm.get_data_dir()
        
        for subdir in ['mds', 'docs', 'pdfs']:
            file_path = os.path.join(data_dir, subdir, filename)
            if os.path.exists(file_path):
                print(f"✅ Found {filename} in {persona}/{subdir}/")
                found = True
    
    if not found:
        print(f"❌ {filename} not found in any persona directory")

if __name__ == "__main__":
    print("🔍 DeBot File Check")
    print("=" * 50)
    
    # Check all persona files
    check_persona_files()
    
    # Check for specific file
    print(f"\n🎯 Checking for zoning_ncr.md:")
    check_specific_file("zoning_ncr.md")
    
    print(f"\n💡 To reindex after adding files:")
    print(f"   export FORCE_REINDEX=true")
    print(f"   python setup.py")