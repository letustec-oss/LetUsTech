# ⚡ Invoice Generator
**Version 2.2.0 — Free Desktop Invoice Tool**
*Made in Liverpool by LetUsTech — letustech.uk*

---

## 🚀 Quick Start

### Option A — Run directly with Python (Recommended)
1. Make sure Python 3.8+ is installed → https://python.org
2. Install dependencies:
   ```
   pip install reportlab Pillow
   ```
3. Double-click `Launch_Invoice_Generator.bat` (Windows)
   OR run: `python invoice_app.py`

### Option B — Build a standalone .exe
1. Install PyInstaller: `pip install pyinstaller`
2. Run: `python build_exe.py`
3. Your `.exe` will be in the `/dist` folder — no Python needed to run it!

---

## ✨ Features
- 📄 Professional PDF invoice export
- 🏢 Full company branding (name, address, VAT, bank details)
- 👤 Client details & billing address
- 📦 Line items with quantity, unit price, per-item tax toggle
- 💰 Automatic subtotal, VAT/tax, discount & grand total
- 🔢 Auto-incrementing invoice numbers
- 📁 Invoice history log
- ⚙️ Full settings panel (currency, tax rate, date format, accent colour, etc.)
- ❓ Built-in help & tutorial
- 💾 100% offline — your data never leaves your machine

---

## 📁 File Structure
```
invoice_generator/
├── invoice_app.py          ← Main application
├── Launch_Invoice_Generator.bat  ← Windows launcher
├── build_exe.py            ← Build to standalone .exe
├── requirements.txt        ← Python dependencies
└── README.md               ← This file
```

Settings & history are saved to:
`C:\Users\YourName\.invoice_generator_data\`

---

## 🛠️ Built With
- Python 3 + Tkinter (UI)
- ReportLab (PDF generation)
- Pillow (image support)

---

*LetUsTech — Free tools for everyone. letustech.uk*
