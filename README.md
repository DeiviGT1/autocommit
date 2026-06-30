# Auto Commit Tool

This command-line tool, written in Python, automates the Git commit process. It also offers the option to generate commit messages automatically using multiple LLM providers, including OpenAI, Anthropic Claude, Google Gemini, Groq, and Ollama.

## Features
- **Stage Changes:** Automatically stages changes with `git add .` or interactively with the `--add` flag.
- **Retrieve Diff:** Captures the current Git diff between the previous and latest commits.
- **Generate Commit Message:** Uses a configured LLM to generate a concise and descriptive commit message based on the diff.
- **Commit and Push:** Commits your changes with the generated or manually entered commit message and optionally pushes the commit to your remote repository using the `--push` flag.

## Requirements
- Python 3.8 or higher.
- Git installed on your system.
- The `requests` package for HTTP.
- A supported LLM provider account and API key unless using Ollama.

## Supported Providers
1. OpenAI
2. Anthropic Claude
3. Google Gemini
4. Groq
5. Ollama (local)

## Installation
1. Clone the repository:
```bash
git clone https://github.com/your_username/auto-commit-tool.git
cd auto-commit-tool
```

2. Create a virtual environment and install the dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Make `run.py` executable:
```bash
chmod +x run.py
```

## First-time Setup
```bash
python run.py --setup
```

You are prompted to select a provider and model, and to enter/store the API key for your provider. If using Ollama, enter the host URL instead of an API key. Configuration is saved to `~/.autocommit.json`.

## Using the Code
Run the tool and generate a commit message with your configured provider:
```bash
python run.py --llm
```

Override provider/model/cmd-line options at any time:
```bash
python run.py --llm --provider openai --model gpt-4o-mini
python run.py --llm --provider ollama --base-url http://localhost:11434/api/chat --model llama3.3
python run.py --llm --provider anthropic --model claude-3-5-haiku-20241022
```

Re-run setup after clearing saved settings:
```bash
python run.py --reset
```

## Flags
- **`--setup`**  
  Run the first-time interactive configuration wizard.

- **`--reset`**  
  Clear saved settings.

- **`--llm`**  
  Use the configured LLM provider to generate the commit message from the diff.

- **`--provider`**  
  Choose `openai`, `anthropic`, `google`, `groq`, or `ollama`.

- **`--model`**  
  Override the model for the selected provider.

- **`--base-url`**  
  Override the API base URL for the selected provider.

- **`--api-key`**  
  Override the API key for the selected provider.

- **`--push`**  
  Push the commit after committing.

- **`--add`**  
  Interactively choose files to add instead of staging all changes.

## Creating Aliases

### For macOS
Create an alias in your shell rc file:
```bash
alias autocommit='python /path/to/auto-commit-tool/run.py --llm'
```

### For Windows
Create a function or alias that points to the full path of `run.py`.

## Contributing
Contributions are welcome!

## License
This project is licensed under the MIT License.
