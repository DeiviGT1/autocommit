# Auto Commit Tool
A command-line tool written in Python to
automate the Git commit process, with an option to generate commit messages\using the OpenAI API via requests.

## Features

- Stage Changes: Automatically stages changes using `git add .`.
- Retrieve Diff: Captures the current Git diff between previous and latest commits.
- Generate Commit Message: Uses the OpenAI API (via requests) to generate a concise and descriptive commit message based on the diff.
- Commit Changes: Commits your changes with the generated or provided commit message.
- Push Commits: Optionally pushes the commit to your remote repository.

## Requirements

- Python 3.6 or higher.
- Git installed on your system.
- Requests package for making HTTP requests.

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/your_username/auto-commit-tool.git
   ```
   cd auto-commit-tool

3. (Optional) Create a virtual environment and install dependencies:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Make the script executable:
   ```
   chmod +x auto_commit.py
   ```
## Usage

### Basic Execution

Run the script witout the OpenAI option:
   ```
   ./auto_commit.py
   ```
### Using the OpenAI API

Ensure your OpenAI API key is et (via the --api-key flag or the OPENAI_API_KEY environment variable).

Example:
   ```
   ./auto_commit.py --openai --push --api-key YOUR_OPENAI_API_KEY
   ```
### Creating an Alias

To simplify execution, create an alias in your shell configuration.

For example, edit your ~/.bash_profile or ~/.zshrc and add this line:
   ```
   alias autocommit='OPENAI_API_KEY=YOUR_OPENAI_API_KEY {complete_folder_path}/auto_commit.py --openai --push'
   ```
Reload your shell configuration:
   ```
   source ~/.bash_profile
   ```
Now, run:
   ```
   autocommit
   ```
## Contributing

Contributions are welcome!

