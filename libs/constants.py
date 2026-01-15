# === Port Constants ===
WEB_PORT = 3000          # Web UI
BRAIN_PORT = 9000        # AI Brain (Multi-Agent System)
EXECUTOR_PORT = 9001     # Web Automation Executor Service
OLLAMA_PORT = 11434      # Ollama LLM (standard)
DB_PORT = 15432          # PostgreSQL (avoid conflict with redteam)

# === Timeout Constants (seconds) ===
TIMEOUT_BROWSER_INIT = 60      # 1 min - browser initialization
TIMEOUT_PAGE_LOAD = 30         # 30 sec - page load
TIMEOUT_ACTION = 60            # 1 min - single action (click, fill, etc.)
TIMEOUT_VERIFICATION = 30     # 30 sec - verification step
TIMEOUT_LLM_REQUEST = 300      # 5 min - LLM response wait
TIMEOUT_QUICK = 10             # 10 sec - quick commands

# === Service Hostnames (Docker network) ===
WEB_HOST = "web"
BRAIN_HOST = "brain"
EXECUTOR_HOST = "executor"
OLLAMA_HOST = "ollama"
DB_HOST = "database"

# === Helper URL Functions ===
def get_web_url() -> str:
    return f"http://{WEB_HOST}:{WEB_PORT}"


def get_brain_url() -> str:
    return f"http://{BRAIN_HOST}:{BRAIN_PORT}"


def get_executor_url() -> str:
    return f"http://{EXECUTOR_HOST}:{EXECUTOR_PORT}"


def get_ollama_url() -> str:
    return f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
