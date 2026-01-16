# libs/database/src/repositories/action_log.py
"""
Action Log Repository - Database operations for action logging.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from psycopg2.extras import RealDictCursor
from .base import get_db_connection
import logging

logger = logging.getLogger(__name__)


def log_action(
    test_case_id: str,
    action_type: str,
    selector: str = None,
    value: str = None,
    expected_result: str = None,
    actual_result: str = None,
    status: str = 'PENDING',
    error_message: str = None,
    screenshot_path: str = None,
    duration_ms: int = 0
) -> Optional[int]:
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO actions (
                        test_case_id, action_type, selector, value,
                        expected_result, actual_result, status,
                        error_message, screenshot_path, duration_ms
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                    RETURNING id
                """, (
                    test_case_id, action_type, selector, value,
                    expected_result, actual_result, status,
                    error_message, screenshot_path, duration_ms
                ))
                action_id = cur.fetchone()[0]
                return action_id
    except Exception as e:
        logger.error(f"Action log error: {e}")
        return None


def get_actions_by_test_case(test_case_id: str) -> List[Dict[str, Any]]:
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM actions 
                    WHERE test_case_id = %s 
                    ORDER BY created_at ASC
                """, (test_case_id,))
                results = []
                for row in cur.fetchall():
                    row_dict = dict(row)
                    for key, value in row_dict.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()
                    results.append(row_dict)
                return results
    except Exception as e:
        logger.error(f"Actions by test case query error: {e}")
    return []


def get_actions(limit: int = 100) -> List[Dict[str, Any]]:
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM actions 
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
        logger.error(f"Actions query error: {e}")
    return []


def get_latest_actions(session_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if session_id:
                    cur.execute("""
                        SELECT a.* FROM actions a
                        JOIN test_cases tc ON a.test_case_id = tc.id
                        WHERE tc.session_id = %s
                        ORDER BY a.created_at DESC
                        LIMIT %s
                    """, (session_id, limit))
                else:
                    cur.execute("""
                        SELECT * FROM actions 
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
        logger.error(f"Latest actions query error: {e}")
    return []
