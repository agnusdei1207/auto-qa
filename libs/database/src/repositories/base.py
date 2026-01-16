# libs/database/src/repositories/base.py
"""
Database Core - Connection Pool and Schema Management.
"""
import os
import time
import logging
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from threading import Lock
from typing import Optional, Generator, Any

logger = logging.getLogger(__name__)

DB_PARAMS = {
    'host': os.environ.get('DB_HOST', 'database'),
    'database': os.environ.get('DB_NAME', 'qa_results'),
    'user': os.environ.get('DB_USER', 'qa_user'),
    'password': os.environ.get('DB_PASS', 'qa_password')
}

_connection_pool: Optional[psycopg2.pool.SimpleConnectionPool] = None
_pool_lock = Lock()


def get_connection_pool() -> Optional[psycopg2.pool.SimpleConnectionPool]:
    global _connection_pool
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                try:
                    logger.info("Initializing database connection pool...")
                    _connection_pool = psycopg2.pool.SimpleConnectionPool(
                        minconn=1,
                        maxconn=10,
                        **DB_PARAMS
                    )
                except Exception as e:
                    logger.critical(f"Failed to create connection pool: {e}")
                    return None
    return _connection_pool


@contextmanager
def get_db_connection() -> Generator[Any, None, None]:
    pool = get_connection_pool()
    conn = None
    try:
        if pool:
            conn = pool.getconn()
        else:
            conn = psycopg2.connect(**DB_PARAMS)
        
        if not conn:
            raise psycopg2.Error("Failed to secure database connection")
        
        yield conn
        if conn:
            conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            if pool:
                pool.putconn(conn)
            else:
                conn.close()


def get_connection():
    return psycopg2.connect(**DB_PARAMS)


def init_database(max_retries: int = 30, retry_delay: int = 5) -> bool:
    logger.info("Initializing database schema...")
    conn = None
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cur = conn.cursor()
            
            # Sessions Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    url TEXT NOT NULL,
                    domain_info TEXT,
                    status TEXT DEFAULT 'PENDING',
                    current_agent TEXT DEFAULT 'NONE',
                    started_at TIMESTAMP DEFAULT NOW(),
                    ended_at TIMESTAMP,
                    notes TEXT
                );
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON sessions(started_at DESC);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status_started ON sessions(status, started_at DESC);")
            
            # Test Cases Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_cases (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP
                );
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_test_cases_session ON test_cases(session_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_test_cases_status ON test_cases(status);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_test_cases_session_status ON test_cases(session_id, status);")
            
            # Actions Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS actions (
                    id SERIAL PRIMARY KEY,
                    test_case_id UUID REFERENCES test_cases(id) ON DELETE CASCADE,
                    action_type TEXT NOT NULL,
                    selector TEXT,
                    value TEXT,
                    expected_result TEXT,
                    actual_result TEXT,
                    status TEXT DEFAULT 'PENDING',
                    error_message TEXT,
                    screenshot_path TEXT,
                    duration_ms INTEGER,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_actions_test_case ON actions(test_case_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_actions_status ON actions(status);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_actions_test_case_status ON actions(test_case_id, status);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_actions_created_at ON actions(created_at DESC);")
            
            # Test Logs Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_logs (
                    id SERIAL PRIMARY KEY,
                    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
                    level TEXT NOT NULL,
                    message TEXT,
                    agent TEXT,
                    timestamp TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_logs_session ON test_logs(session_id);")
            
            conn.commit()
            logger.info("Database schema initialized")
            return True
        
        except Exception as e:
            logger.warning(f"Schema initialization warning (Attempt {attempt+1}/{max_retries}): {e}")
            if conn:
                conn.rollback()
            time.sleep(retry_delay)
        finally:
            if conn:
                conn.close()
                conn = None
    
    logger.error("Failed to initialize database schema after multiple attempts.")
    return False
