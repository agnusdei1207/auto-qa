# libs/database/src/repositories/session.py
"""
Session Repository - Database operations for test sessions.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from psycopg2.extras import RealDictCursor
from .base import get_db_connection
import logging

logger = logging.getLogger(__name__)


def create_session(url: str, domain_info: str = None) -> Optional[str]:
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO sessions (url, domain_info) VALUES (%s, %s) RETURNING id",
                    (url, domain_info)
                )
                session_id = str(cur.fetchone()[0])
                return session_id
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        return None


def update_session_status(session_id: str, status: str, current_agent: str = None):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if current_agent:
                    cur.execute(
                        "UPDATE sessions SET status = %s, current_agent = %s WHERE id = %s",
                        (status, current_agent, session_id)
                    )
                else:
                    cur.execute(
                        "UPDATE sessions SET status = %s WHERE id = %s",
                        (status, session_id)
                    )
    except Exception as e:
        logger.error(f"Session status update error: {e}")


def end_session(session_id: str, status: str = 'COMPLETED', notes: str = None):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE sessions SET status = %s, ended_at = NOW(), notes = %s WHERE id = %s",
                    (status, notes, session_id)
                )
    except Exception as e:
        logger.error(f"Session end error: {e}")


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sessions WHERE id = %s", (session_id,))
                row = cur.fetchone()
                if row:
                    row_dict = dict(row)
                    for key, value in row_dict.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()
                    return row_dict
    except Exception as e:
        logger.error(f"Session query error: {e}")
    return None


def get_all_sessions(limit: int = 50) -> List[Dict[str, Any]]:
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM sessions 
                    ORDER BY started_at DESC 
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
        logger.error(f"All sessions query error: {e}")
    return []
