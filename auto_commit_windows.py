import os
import sys
import argparse
import subprocess

from autocommit_llm import (
    CONFIG_PATH,
    build_client,
    first_run_setup,
    generate_commit_message,
    load_config,
    provider_requires_api_key,
    save_config,
)


def main():
    parser = argparse.ArgumentParser(
        description="Windows automation tool for Git commits with multi-provider LLM support.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto_commit_windows.py --llm
  python auto_commit_windows.py --llm --provider openai --model gpt-4o
  python auto_commit_windows.py --llm --provider ollama
  python auto_commit_windows.py --setup
  python auto_commit_windows.py --llm --base-url http://localhost:11434/api/chat --model llama3.3
""",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic", "google", "ollama", "groq"],
        help="LLM provider for generating commit messages.",
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model name override from the selected provider.",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        help="Override the default API base URL for the chosen provider.",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for the chosen provider. Falls back to saved config or provider env vars.",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Automatically generate the commit message with the configured LLM.",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run the first-time interactive setup wizard.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset saved configuration and re-run setup.",
    )
    parser.add_argument(
        "--config-path",
        type=str,
        default=str(CONFIG_PATH),
        help="Path to the configuration file. Defaults to ~/.autocommit.json",
    )
    parser.add_argument(
        "--push",
        type=bool,
        default=False,
        nargs="?",
        const=True,
        help="Push after committing (true/false).",
    )
    parser.add_argument(
        "--add",
        type=bool,
        default=False,
        nargs="?",
        const=True,
        help="Interactively choose files to stage instead of staging everything.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Stage all changes before committing.",
    )
    parser.add_argument(
        "--message",
        type=str,
        default=None,
        help="Provide the commit message directly for non-interactive scripts.",
    )

    args = parser.parse_args()

    if not os.path.isdir(".git"):
        print("Error: .git directory not found. Make sure you are in a Git repository.")
        sys.exit(1)

    if args.reset:
        save_config({})
        print("Configuration cleared.")

    if args.setup or not load_config():
        first_run_setup(force=bool(args.setup))

    if args.all or not args.add:
        print("Staging changes with 'git add .'...")
        add_result = subprocess.run(
            ["git", "add", "."],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if add_result.returncode != 0:
            print("Error staging changes.")
            print(add_result.stderr)
            sys.exit(1)
    else:
        # NOTE: full Windows interactive file picker not implemented yet.
        print("Interactivity is limited in this release. Use --all or provide file paths manually.")
        sys.exit(1)

    print("Retrieving staged diff...")
    try:
        diff_result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if diff_result.returncode != 0:
            print("Error retrieving staged diff.")
            print(diff_result.stderr)
            sys.exit(1)

        diff_output = diff_result.stdout.strip()

        if not diff_output:
            print("Nothing staged to commit.")
            sys.exit(0)
    except Exception as error:
        print(f"Error retrieving staged diff: {error}")
        sys.exit(1)

    commit_message = None
    if args.llm:
        config = load_config()
        provider = args.provider or config.get("provider")
        model = args.model or config.get("model", "")
        api_key = args.api_key or config.get("api_key", "")
        base_url = args.base_url or config.get("base_url", "")

        if not provider:
            raise SystemExit(
                "No LLM provider configured. Re-run with --setup or pass --provider."
            )

        if not model:
            raise SystemExit(
                "No model configured for provider. Re-run with --setup or pass --model."
            )

        client_fn, resolved_base_url, resolved_api_key = build_client(
            provider, base_url, api_key
        )

        if provider_requires_api_key(provider) and not resolved_api_key:
            env_var = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_API_KEY",
                "groq": "GROQ_API_KEY",
            }.get(provider)

            if env_var:
                resolved_api_key = os.environ.get(env_var, "")

            if not resolved_api_key:
                raise SystemExit(
                    f"API key missing for provider '{provider}'. Pass --api-key or set {env_var}."
                )

        print(f"Generating commit message via {provider}/{model}...")
        try:
            commit_message = generate_commit_message(
                diff_output, client_fn, resolved_base_url, resolved_api_key, model
            )
        except Exception as error:
            print(f"Error generating commit message with configured LLM: {error}")
            sys.exit(1)

    if commit_message is None:
        if args.message:
            commit_message = args.message
        else:
            commit_message = input("Enter the commit message: ").strip()

    print("Committing changes...")
    commit_cmd = ["git", "commit", "-m", commit_message]
    commit_result = subprocess.run(
        commit_cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if commit_result.returncode != 0:
        print("Commit failed.")
        print(commit_result.stderr)
        sys.exit(1)

    if args.push:
        print("Pushing to remote...")
        push_result = subprocess.run(["git", "push"])
        if push_result.returncode != 0:
            print("Push failed.")
            sys.exit(1)
    else:
        print("Push option not specified. Skipping push.")


if __name__ == "__main__":
    main()
