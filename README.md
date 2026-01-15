# Auto-QA v2.0 - AI-Powered Web Testing Automation

**Enhanced multi-agent web testing system with parallel execution, resource monitoring, and git automation.**

Simply provide a URL and project description, and the system automatically generates and executes comprehensive test cases with autonomous parallel agent collaboration.

---

## 🎯 What It Does

### Core Features
- **🤖 AI-Powered Test Generation**: Analyzes project requirements and generates relevant test cases
- **👁️ Real-Time Visual Testing**: Headful mode with live screenshot streaming - watch tests execute in real browser
- **🔍 HTML Code Analysis**: Alternative testing mode - analyze HTML structure, accessibility, and semantics
- **🎭 Browser Automation**: Playwright-powered web automation for realistic user interactions

### v2.0 Enhancements ⚡
- **⚡ Async Parallel Execution**: True async/await with parallel agent execution (3-4x faster)
- **🧠 Smart Orchestration**: Enhanced orchestrator with dependency-aware task scheduling
- **📊 Resource Monitoring**: Real-time tracking of memory, CPU, and browser resources
- **🧹 Safe Cleanup**: Automatic resource cleanup on completion/failure/cancellation
- **📝 Git Auto-Commit**: Automatically commit and push test results to git
- **🔄 Background Task Manager**: Advanced async task management with health monitoring
- **🔀 Merge Points**: Intelligent result merging at parallel execution merge points
- **⚙️ Configurable Concurrency**: Adjustable max parallel agents (default: 4)

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Validate Setup

```bash
python3 validate.py
```

This checks:
- ✅ Docker installation and daemon
- ✅ Project structure
- ✅ Configuration files
- ✅ Port availability
- ✅ Git repository (for auto-commit)

### Step 2: Configure

```bash
cp .env.example .env
```

Edit `.env` to customize (defaults work for most cases):
```bash
# Enable features
ENABLE_PARALLEL=true        # Enable async parallel execution
MAX_PARALLEL_AGENTS=4       # Max parallel agents
ENABLE_GIT_AUTO_COMMIT=true  # Auto-commit test results

# Git configuration
GIT_REPO_PATH=.             # Path to git repo
GIT_BRANCH=main             # Branch to push to

# Resource limits
MAX_MEMORY_MB=4096         # Max memory per session
MAX_CPU_PERCENT=80          # Max CPU threshold
```

### Step 3: Start Services

```bash
docker-compose --profile ollama up -d
```

This starts:
- 🌐 Web UI at **http://localhost:3000**
- 🧠 Brain API at **http://localhost:9000**
- 🎭 Executor at **http://localhost:9001**
- 🤖 Ollama at **http://localhost:11434**
- 💾 Database at **localhost:15432**

### Step 4: Wait (30 seconds)

Wait for:
- Ollama to pull model (gemma3:1b)
- Database to initialize
- All services to be healthy

Check status:
```bash
docker-compose ps
```

### Step 5: Start Testing!

**Option A: Web Dashboard (Recommended)**
```bash
open http://localhost:3000
```

**Option B: Command Line**
```bash
python cli.py run https://example.com \
  --description "E-commerce website with shopping cart"
```

---

## 📖 Usage Guide

### Web Dashboard

1. Open **http://localhost:3000**
2. Enter **URL** to test
3. Provide **Domain Description** (what the website does)
4. Click **"🚀 Start Test"**
5. Watch tests execute in real-time with parallel agent activity
6. View detailed reports after completion
7. Git auto-commit automatically pushes results (if enabled)

**Example Domain Description**:
```markdown
E-commerce website with:
- User registration and login
- Product catalog with search and filtering
- Shopping cart functionality
- Checkout process with payment
- User account management

Critical user flows:
- New user registration
- Add items to cart
- Complete purchase
- View order history
```

### Command Line Interface

```bash
# Start test
python cli.py run https://example.com \
  --description "E-commerce site"

# Check status
python cli.py status

# Stop test
python cli.py stop
```

### API Usage

**Start Test**:
```bash
curl -X POST http://localhost:9000/start \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "domain_info": "E-commerce site"
  }'
```

**Get Real-Time Screenshot** (for web display):
```bash
curl -X POST http://localhost:9001/screenshot_base64 \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "full_page": false
  }'
```

**Get Progress**:
```bash
curl http://localhost:9001/progress/session-123
```

---

## 🏗️ System Architecture v2.0

```
┌─────────────────────────────────────────────────────┐
│                 Web UI Dashboard                │
│             (http://localhost:3000)            │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
┌────────▼────────┐  ┌─────▼───────────┐
│  Enhanced Brain  │  │  Playwright     │
│   (v2.0)       │  │  Executor       │
│                 │  │                 │
│  ┌───────────┐  │  │  Browser Pool   │
│  │ Orchestrator│  │  │  - Context 1   │
│  │            │  │  │  - Context 2   │
│  │ - Parallel │  │  │  - Context N   │
│  │   Groups   │  │  │               │
│  │ - Merge    │◄─┼──┤  Auto Cleanup  │
│  │   Points   │  │  │               │
│  └───────┬────┘  │  └───────────────┘
│          │       │
│  ┌───────┴─────┐ │
│  │  Agent Pool  │ │
│  │             │ │
│  │ - Navigation│ │
│  │ - Form      │ │
│  │ - Interaction│ │
│  │ - Verify    │ │
│  │ - HTML Analyzer│
│  │ - Merging   │
│  │ - Report    │ │
│  └─────────────┘ │
│                  │
│  ┌───────────────▼───────────┐
│  │  Background Task Manager    │
│  │  - Async execution        │
│  │  - Resource monitoring     │
│  │  - Safe cleanup          │
│  │  - Health checking        │
│  └───────────────────────────┘
│                  │
└──────────────────┼────────────────────┐
                   │                │
        ┌──────────▼─────────┐  ┌───▼──────────┐
        │   Task Manager    │  │  Git Manager  │
        │  - Concurrency    │  │  - Auto-commit │
        │  - Timeout       │  │  - Auto-push   │
        │  - Resource     │  │  - Branch     │
        │  - Cleanup      │  │  - History    │
        └───────────────────┘  └───────────────┘
                   │
        ┌──────────▼─────────┐
        │  Error Logger     │
        │  - Categorized   │
        │  - Severity      │
        │  - Traceback     │
        └──────────┬────────┘
                   │
        ┌──────────▼─────────┐
        │   PostgreSQL      │
        │   Database       │
        │  (localhost:15432)│
        └───────────────────┘
                   │
        ┌──────────▼─────────┐
        │    Ollama LLM     │
        │  (gemma3:1b)      │
        │ (localhost:11434)   │
        └───────────────────┘
```

---

## 📁 Project Structure

```
auto-qa/
├── apps/
│   ├── brain/                      # Enhanced Multi-Agent System
│   │   ├── src/
│   │   │   ├── agents/            # Agent implementations
│   │   │   │   ├── enhanced_orchestrator.py  # NEW: Async parallel orchestration
│   │   │   │   ├── orchestrator.py         # Legacy orchestrator
│   │   │   │   ├── navigation_agent.py     # Page navigation
│   │   │   │   ├── form_agent.py          # Form handling
│   │   │   │   ├── interaction_agent.py    # UI interactions
│   │   │   │   ├── verification_agent.py   # Result validation
│   │   │   │   ├── report_agent.py       # Report generation
│   │   │   │   ├── progress_tracker_agent.py # Progress & checklists
│   │   │   │   ├── html_analyzer_agent.py  # HTML analysis
│   │   │   │   ├── merging_agent.py       # Parallel result merging
│   │   │   │   └── base_agent.py         # Base class
│   │   │   ├── core/              # LLM client, prompts
│   │   │   │   ├── llm_client.py
│   │   │   │   ├── prompts.py       # All prompt templates
│   │   │   │   └── parser.py
│   │   │   ├── loop.py            # NEW: Enhanced orchestration loop
│   │   │   ├── config.py          # Configuration
│   │   │   └── main.py           # FastAPI entry point (v2.0)
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── executor/                   # Playwright automation
│   │   ├── src/
│   │   │   ├── automation/        # Browser management
│   │   │   │   ├── browser.py
│   │   │   │   └── actions.py
│   │   │   └── main.py           # FastAPI with all browser actions
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── web/                        # Dashboard UI
│       ├── src/
│       │   └── main.py             # FastAPI + Jinja2
│       ├── templates/
│       │   └── index.html
│       ├── Dockerfile
│       └── requirements.txt
├── libs/
│   ├── database/                   # Database operations
│   │   └── src/
│   │       ├── repositories/       # DB queries
│   │       │   ├── base.py
│   │       │   ├── session.py
│   │       │   ├── test_case.py
│   │       │   └── action_log.py
│   │       ├── repository.py
│   │       └── error_logger.py    # Enhanced error tracking
│   ├── task_manager/              # NEW: Background task management
│   │   └── src/
│   │       ├── task_manager.py    # Async task manager
│   │       └── __init__.py
│   └── git_automation/            # NEW: Git auto-commit/push
│       └── src/
│           ├── git_manager.py     # Git operations
│           └── __init__.py
├── cli.py                        # Command-line interface
├── validate.py                   # Pre-flight system checks
├── compose.yml                    # Docker Compose configuration
├── .env.example                  # Configuration template
└── README.md                     # This file
```

---

## ⚡ v2.0 Features

### 1. Async Parallel Execution

**How it works**:
- Multiple agents execute independently using async/await
- Dependency-aware task scheduling
- Parallel groups execute simultaneously
- Merge points coordinate results

**Benefits**:
- 🚀 3-4x faster for independent tests
- ⚡ Reduced idle time
- 💪 Better resource utilization
- 🎯 Task distribution and workload balancing

**Configuration**:
```bash
ENABLE_PARALLEL=true        # Enable parallel execution
MAX_PARALLEL_AGENTS=4       # Max parallel agents
```

### 2. Background Task Manager

**Features**:
- Async task execution with safe cleanup
- Resource tracking (memory, CPU, browsers)
- Health monitoring and auto-restart
- Graceful shutdown handling
- Timeout management

**Resource Monitoring**:
```python
{
  "memory_usage_mb": 512.3,
  "cpu_usage_percent": 25.6,
  "browser_contexts": ["ctx1", "ctx2"],
  "last_activity": "2025-01-15T22:30:00"
}
```

**Configuration**:
```bash
MAX_MEMORY_MB=4096         # Max memory per session
MAX_CPU_PERCENT=80          # Max CPU threshold
MONITOR_INTERVAL=5          # Monitoring interval (seconds)
```

### 3. Enhanced Orchestrator

**Improvements**:
- Dependency-aware task scheduling
- Parallel group execution
- Merge point identification
- Async/await throughout
- Resource-aware execution

**Task Dependencies**:
```json
{
  "tasks": [
    {"task_id": "navigate_home", "dependencies": []},
    {"task_id": "click_login", "dependencies": ["navigate_home"]},
    {"task_id": "fill_form", "dependencies": ["click_login"]},
    {"task_id": "verify_dashboard", "dependencies": ["fill_form"]}
  ],
  "parallel_groups": [
    ["navigate_home"],
    ["click_login", "verify_dashboard"]
  ]
}
```

### 4. Git Auto-Commit

**Features**:
- Automatic commit after test completion
- Meaningful commit messages with test summary
- Auto-push to configured branch
- Merge conflict handling

**Commit Message Format**:
```
✅ QA Test Results - 2025-01-15 22:30:00

Session ID: abc123
URL: https://example.com
Status: COMPLETED

Summary:
  test_cases: 15
  domain: E-commerce website with...
```

**Configuration**:
```bash
ENABLE_GIT_AUTO_COMMIT=true  # Enable git auto-commit
GIT_REPO_PATH=.             # Path to git repo
GIT_BRANCH=main             # Branch to push to
```

### 5. Safe Resource Cleanup

**What gets cleaned**:
- Browser contexts and pages
- Memory allocations
- Async tasks
- Temporary files
- Network connections

**Cleanup Triggers**:
- Task completion
- Task failure
- Task cancellation
- Timeout
- Manual stop

---

## 🧪 Testing Modes

### Mode 1: Visual Testing (Headful)

Watch tests execute in real-time browser window.

**How to enable**:
```bash
# Via API
curl -X POST http://localhost:9001/set_headful \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "headful": true
  }'

# Via CLI
python cli.py run https://example.com \
  --description "E-commerce site" \
  --visible
```

**Features**:
- ✅ See tests execute in real browser window
- ✅ Watch mouse movements, clicks, typing
- ✅ Real-time screenshot streaming (base64 for web display)
- ✅ Monitor each step as it happens
- ✅ Toggle headful/headless per session

### Mode 2: HTML Code Analysis

Analyze HTML structure instead of visual testing.

**How it works**:
```python
from apps.brain.src.agents.html_analyzer_agent import HTMLAnalyzerAgent

analyzer = HTMLAnalyzerAgent(session_id, llm)

# Full HTML analysis
action = {"action": "analyze_html"}
result = analyzer.execute(action)

# Accessibility check
action = {"action": "check_accessibility"}
result = analyzer.execute(action)
```

**Analysis types**:
- ✅ Full HTML analysis
- ✅ Accessibility (alt tags, ARIA, form labels)
- ✅ Structure validation (proper nesting, unclosed tags)
- ✅ Form validation (input types, required attributes)
- ✅ Semantic HTML (proper tag usage)
- ✅ Performance (inline scripts, large DOM)

### Mode 3: Parallel Agent Execution

Multiple agents work simultaneously for faster testing.

**How it works**:
```python
# Enhanced orchestrator handles parallel execution
orchestrator = EnhancedOrchestrator(
    session_id,
    llm,
    agents,
    max_parallel=4
)

# Execute with parallel groups and merge points
await orchestrator.orchestrate(url, domain_info, check_running)
```

**Benefits**:
- 🚀 3-4x faster for independent tests
- ⚡ Reduced idle time
- 💪 Better resource utilization
- 🎯 Task distribution and workload balancing

---

## 📊 Progress Tracking & Checklists

### Real-Time Progress

All progress tracked in files (not just memory):

```
/tmp/progress/
├── {session_id}_progress.json       # Detailed progress data
├── {session_id}_checklist.json      # Checklists for all test cases
└── {session_id}_collaboration.json  # Agent activity log
```

### Checklist Example

```
✅ Test case ready: Login
☐ Step 1: Navigate to login page
☐ Step 2: Enter username
☐ Step 3: Enter password
☐ Step 4: Click login button
✓ All validations passed
✓ Test case completed successfully
```

### Progress Dashboard

- 📈 Overall progress percentage
- ✅ Completed tests vs total
- ⏱️ Estimated time remaining
- 🤖 Current active agents (parallel count)
- 📝 Step-by-step status
- ✅ Checklist with checkboxes
- 📊 Resource usage (memory, CPU)

---

## 🔍 Error Tracking & Categorization

### Error Categories (10 types)

| Category | Description |
|-----------|-------------|
| `NAVIGATION` | Page navigation, URL routing errors |
| `ELEMENT_NOT_FOUND` | Selector errors, missing elements |
| `TIMEOUT` | Operation timeouts |
| `NETWORK` | Network-related failures |
| `FORM_VALIDATION` | Form submission, validation errors |
| `ACCESSIBILITY` | Accessibility issues found |
| `PERFORMANCE` | Performance-related errors |
| `LOGIC` | Agent logic errors |
| `CONFIGURATION` | Configuration issues |
| `UNKNOWN` | Uncategorized errors |

### Severity Levels (5 levels)

| Level | Description |
|-------|-------------|
| `CRITICAL` | System-breaking errors |
| `HIGH` | Major functionality failure |
| `MEDIUM` | Minor issues, workarounds exist |
| `LOW` | Cosmetic issues, warnings |
| `INFO` | Informational messages |

---

## 🎯 Micro-Test Generation

Tests broken down into atomic, granular steps:

**Example**:
```
Macro Test: "Login to account"
→ Micro Steps:
  1. Navigate to login page
  2. Verify login page title
  3. Enter username in username field
  4. Verify username field value
  5. Enter password in password field
  6. Verify password field value
  7. Click login button
  8. Verify redirect to dashboard
  9. Verify user name displayed
```

**Benefits**:
- ✅ Each step independently verifiable
- ✅ Precise error location identification
- ✅ Easy to track and debug
- ✅ Estimated time per step
- ✅ Priority-based execution

---

## ⚙️ Configuration

### Environment Variables

Edit `.env` to customize:

```bash
# Ports
WEB_PORT=3000              # Web UI
BRAIN_PORT=9000            # Brain API
EXECUTOR_PORT=9001         # Executor API
DB_PORT=15432              # Database

# Ollama LLM
OLLAMA_API_URL=http://ollama:11434  # Or external: http://host.docker.internal:11434
OLLAMA_PORT=11434

# LLM Model
LLM_MODEL=gemma3:1b        # Or: llama3:8b, mistral, etc.

# Database
DB_HOST=database
DB_NAME=qa_results
DB_USER=qa_user
DB_PASS=qa_password

# File Persistence
SCREENSHOT_DIR=/tmp/screenshots
PROGRESS_DIR=/tmp/progress
ERROR_LOG_DIR=/tmp/error_logs

# Execution Modes (v2.0)
DEFAULT_HEADFUL=false       # Enable headful by default
ENABLE_PARALLEL=true        # Enable parallel execution
MAX_PARALLEL_AGENTS=4       # Max parallel agents

# Git Auto-Commit (v2.0)
ENABLE_GIT_AUTO_COMMIT=true  # Auto-commit test results to git
GIT_REPO_PATH=.             # Path to git repository
GIT_BRANCH=main             # Branch to push to

# Resource Monitoring (v2.0)
MAX_MEMORY_MB=4096         # Max memory usage per session (MB)
MAX_CPU_PERCENT=80          # Max CPU usage threshold (%)
MONITOR_INTERVAL=5          # Resource monitoring interval (seconds)
```

### Changing LLM Model

```bash
# Edit .env
LLM_MODEL=llama3:8b

# Restart services
docker-compose restart brain executor
```

---

## 🔎 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f brain
docker-compose logs -f executor
docker-compose logs -f web
```

### Check Database

```bash
docker exec -it qa-database psql -U qa_user -d qa_results

# View sessions
SELECT * FROM sessions ORDER BY started_at DESC LIMIT 10;

# View test cases
SELECT * FROM test_cases WHERE session_id = '<session_id>';

# View actions
SELECT * FROM actions WHERE test_case_id = '<test_case_id>';
```

### View Progress Files

```bash
# Progress data
cat /tmp/progress/{session_id}_progress.json

# Checklists
cat /tmp/progress/{session_id}_checklist.json

# Agent collaboration log
cat /tmp/progress/{session_id}_collaboration.json

# Error logs
cat /tmp/error_logs/{session_id}_errors.json
cat /tmp/error_logs/{session_id}_error_summary.json
```

### Task Manager Status

```bash
# Check task manager statistics via brain API
curl http://localhost:9000/status
```

---

## 🔌 API Endpoints

### Brain API (Port 9000)

**Core Endpoints**:
- `POST /start` - Start new test
- `POST /stop` - Stop current test
- `GET /status` - Get test status
- `GET /health` - Health check (includes v2.0 features)

**Health Check Response**:
```json
{
  "status": "healthy",
  "service": "Enhanced Brain",
  "version": "2.0",
  "features": [
    "async_parallel_execution",
    "resource_monitoring",
    "safe_cleanup",
    "git_auto_commit"
  ]
}
```

### Web API (Port 3000)

- `GET /` - Dashboard UI
- `POST /api/start` - Start test (proxies to brain)
- `POST /api/stop` - Stop test (proxies to brain)
- `GET /api/status` - Get status (proxies to brain)
- `GET /api/sessions` - Get all sessions
- `GET /api/sessions/{id}` - Get session details

### Executor API (Port 9001)

**Browser Actions**:
- `POST /navigate` - Navigate to URL
- `POST /click` - Click element
- `POST /fill` - Fill form field
- `POST /select` - Select dropdown option
- `POST /submit` - Submit form
- `POST /drag` - Drag element
- `POST /scroll` - Scroll page

**Verification**:
- `POST /verify_text` - Verify text present
- `POST /verify_element` - Verify element exists
- `POST /verify_url` - Verify current URL
- `POST /verify_title` - Verify page title

**Enhanced Features**:
- `POST /set_headful` - Toggle visible mode
- `POST /screenshot` - Save screenshot to file
- `POST /screenshot_base64` - Get base64 screenshot
- `POST /get_html` - Capture HTML for analysis
- `POST /update_progress` - Update progress to file
- `GET /progress/{session_id}` - Get session progress

---

## 🤖 Agent Specifications

### EnhancedOrchestratorAgent ⚡ (NEW in v2.0)
- **Role**: Master coordinator with async parallel execution
- **Responsibilities**: Plan execution, coordinate agents, manage merge points
- **Features**:
  - Async/await throughout
  - Dependency-aware task scheduling
  - Parallel group execution
  - Merge point identification
  - Resource-aware execution

### NavigationAgent
- **Role**: Handles page navigation and URL routing
- **Actions**: Navigate, wait, screenshot
- **Enhancements**: Headful mode support, HTML capture

### FormAgent
- **Role**: Manages form filling and submission
- **Actions**: Fill, select, submit, validate
- **Features**: Form validation, error handling

### InteractionAgent
- **Role**: Handles UI interactions
- **Actions**: Click, hover, drag, double-click, scroll
- **Features**: Complex interaction support

### VerificationAgent
- **Role**: Validates test results and page states
- **Actions**: Verify text, element, URL, title, screenshot
- **Features**: Multiple verification types

### ProgressTrackerAgent ✨
- **Role**: Real-time progress tracking & checklist management
- **Features**:
  - Step-by-step status tracking
  - Checklist generation per test case
  - Overall progress percentage
  - Agent activity logging
  - File-based persistence
- **File Outputs**: progress.json, checklist.json, collaboration.json

### HTMLAnalyzerAgent ✨
- **Role**: Analyzes HTML structure and accessibility
- **Features**:
  - Full HTML analysis
  - Accessibility checking (alt tags, ARIA, labels)
  - Structure validation
  - Form validation
  - Semantic HTML checking
  - Performance analysis
- **Analysis Types**: 6 different analysis modes

### MergingAgent ✨
- **Role**: Combines parallel agent results
- **Features**:
  - Collect results from multiple agents
  - Detect and log conflicts
  - Merge results into unified dataset
  - Resolve conflicts intelligently
  - Validate merged results
  - Generate final report
- **Conflict Types**: Selector, status, data, timing conflicts

### ReportAgent
- **Role**: Generates comprehensive test reports
- **Features**:
  - Pass/fail status per test
  - Action-by-action logs
  - Screenshot evidence
  - Session-level summaries
- **Enhancements**: Agent collaboration logs, error summaries

### ErrorLogger ✨
- **Role**: Categorized error tracking
- **Features**:
  - 10+ error categories
  - 5 severity levels
  - Detailed traceback logging
  - Resolution tracking
  - Statistics and reporting
  - CSV export capability
- **File Outputs**: errors.json, error_summary.json

---

## 🔧 Troubleshooting

### Tests Not Starting

1. Check all services are running: `docker-compose ps`
2. Check logs: `docker-compose logs brain`
3. Verify Ollama is ready: `curl http://localhost:11434/api/tags`
4. Ensure database initialized: Check brain logs for "Database initialized"

### Git Auto-Commit Not Working

1. Verify git repository exists: `git status`
2. Check git permissions: Ensure write access to repo
3. Check .env configuration: `ENABLE_GIT_AUTO_COMMIT=true`
4. Verify git remote configured: `git remote -v`

### Parallel Execution Issues

1. Reduce max parallel agents: `MAX_PARALLEL_AGENTS=2`
2. Check system resource limits: Monitor memory/CPU
3. Review dependencies in execution plan
4. Monitor for conflicts in logs

### High Memory Usage

1. Reduce max parallel agents
2. Lower browser context count
3. Adjust `MAX_MEMORY_MB` in .env
4. Check for memory leaks in custom agents

### Headful Mode Not Working

1. Ensure VNC/X11 forwarding configured
2. Check DISPLAY environment variable
3. Verify browser supports headful mode
4. Try VNC remote viewing

### File Permission Errors

1. Ensure directories exist
2. Check write permissions
3. Verify volume mounts in Docker
4. Check disk space available

### Database Connection Issues

1. Check database is running: `docker-compose ps database`
2. Verify credentials in `.env`
3. Check database logs: `docker-compose logs database`
4. Manually test connection: `docker exec -it qa-database psql -U qa_user -d qa_results`

### Task Manager Issues

1. Check task manager stats via `/status` endpoint
2. Review monitoring logs
3. Verify cleanup handlers registered
4. Check for stale tasks: Monitor task list

---

## 📈 Performance Considerations

### Memory Usage

- Progress files: ~1-5 MB per session
- Error logs: ~500 KB per 100 errors
- Screenshots: ~500 KB each (full page: ~2-5 MB)
- HTML captures: ~100-500 KB each
- **v2.0 overhead**: Task manager ~50-100 MB, Resource monitoring ~10-20 MB

### I/O Operations

- Progress written after each step (minimal impact)
- Screenshots on demand (configurable frequency)
- Error logging async (non-blocking)
- File persistence ensures safety
- **v2.0 improvements**: Async writes reduce I/O blocking

### Parallel Execution Benefits

- 🚀 3-4x faster for independent tests
- ⚡ Reduced idle time
- 💪 Better resource utilization
- ⚠️ Requires more system resources
- **v2.0 optimizations**: Dependency-aware scheduling reduces waiting

### Resource Thresholds

Default thresholds:
- Memory: 4 GB per session
- CPU: 80% sustained usage
- Browsers: Unlimited (managed by Playwright)
- Timeout: 30 minutes per task

---

## 💻 Development

### Adding New Agents

1. Create new agent in `apps/brain/src/agents/`
2. Extend `BaseAgent` class
3. Implement `get_system_prompt()`, `get_description()`, and `execute()`
4. Add to enhanced orchestrator's agent list in `apps/brain/src/loop.py`

Example:
```python
from .base_agent import BaseAgent
import asyncio

class CustomAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are Custom Agent..."""

    def get_description(self) -> str:
        return "Custom Agent"

    async def execute_async(self, action: Dict) -> str:
        # Async implementation
        await asyncio.sleep(1)
        return "Result"

    def execute(self, action: Dict) -> str:
        # Sync wrapper
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(self.execute_async(action))
```

### Using Task Manager

```python
from libs.task_manager.src.task_manager import get_task_manager
import asyncio

async def my_background_task():
    # Your async code here
    await asyncio.sleep(10)
    return "Task completed"

# Create task
task_manager = get_task_manager(max_concurrent=4)
task_id = await task_manager.create_task(
    name="My Custom Task",
    coro=my_background_task,
    timeout=60.0
)

# Get status
status = task_manager.get_task_status(task_id)
print(f"Task status: {status}")
```

### Git Automation

```python
from libs.git_automation.src.git_manager import GitManager

# Initialize
git = GitManager(repo_path=".", branch="main")

# Auto commit and push
result = git.auto_commit_and_push(
    session_id="session-123",
    test_url="https://example.com",
    test_status="COMPLETED",
    summary={
        "test_cases": 15,
        "passed": 12,
        "failed": 3
    }
)

if result["success"]:
    print("Committed and pushed successfully!")
```

### File Persistence Pattern

All critical data should be written to files:

```python
# Progress tracking
import json
from pathlib import Path

progress_file = Path(f"/tmp/progress/{session_id}_progress.json")
progress_file.parent.mkdir(parents=True, exist_ok=True)

data = {"step": 1, "status": "completed"}
with open(progress_file, 'w') as f:
    json.dump(data, f, indent=2, default=str)
```

---

## 📄 License

MIT

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make your changes
4. Add tests if applicable
5. Test with `python3 validate.py`
6. Submit pull request

---

## 🆘 Support

For issues and questions:
- Review this README for detailed documentation
- Run `python3 validate.py` for diagnostics
- Check logs: `docker-compose logs`
- Review troubleshooting section above
- Monitor task manager status via API

---

## 🎉 v2.0 Changelog

### New Features
- ✅ Async parallel execution with 3-4x speed improvement
- ✅ Background task manager with safe cleanup
- ✅ Real-time resource monitoring (memory, CPU, browsers)
- ✅ Git auto-commit and auto-push
- ✅ Enhanced orchestrator with dependency-aware scheduling
- ✅ Merge points for parallel result coordination
- ✅ Health monitoring and auto-restart
- ✅ Graceful shutdown handling

### Improvements
- ⚡ Better concurrency handling
- 🧹 Safer resource cleanup
- 📊 Enhanced monitoring and observability
- 🔀 Improved parallel execution coordination
- 📝 Better error tracking and reporting

### Breaking Changes
- Requires Python 3.8+ (async support)
- New environment variables for v2.0 features
- Orchestrator API changed to async

---

**Ready to automate your web QA with enhanced parallel execution, resource monitoring, and git automation! 🚀**
