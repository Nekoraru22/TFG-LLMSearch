#!/usr/bin/env python3
import argparse
import requests
import sys
import os

API_BASE = "http://localhost:5000/api"
models: list[str] = os.environ.get("LM_STUDIO_MODELS", "").split(" ")


def do_status():
    """Send GET /api/status and display the resulting JSON."""
    try:
        response = requests.get(f"{API_BASE}/status")
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"[ERROR] Could not connect to server: {error}", file=sys.stderr)
        sys.exit(1)

    data = response.json()
    print("=== System Status ===")
    print(f"Processed files       : {data.get('total_processed_files')}")
    print(f"Total files in system : {data.get('total_files')}")
    print(f"Files currently active: {data.get('total_in_process_files')}")
    print("By file type          :")
    for ext, count in data.get("total_files_by_type", {}).items():
        print(f"  {ext}: {count}")
    print(f"Errors encountered    : {data.get('encountered_errors')}")


def do_query(query: str, model: str, temperature: float, verbose: bool):
    """Send POST /api/query and display the result."""
    payload = {
        "query": query,
        "model": model,
        "temperature": temperature,
        "verbose": verbose
    }
    try:
        response = requests.post(f"{API_BASE}/query", json=payload)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"[ERROR] Request failed: {error}", file=sys.stderr)
        sys.exit(1)

    result = response.json()
    if "result" in result:
        print("=== Query Result ===")
        print(result["result"])
    else:
        print(f"[WARNING] Unexpected response: {result}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="LLMSearch Enhanced CLI")
    # Core options
    parser.add_argument(
        "-q", "--query",
        help="Search query (omit to show --status output)"
    )
    parser.add_argument(
        "-m", "--model",
        default="jonahhenry/mistral-7b-instruct-v0.2.Q4_K_M-GGUF",
        help="Model to use (e.g. gpt-4o-mini)"
    )
    parser.add_argument(
        "-t", "--temperature",
        type=float,
        default=0.7,
        help="LLM temperature (0.0–1.0)"
    )
    parser.add_argument(
        "-l", "--list-models",
        action="store_true",
        help="List available models"
    )

    # Flags
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose mode: include detailed descriptions"
    )
    parser.add_argument(
        "-s", "--status",
        action="store_true",
        help="Display system status and exit"
    )

    args = parser.parse_args()

    # If status flag is set, ignore --query and show status
    if args.status:
        do_status()
        return
    
    # If list-models flag is set, show available models
    if args.list_models:
        print("Available models:")
        for model in models:
            print(f"  - {model}")
        return

    # If no query provided, show usage and hint
    if not args.query:
        parser.print_usage(sys.stderr)
        print(
            "\nOr use --status to view the system status.",
            file=sys.stderr
        )
        sys.exit(1)

    # Execute the query
    do_query(args.query, args.model, args.temperature, args.verbose)


if __name__ == "__main__":
    main()
