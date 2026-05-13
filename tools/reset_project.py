"""
Script dọn dẹp dự án (Moved to tools/)
"""
import os
import sys
from pathlib import Path

# Đảm bảo đường dẫn đúng
ROOT_DIR = Path(__file__).resolve().parent.parent
os.chdir(ROOT_DIR)

def reset_project():
    print("--- DANG DON DEP DU AN AGO FRUIT ---")
    
    db_file = ROOT_DIR / "extraction.db"
    if db_file.exists():
        try:
            os.remove(db_file)
            print(f"Xoa database: {db_file}")
        except:
            print("Khong the xoa database (dang mo).")

    for dir_name in ["sample_input", "output"]:
        d = ROOT_DIR / dir_name
        if d.exists():
            for f in d.glob("*.*"):
                os.remove(f)
            print(f"Da don dep {dir_name}/")

    junk = ["test_page_1.png", "temp_upload.pdf", "bang_ke_nhap_lieu.xlsx"]
    for f_name in junk:
        f_path = ROOT_DIR / f_name
        if f_path.exists():
            os.remove(f_path)
            print(f"Xoa file tam: {f_name}")

if __name__ == "__main__":
    reset_project()
