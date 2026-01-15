# Auto-QA Environment Context

## INFRA
- **Type**: Docker Compose
- **Base**: Python 3.13-slim-bookworm
- **Existing Ports (redteam)**:
  - Web UI: 80
  - Brain: 8000
  - Executor: 8001
  - Ollama: 11434
  - Database: 5432
- **Constraint**: Must use different ports to avoid conflicts

## DOMAIN
- **Type**: Web Automation QA System
- **Purpose**: User simulation testing (drag, form input, click events)
- **Input**: Website URL + Markdown domain info
- **Output**: Automated web testing and verification

## STACK
- **Language**: Python 3.13
- **Framework**: FastAPI
- **Database**: PostgreSQL 18-alpine
- **LLM**: Ollama gemma3:1b (same as redteam)
- **Web Automation**: Playwright (recommended for modern web)
- **Architecture**: Multi-agent system (similar to redteam)

## PROJECT STRUCTURE (based on redteam)
```
.
├── apps/
│   ├── brain/           # Multi-agent orchestration
│   ├── executor/        # Web automation execution (Playwright)
│   └── web/             # FastAPI + Dashboard UI
├── libs/
│   ├── database/        # Shared repositories & models
│   └── constants/       # Shared configuration
└── compose.yml          # Docker Compose orchestration
```

## AGENT TYPES (for QA testing)
- **OrchestratorAgent**: Master coordinator
- **NavigationAgent**: Page navigation and URL handling
- **FormAgent**: Form filling and validation
- **InteractionAgent**: Click, drag, hover events
- **VerificationAgent**: Test result validation
- **ReportAgent**: Generate test reports

## KEY REQUIREMENTS
1. Port conflict avoidance (use different ports than redteam)
2. Markdown parsing for domain instructions
3. Playwright for web automation
4. Real-time dashboard for test monitoring
5. Database logging for test history
6. Multi-agent coordination similar to redteam

## CONFIGURATION
- **Web UI Port**: 3000 (avoid conflict with 80)
- **Brain API Port**: 9000 (avoid conflict with 8000)
- **Executor API Port**: 9001 (avoid conflict with 8001)
- **Ollama Port**: 11434 (shared service)
- **Database Port**: 15432 (avoid conflict with 5432)
