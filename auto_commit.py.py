#!/usr/bin/env python3
import os
import subprocess
import argparse
import sys

# Import openai only if needed
try:
    import openai
except ImportError:
    openai = None

def main():
    parser = argparse.ArgumentParser(
        description="Tool for automating Git commits, with the option to generate commit messages using the OpenAI API."
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
    print("Staging changes with 'git add *'...")
    add_result = subprocess.run("git add *", shell=True)
    if add_result.returncode != 0:
        print("Error executing 'git add *'.")
        sys.exit(1)

    # 2. Retrieve the Git diff
    print("Retrieving Git diff...")
    diff_process = subprocess.run(["git", "diff"], capture_output=True, text=True)
    diff_output = diff_process.stdout.strip()

    # 3. Generate commit message
    if args.openai:
        if openai is None:
            print("Error: 'openai' package not found. Please install it with 'pip install openai'.")
            sys.exit(1)
        api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: OpenAI API key not provided. Use --api-key or set the OPENAI_API_KEY environment variable.")
            sys.exit(1)
        openai.api_key = api_key

        prompt = (
            "Generate a concise and descriptive commit message for the following diff:\n\n"
            + diff_output
        )
        print("Generating commit message using OpenAI...")
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=50,
                temperature=0.5,
                n=1,
                stop=None,
            )
            commit_message = response.choices[0].text.strip()
            print("Generated commit message:", commit_message)
        except Exception as e:
            print("Error generating commit message with OpenAI:", e)
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