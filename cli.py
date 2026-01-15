#!/usr/bin/env python3
"""
Auto-QA CLI - Command line interface for automated QA testing

Usage:
    python cli.py run <url> --description "<domain description>"
    python cli.py status
    python cli.py report <session_id>
"""

import sys
import os
import argparse
import httpx
import json
from typing import Optional

BRAIN_API_URL = os.environ.get('BRAIN_API_URL', 'http://localhost:9000')


def start_test(url: str, description: str) -> bool:
    """Start a new QA test"""
    print(f"🚀 Starting QA test on: {url}")
    print(f"📝 Description: {description[:100]}...")
    print()

    try:
        with httpx.Client(timeout=300) as client:
            response = client.post(
                f"{BRAIN_API_URL}/start",
                json={"url": url, "domain_info": description}
            )
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "success":
                session_id = data.get("session_id")
                print(f"✅ Test started successfully!")
                print(f"📋 Session ID: {session_id}")
                print()
                print("Monitor the test:")
                print(f"  python cli.py status")
                print(f"  python cli.py report {session_id}")
                return True
            else:
                print(f"❌ Failed to start test: {data.get('message')}")
                return False

    except httpx.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_status() -> bool:
    """Get current test status"""
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(f"{BRAIN_API_URL}/status")
            response.raise_for_status()
            data = response.json()

            print("📊 QA System Status")
            print("-" * 40)
            print(f"Running: {'Yes' if data.get('running') else 'No'}")
            print(f"Session ID: {data.get('session_id', 'None')}")
            print(f"Model: {data.get('model', 'Unknown')}")
            print()
            return True

    except httpx.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def stop_test() -> bool:
    """Stop current test"""
    print("⏹️  Stopping QA test...")
    print()

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(f"{BRAIN_API_URL}/stop")
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "success":
                print("✅ Test stopped successfully")
                return True
            else:
                print(f"❌ Failed to stop test: {data.get('message')}")
                return False

    except httpx.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Auto-QA CLI - AI-powered web testing automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py run https://example.com --description "E-commerce site with shopping cart"
  python cli.py status
  python cli.py stop
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    run_parser = subparsers.add_parser("run", help="Start a new QA test")
    run_parser.add_argument("url", help="Website URL to test")
    run_parser.add_argument("-d", "--description", required=True,
                         help="Domain/project description in markdown")

    subparsers.add_parser("status", help="Check current test status")

    subparsers.add_parser("stop", help="Stop current test")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        success = start_test(args.url, args.description)
        sys.exit(0 if success else 1)

    elif args.command == "status":
        success = get_status()
        sys.exit(0 if success else 1)

    elif args.command == "stop":
        success = stop_test()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
