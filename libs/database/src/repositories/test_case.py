# libs/database/src/repositories/test_case.py
"""
Test Case Repository - Database operations for test cases.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from psycopg2.extras import RealDictCursor
from .base import get_db_connection
import logging

logger = logging.getLogger(__name__)


def create_test_case(session_id: str, name: str, description: str = None) -> Optional[str]:
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO test_cases (session_id, name, description) VALUES (%s, %s, %s) RETURNING id",
                    (session_id, name, description)
                )
                test_case_id = str(cur.fetchone()[0])
                return test_case_id
    except Exception as e:
        logger.error(f"Test case creation error: {e}")
        return None


def update_test_case_status(test_case_id: str, status: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if status == 'COMPLETED':
                    cur.execute(
                        "UPDATE test_cases SET status = %s, completed_at = NOW() WHERE id = %s",
                        (status, test_case_id)
                    )
                else:
                    cur.execute(
                        "UPDATE test_cases SET status = %s WHERE id = %s",
                        (status, test_case_id)
                    )
    except Exception as e:
        logger.error(f"Test case status update error: {e}")


def get_test_case_by_id(test_case_id: str) -> Optional[Dict[str, Any]]:
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM test_cases WHERE id = %s", (test_case_id,))
                row = cur.fetchone()
                if row:
                    row_dict = dict(row)
                    for key, value in row_dict.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()
                    return row_dict
    except Exception as e:
        logger.error(f"Test case query error: {e}")
    return None


def get_test_cases_by_session(session_id: str) -> List[Dict[str, Any]]:
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM test_cases 
                    WHERE session_id = %s 
                    ORDER BY created_at ASC
                """, (session_id,))
                results = []
                for row in cur.fetchall():
                    row_dict = dict(row)
                    for key, value in row_dict.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()
                    results.append(row_dict)
                return results
    except Exception as e:
        logger.error(f"Test cases by session query error: {e}")
    return []


def get_test_cases(limit: int = 100) -> List[Dict[str, Any]]:
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM test_cases 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
                results = []
                for row in cur.fetchall():
                    row_dict = dict(row)
                    for key, value in row_dict.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()
                    results.append(row_dict)
                return results
    except Exception as e:
        logger.error(f"Test cases query error: {e}")
    return []
