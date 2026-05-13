"""
Database Query Tool (Moved to tools/)
"""
import sqlite3
import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config import DB_PATH

def run_query(sql):
    try:
        import pandas as pd
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        print(df.to_string(index=False))
        conn.close()
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")

if __name__ == "__main__":
    print("--- AGO Database Query Tool ---")
    while True:
        query = input("\nSQL (hoặc 'exit'): ")
        if query.lower() in ['exit', 'q']: break
        run_query(query)
