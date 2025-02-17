#!/Users/david/Desktop/ds/venv/bin/python3
import os
import subprocess
import argparse
import sys
import requests

def main():
    parser = argparse.ArgumentParser(
        description="Tool for automating Git commits, with the option to generate commit messages using the OpenAI API via requests."
    )
    parser.add_argument(
        "--openai",
        action="store_true",
        help="Use the OpenAI API to generate the commit message from the diff."
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push the commit after committing."
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key. If not provided, the script will look in the OPENAI_API_KEY environment variable."
    )
    args = parser.parse_args()

    # Check that the current directory is a Git repository
    if not os.path.isdir(".git"):
        print("Error: .git directory not found. Make sure you are in a Git repository.")
        sys.exit(1)

    # 1. Stage changes
    print("Staging changes with 'git add .'...")
    add_result = subprocess.run("git add .", shell=True, capture_output=True, text=True)
    if add_result.returncode != 0:
        print("Error executing 'git add .'.")
        sys.exit(1)

    # 2. Retrieve the Git diff
    print("Retrieving Git diff...")
    diff_process = subprocess.run(["git", "diff", "HEAD^", "HEAD"], capture_output=True, text=True)
    diff_output = diff_process.stdout.strip()
    

    # 3. Generate commit message using OpenAI (via requests)
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
            print("Generated commit message:", commit_message)
        except Exception as e:
            print("Error generating commit message with OpenAI via requests:", e)
            sys.exit(1)
    else:
        commit_message = input("Enter the commit message: ")

    # 4. Commit the changes
    print("Committing changes...")
    commit_result = subprocess.run(["git", "commit", "-am", commit_message])
    if commit_result.returncode != 0:
        print("Error during commit.")
        sys.exit(1)

    # 5. Push changes if the --push flag was specified
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