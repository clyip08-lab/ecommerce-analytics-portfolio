# scripts/verify_setup.py
# ============================================================
# PHASE 0 - Verification Script
# Run this to confirm everything is installed correctly
# ============================================================

import sys
print("=" * 55)
print("  E-COMMERCE ANALYTICS PORTFOLIO - SETUP VERIFICATION")
print("=" * 55)

# --- Check Python version ---
print(f"\n✅ Python Version : {sys.version.split()[0]}")

# --- Check all libraries ---
libraries = {
    "pandas"       : "pd",
    "numpy"        : "np",
    "plotly"       : "plotly",
    "matplotlib"   : "matplotlib",
    "seaborn"      : "sns",
    "sklearn"      : "scikit-learn",
    "sqlalchemy"   : "sqlalchemy",
    "pymysql"      : "pymysql",
    "dotenv"       : "python-dotenv",
    "tqdm"         : "tqdm",
    "openpyxl"     : "openpyxl",
    "streamlit"    : "streamlit",
    "jupyter"      : "jupyter",
}

all_good = True
for lib, display_name in libraries.items():
    try:
        __import__(lib)
        print(f"  ✅ {display_name:<20} installed")
    except ImportError:
        print(f"  ❌ {display_name:<20} MISSING — run: pip install {display_name}")
        all_good = False

# --- Check data files exist ---
import os
print("\n--- Checking Data Files ---")
raw_files = [
    r"C:\Users\yipch\ecommerce-analytics-portfolio\data\raw\2019-Oct.csv",
    r"C:\Users\yipch\ecommerce-analytics-portfolio\data\raw\2019-Nov.csv",
]
for f in raw_files:
    if os.path.exists(f):
        size_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"  ✅ Found : {os.path.basename(f)}  ({size_mb:.1f} MB)")
    else:
        print(f"  ❌ MISSING : {f}")
        all_good = False

# --- Check folder structure ---
print("\n--- Checking Folder Structure ---")
base = r"C:\Users\yipch\ecommerce-analytics-portfolio"
folders = [
    "data/raw", "data/processed", "data/samples", "data/exports",
    "notebooks", "scripts", "sql", "dashboard",
    "streamlit_app", "reports/figures"
]
for folder in folders:
    full_path = os.path.join(base, folder.replace("/", os.sep))
    if os.path.isdir(full_path):
        print(f"  ✅ {folder}")
    else:
        print(f"  ❌ Missing folder: {folder}")
        all_good = False

# --- Final result ---
print("\n" + "=" * 55)
if all_good:
    print("  🎉 ALL CHECKS PASSED! You are ready for PHASE 1.")
else:
    print("  ⚠️  Some checks failed. Fix the ❌ items above first.")
print("=" * 55)