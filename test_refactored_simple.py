#!/usr/bin/env python3
"""
Simple test for refactored Auto-QA structure
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("=" * 70)
print("Auto-QA Refactored Structure Test")
print("=" * 70)

# Test 1: Import refactored modules
print("\n📦 Testing Module Imports...")
modules_tested = 0
modules_passed = 0

executor_modules = [
    ("apps.executor.src.models", "Request/Response Models"),
    ("apps.executor.src.browser_manager", "Browser Manager"),
    ("apps.executor.src.action_handlers", "Action Handlers"),
    ("apps.executor.src.main_refactored", "Refactored Main"),
]

task_manager_modules = [
    ("libs.task_manager.src.task_metadata", "Task Metadata"),
    ("libs.task_manager.src.resource_tracker", "Resource Tracker"),
    ("libs.task_manager.src.task_manager_refactored", "Refactored Task Manager"),
]

git_modules = [
    ("libs.git_automation.src.git_manager", "Git Manager"),
]

# Test executor modules
print("  ├─ Executor Modules:")
for module_path, description in executor_modules:
    try:
        __import__(module_path)
        print(f"  │   ✅ {description}")
        modules_passed += 1
    except Exception as e:
        print(f"  │   ❌ {description}: {e}")
    modules_tested += 1

# Test task manager modules
print("  ├─ Task Manager Modules:")
for module_path, description in task_manager_modules:
    try:
        __import__(module_path)
        print(f"  │   ✅ {description}")
        modules_passed += 1
    except Exception as e:
        print(f"  │   ❌ {description}: {e}")
    modules_tested += 1

# Test git automation
print("  └─ Git Automation:")
for module_path, description in git_modules:
    try:
        __import__(module_path)
        print(f"  │   ✅ {description}")
        modules_passed += 1
    except Exception as e:
        print(f"  │   ❌ {description}: {e}")
    modules_tested += 1

# Test 2: Verify file sizes
print("\n📊 File Size Comparison...")
files_checked = []

# Compare file sizes
file_comparisons = [
    ("apps/executor/src/main.py", "apps/executor/src/main_refactored.py", "Executor Main"),
    ("libs/task_manager/src/task_manager.py", "libs/task_manager/src/task_manager_refactored.py", "Task Manager"),
]

for original_file, refactored_file, description in file_comparisons:
    if os.path.exists(original_file) and os.path.exists(refactored_file):
        orig_size = os.path.getsize(original_file)
        orig_lines = 0
        with open(original_file) as f:
            orig_lines = sum(1 for _ in f)

        ref_size = os.path.getsize(refactored_file)
        ref_lines = 0
        with open(refactored_file) as f:
            ref_lines = sum(1 for _ in f)

        reduction = orig_lines - ref_lines
        pct = (reduction / orig_lines * 100) if orig_lines > 0 else 0

        print(f"  ├─ {description}:")
        print(f"  │   Original: {orig_lines:,} lines ({orig_size/1024:.1f} KB)")
        print(f"  │   Refactored: {ref_lines:,} lines ({ref_size/1024:.1f} KB)")
        print(f"  │   Reduction: {reduction:,} lines ({pct:.1f}%)")
        files_checked.append(True)

# Test 3: Check configuration files
print("\n⚙️  Configuration Files:")
config_files = [
    "compose.yml",
    "compose.test.yml",
    ".env.example",
    ".env.test",
]

for config_file in config_files:
    if os.path.exists(config_file):
        size = os.path.getsize(config_file)
        print(f"  ✅ {config_file}: {size:,} bytes")
    else:
        print(f"  ⚠️  {config_file}: Not found")

# Summary
print("\n" + "=" * 70)
print(f"✅ Test Summary:")
print(f"   Modules tested: {modules_tested}")
print(f"   Modules passed: {modules_passed}")
print(f"   Success rate: {modules_passed/modules_tested*100:.1f}%")
print(f"   Files compared: {len(files_checked)}")
print("=" * 70)

print("\n📁 Refactored Structure:")
print("""
  apps/executor/src/
    ├── models.py              (Request/Response models)
    ├── browser_manager.py      (Browser state management)
    ├── action_handlers.py       (Action execution logic)
    ├── main_refactored.py      (Simplified main)
    └── main.py               (Original - for reference)

  libs/task_manager/src/
    ├── task_metadata.py        (Task lifecycle & status)
    ├── resource_tracker.py      (Resource usage tracking)
    ├── task_manager_refactored.py (Simplified manager)
    └── task_manager.py         (Original - for reference)

  Configuration:
    ├── compose.yml              (Default ports)
    ├── compose.test.yml          (Alternative ports)
    ├── .env.example             (Default config)
    └── .env.test               (Test config)
""")

print("📝 To test with 여행가는달.com:")
print("""
  1. Start services:
     docker-compose -f compose.test.yml --profile ollama up -d

  2. Open web UI:
     open http://localhost:3001

  3. Run test:
     python cli.py run 여행가는달.com \\
       --description "Travel website with booking features"
""")

print("=" * 70)
