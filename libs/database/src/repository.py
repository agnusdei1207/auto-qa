# libs/database/src/repository.py
"""
Central Database Repository - Unified API for all database operations.
"""
from .repositories.base import (
    get_connection_pool, get_db_connection, get_connection, init_database
)
from .repositories.session import (
    create_session, update_session_status, end_session,
    get_session, get_all_sessions
)
from .repositories.test_case import (
    create_test_case, update_test_case_status, get_test_cases,
    get_test_case_by_id, get_test_cases_by_session
)
from .repositories.action_log import (
    log_action, get_actions, get_actions_by_test_case,
    get_latest_actions
)

__all__ = [
    # Base
    'get_connection_pool', 'get_db_connection', 'get_connection', 'init_database',
    # Session
    'create_session', 'update_session_status', 'end_session',
    'get_session', 'get_all_sessions',
    # Test Case
    'create_test_case', 'update_test_case_status', 'get_test_cases',
    'get_test_case_by_id', 'get_test_cases_by_session',
    # Action Log
    'log_action', 'get_actions', 'get_actions_by_test_case',
    'get_latest_actions'
]
