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
    prompt_first_run,
    provider_requires_api_key,
    save_config,
)


def prompt_for_files(cli_files):
    if cli_files:
        return cli_files

    files = input("Enter the file(s) to add (separated by space): ").strip()
    if not files:
        print("No files entered. Exiting.")
        sys.exit(1)

    return files.split()


def main():
    parser = argparse.ArgumentParser(
        description="Tool for automating Git commits with multi-provider LLM support."
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic", "google", "ollama", "groq"],
        help="LLM provider to use for generating commit messages.",
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
        help="LLM API key. Falls back to provider environment variables or saved config.",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Use the configured LLM provider to generate commit messages from diffs.",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run the first-time interactive configuration wizard.",
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
        help="Path to the persisted configuration file. Defaults to ~/.autocommit.json",
    )
    parser.add_argument(
        "--push",
        "--p",
        action="store_true",
        default=False,
        help="Push the commit after committing.",
    )
    parser.add_argument(
        "--add",
        "-a",
        action="store_true",
        help="Interactively choose files to add instead of staging all changes.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Optional file names to stage when using --add flag.",
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

    if args.add:
        files_to_add = args.files if args.files else prompt_for_files([])
        add_cmd = ["git", "add"] + files_to_add
    else:
        print("Staging all changes with 'git add .'...")
        add_cmd = ["git", "add", "."]

    add_result = subprocess.run(add_cmd, capture_output=True, text=True)
    if add_result.returncode != 0:
        print("Error executing git add command.")
        print(add_result.stderr)
        sys.exit(1)

    print("Retrieving Git diff...")
    diff_process = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True)
    diff_output = diff_process.stdout.strip()

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
            print(f"Error generating commit message with the configured LLM: {error}")
            sys.exit(1)

    if commit_message is None:
        commit_message = input("Enter the commit message: ")

    print("Committing changes...")
    commit_result = subprocess.run(["git", "commit", "-m", commit_message])
    if commit_result.returncode != 0:
        print("Error during commit.")
        sys.exit(1)

    if args.push:
        print("Pushing changes to the remote repository...")
        push_result = subprocess.run(["git", "push"])
        if push_result.returncode != 0:
            print("Error during push.")
            sys.exit(1)
    else:
        print("Push option not specified. Skipping push.")


if __name__ == "__main__":
    main()
