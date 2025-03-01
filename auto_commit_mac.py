#!/Users/david/Desktop/ds/venv/bin/python3

import os
import subprocess
import argparse
import sys
import requests

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
        description="Tool for automating Git commits, with options for interactive file staging and generating commit messages via the OpenAI API."
    )
    parser.add_argument(
        "--openai",
        action="store_true",
        help="Use the OpenAI API to generate the commit message from the diff."
    )
    parser.add_argument(
        "--push",
        "--p",
        action="store_true",
        default=False,
        help="Push the commit after committing. (Default: False)"
    )
    parser.add_argument(
        "--add",
        "-a",
        action="store_true",
        help="Interactively choose files to add instead of staging all changes."
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key. If not provided, the script will look in the OPENAI_API_KEY environment variable."
    )
    # New positional argument for files.
    parser.add_argument(
        "files",
        nargs="*",
        help="Optional file names to stage when using --add flag."
    )
    
    args = parser.parse_args()

    if not os.path.isdir(".git"):
        print("Error: .git directory not found. Make sure you are in a Git repository.")
        sys.exit(1)

    # Stage changes: either interactively choose files or add all changes.
    if args.add:
        print(f"git add {args.files}")
        print("DEBUG")
        # If positional file names are provided, use them; otherwise, prompt the user.
        files_to_add = args.files if args.files else prompt_for_files([])
        add_cmd = ["git", "add"] + files_to_add
    else:
        print("Staging all changes with 'git add .'...")
        add_cmd = ["git", "add", "."]

    add_result = subprocess.run(add_cmd, capture_output=True, text=True)
    print(f"add_cmd: {add_cmd}")
    print(f"add_result: {add_result}")
    if add_result.returncode != 0:
        print("Error executing git add command.")
        print(add_result.stderr)
        sys.exit(1)

    print("Retrieving Git diff...")
    diff_process = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True)
    print(f"DIFF PROCEESS: {diff_process}")
    diff_output = diff_process.stdout.strip()

    if args.openai:
        api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: OpenAI API key not provided. Use --api-key or set the OPENAI_API_KEY environment variable.")
            sys.exit(1)
        user_message = (
            "Based on the following Git diff, generate a concise commit message that clearly summarizes the changes made. "
            "Highlight any new features, bug fixes, or improvements while keeping the message succinct:\n\n"
            + diff_output
        )
        print("Generating commit message using OpenAI (via requests)...")
        endpoint = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that generates concise and descriptive commit messages."},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 50,
            "temperature": 0.5
        }
        try:
            response = requests.post(endpoint, headers=headers, json=data)
            if response.status_code != 200:
                print("Error generating commit message with OpenAI. Status Code:", response.status_code)
                print("Response:", response.text)
                sys.exit(1)
            json_response = response.json()
            commit_message = json_response['choices'][0]['message']['content'].strip()
        except Exception as e:
            print("Error generating commit message with OpenAI via requests:", e)
            sys.exit(1)
    else:
        commit_message = input("Enter the commit message: ")

    print("Committing changes...")
    commit_result = subprocess.run(["git", "commit", "-m", commit_message])
    if commit_result.returncode != 0:
        print("Error during commit.")
        sys.exit(1)

    if args.push:
        print("Pushing changes to the remote repository...")
        remote_result = subprocess.run(["git", "remote"], capture_output=True, text=True)
        if remote_result.stdout.strip() == "":
            print("No remote repository configured. Skipping push.")
        else:
            push_result = subprocess.run(["git", "push"])
            if push_result.returncode != 0:
                print("Error during push.")
                sys.exit(1)
    else:
        print("Push option not specified. Skipping push.")

if __name__ == "__main__":
    main()