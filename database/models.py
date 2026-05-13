"""
Quản lý SQLite để lưu trữ lịch sử trích xuất và nhật ký kiểm toán (Audit Log).
Sử dụng thư viện sqlite3 có sẵn của Python.
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import DB_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Khởi tạo các bảng nếu chưa tồn tại."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Bảng lưu thông tin chứng từ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    document_type TEXT,
                    overall_confidence REAL,
                    status TEXT DEFAULT 'pending',
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    token_usage_input INTEGER,
                    token_usage_output INTEGER,
                    raw_data_json TEXT
                )
            ''')

            # Bảng lưu nhật ký thay đổi (Audit Log)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    user TEXT DEFAULT 'system',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            ''')
            conn.commit()
            logger.info("Database initialized at %s", self.db_path)

    def save_extraction(self, result: Any) -> int:
        """Lưu kết quả trích xuất mới."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documents (
                    filename, document_type, overall_confidence, 
                    status, token_usage_input, token_usage_output, raw_data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.filename,
                result.document_type.value,
                result.overall_confidence,
                'reviewed' if not result.needs_review else 'pending',
                result.token_usage.get('input', 0),
                result.token_usage.get('output', 0),
                json.dumps(result.data, ensure_ascii=False)
            ))
            doc_id = cursor.lastrowid
            
            # Log action
            cursor.execute('''
                INSERT INTO audit_logs (document_id, action, details)
                VALUES (?, ?, ?)
            ''', (doc_id, 'extraction_completed', f"Confidence: {result.overall_confidence}"))
            
            conn.commit()
            return doc_id

    def update_document_data(self, doc_id: int, new_data: Dict, user: str = "user"):
        """Cập nhật dữ liệu sau khi người dùng review."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE documents 
                SET raw_data_json = ?, status = 'approved'
                WHERE id = ?
            ''', (json.dumps(new_data, ensure_ascii=False), doc_id))
            
            cursor.execute('''
                INSERT INTO audit_logs (document_id, action, user, details)
                VALUES (?, ?, ?, ?)
            ''', (doc_id, 'data_updated_manual', user, "Manual review and approval"))
            conn.commit()

    def get_all_documents(self) -> List[Dict]:
        """Lấy danh sách tất cả chứng từ."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM documents ORDER BY upload_time DESC')
            return [dict(row) for row in cursor.fetchall()]

    def get_audit_logs(self, doc_id: int) -> List[Dict]:
        """Lấy log của một chứng từ cụ thể."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM audit_logs WHERE document_id = ? ORDER BY timestamp DESC', (doc_id,))
            return [dict(row) for row in cursor.fetchall()]
