"""
Build Invoice Generator into a standalone Windows .exe
Run this script once to produce dist/Invoice_Generator.exe

Requirements:
    pip install pyinstaller reportlab pillow
"""

import subprocess
import sys
import os

def build():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "Invoice_Generator",
        "--icon", "NONE",
        "--add-data", "requirements.txt;.",
        "invoice_app.py"
    ]
    print("Building exe... this may take a minute.")
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    if result.returncode == 0:
        print("\n✅ Build complete!")
        print("Your exe is in the /dist folder.")
    else:
        print("\n❌ Build failed. Make sure PyInstaller is installed:")
        print("   pip install pyinstaller")

if __name__ == "__main__":
    build()
