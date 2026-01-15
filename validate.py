#!/usr/bin/env python3
"""
Validate Auto-QA system setup and dependencies
"""

import os
import sys
import subprocess
import shutil

def check_command(cmd, name):
    """Check if a command is available"""
    if shutil.which(cmd):
        print(f"✅ {name}: Found ({cmd})")
        return True
    else:
        print(f"❌ {name}: Not found ({cmd})")
        return False

def check_file(path, name):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"✅ {name}: Found ({path})")
        return True
    else:
        print(f"❌ {name}: Not found ({path})")
        return False

def check_docker():
    """Check Docker installation and status"""
    print("\n🐳 Docker Check")
    print("-" * 40)

    docker_ok = True
    docker_ok &= check_command("docker", "Docker CLI")
    docker_ok &= check_command("docker-compose", "Docker Compose")

    if docker_ok:
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✅ Docker daemon: Running")
            else:
                print("❌ Docker daemon: Not running")
                docker_ok = False
        except:
            print("❌ Docker daemon: Not accessible")
            docker_ok = False

    return docker_ok

def check_project_structure():
    """Check project structure"""
    print("\n📁 Project Structure Check")
    print("-" * 40)

    structure_ok = True
    structure_ok &= check_file("compose.yml", "Docker Compose config")
    structure_ok &= check_file("apps/brain/src/main.py", "Brain service")
    structure_ok &= check_file("apps/executor/src/main.py", "Executor service")
    structure_ok &= check_file("apps/web/src/main.py", "Web service")
    structure_ok &= check_file("cli.py", "CLI tool")
    structure_ok &= check_file("README.md", "Documentation")

    return structure_ok

def check_config():
    """Check configuration files"""
    print("\n⚙️  Configuration Check")
    print("-" * 40)

    config_ok = True
    config_ok &= check_file(".env.example", "Environment template")

    if os.path.exists(".env"):
        print("✅ .env: Found (using custom configuration)")
    else:
        print("⚠️  .env: Not found (will use defaults)")
        print("   Run: cp .env.example .env")

    return config_ok

def check_ports():
    """Check if required ports are available"""
    print("\n🔌 Port Availability Check")
    print("-" * 40)

    import socket

    ports = {
        3000: "Web UI",
        9000: "Brain API",
        9001: "Executor API",
        11434: "Ollama (if using built-in)",
        15432: "Database"
    }

    port_available = True
    for port, name in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", port))
        sock.close()

        if result != 0:
            print(f"✅ {name} ({port}): Available")
        else:
            print(f"⚠️  {name} ({port}): Already in use")

    return port_available

def main():
    """Main validation function"""
    print("🤖 Auto-QA System Validation")
    print("=" * 40)

    all_ok = True
    all_ok &= check_docker()
    all_ok &= check_project_structure()
    all_ok &= check_config()
    all_ok &= check_ports()

    print("\n" + "=" * 40)
    if all_ok:
        print("✅ All checks passed!")
        print("\n🚀 Ready to start:")
        print("   docker-compose --profile ollama up -d")
        print("\n📚 Or check README.md for more options")
        return 0
    else:
        print("⚠️  Some checks failed")
        print("\nPlease resolve the issues above before starting")
        return 1

if __name__ == "__main__":
    sys.exit(main())
