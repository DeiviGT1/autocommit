# Auto Commit Tool

A command-line tool written in Python to
automate the Git commit process, with an option to generate commit messages using the OpenAI API via requests.

## Features

- Stage Changes: Automatically stages changes using `git add .`.
- Retrieve Diff: Captures the current Git diff between previous and latest commits.
- Generate Commit Message: Uses the OpenAI API via requests to generate a concise and descriptive commit message based on the diff.
- Commit Changes: Commits your changes with the generated or provided commit message.
- Push Commits: Optionally pushes the commit to your remote repository (if specified).

## Requirements

- Python 3.6 or higher.
- Git installed on your system.
- Requests package for making HTTP requests.

## Installation

1. Clone the repository:

   git clone https://github.com/your_username/auto-commit-tool.git
   cd auto-commit-tool

2. (Optional) Create a virtual environment and install dependencies:

   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

3. Adjust the shebang lines:

   in the code folder, update the shebang lines to point to your venv's python interpreter.
   You can use `pwd` to get the current directory path and update your alias accordingly.

4. Make the run.py executable:

   chmod +x run.py

## Usage

### Basic Execution

Run the tool via the run.py entrypoint:

   python run.py

### Using the OpenAI API

Ensure your OpenAI API key is et via the --api-key flag or the OPENAI_API_KEY environment variable.

Example:

   python run.py --openai --api-key YOUR_OPENAI_API_KEY

### Creating Aliases

#### For macOS

Edit your ~/.zshrc (or\~/.bash_profile) and add this line:

   alias autocommit='OPENAI_API_KEY=YOUR_OPENAI_API_KEY $(pwd)/run.py --openai'

Reload your configuration:

   source ~/.zshrc

#### For Windows

Edit your PowerShell profile (or your command lime configuration) and create a similar alias or function that points to the full path of run.py.
Example:

   fuction Set-Alias autocommit {
        $env:OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY';
    python "C:\path\to\auto-commit-tool\run.py" --openai
  }

## Contributing

Contributions are welcome!

## License

This project is licensed under the MIT License.
