# Auto Commit Tool

This command-line tool, written in Python, automates the Git commit process. It also offers the option to generate commit messages automatically using the OpenAI API via the *requests* library. Below you will find detailed instructions on how to use the code, explanations for each flag, how to create aliases for easier access, and an important note for Mac users.

## Features
- **Stage Changes:** Automatically stages changes with `git add .` or interactively with the `--add` flag.
- **Retrieve Diff:** Captures the current Git diff between the previous and latest commits.
- **Generate Commit Message:** Uses the OpenAI API to generate a concise and descriptive commit message based on the diff.
- **Commit and Push:** Commits your changes with the generated or manually entered commit message and optionally pushes the commit to your remote repository using the `--push` flag.

## Requirements

- Python 3.6 or higher.
- Git installed on your system.
- The *requests* package for making HTTP requests.
- An OpenAI account and API key (if you wish to use automatic message generation).

## Installation
1. Clone the repository:

```
git clone https://github.com/your_username/auto-commit-tool.git
cd auto-commit-tool
```

2. (Optional) Create a virtual environment and install the dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Important for Mac Users:**  
   Ensure that each file starts with the following shebang line for proper execution:

``` 
#!/Users/david/Desktop/ds/venv/bin/python3
```

   Modify this line if your virtual environment is located elsewhere.

4. Make the `run.py` file executable:

```
chmod +x run.py
```

## Using the Code

The `run.py` script serves as the entry point for the tool. Below are the explanations for the different flags:

- **`--openai`**  
  Activates the generation of the commit message using the OpenAI API. When used, the script will take the current Git diff and send it to OpenAI to obtain a concise message.  
  Example:
  
```
python run.py --openai --api-key YOUR_OPENAI_API_KEY
```

- **`--api-key`**  
  Allows you to pass your OpenAI API key directly. If not provided, the script will look for the `OPENAI_API_KEY` environment variable.

- **`--push` (or `--p`)**  
  Indicates that after committing, the tool should push the commit to the remote repository. If this flag is not used, the push step will be skipped.

- **`--add` (or `-a`)**  
  Enables interactive file staging. When this flag is used, you can select which files to stage rather than staging all changes. If positional file names are provided, those files will be staged; otherwise, the tool will prompt you to enter the files manually.
```
   chmod +x run.py
```
## Usage
### Creating Aliases

#### For macOS
You can create an alias in your shell configuration file (`~/.zshrc` or `~/.bash_profile`) to easily run the tool:

``` 
alias autocommit='OPENAI_API_KEY=YOUR_OPENAI_API_KEY $(pwd)/run.py --openai'
```

If you want to use the interactive file selection option, use:

``` 
alias autocommit='OPENAI_API_KEY=YOUR_OPENAI_API_KEY $(pwd)/run.py --openai --add'
```

Then, reload your configuration:

``` 
source ~/.zshrc
```
#### For Windows

Edit your PowerShell profile (or your command lime configuration) and create a similar alias or function that points to the full path of run.py.
Example:
```
   powershell
      function Set-Alias autocommit {
      $env:OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY';
      python "C:\\path\\to\\auto-commit-tool\\run.py" --openai
}
```
## Contributing

Contributions are welcome!

## License

This project is licensed under the MIT License.

---

# Updated Features — 2026-06-30

This section documents enhancements added after the original Auto Commit Tool README above.

## New: Multi-LLM Provider Support

The tool now supports generating commit messages through multiple LLM providers, not only OpenAI.

### Supported Providers
1. **OpenAI** — `gpt-4o`, `gpt-4o-mini`, `gpt-4.1`, `o3-mini`
2. **Anthropic (Claude)** — `claude-sonnet-4-20250514`, `claude-3-5-haiku-20241022`, `claude-3-opus-20240229`
3. **Google (Gemini)** — `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.0-flash`, `gemma-3-27b-it`
4. **Ollama (local)** — `llama3.3`, `deepseek-coder-v2`, `mistral`, `qwen2.5:72b`, `phi4`
5. **Groq** — `llama-3.3-70b-versatile`, `mixtral-8x7b-32768`, `gemma2-9b-it`

### New CLI Flags
- **`--setup`**
  Run the first-time interactive configuration wizard to select your provider and model.

- **`--reset`**
  Clear saved settings and re-run setup.

- **`--llm`**
  Use the configured LLM provider to generate commit messages from diffs.

- **`--provider`**
  Select a provider: `openai`, `anthropic`, `google`, `ollama`, or `groq`.

- **--model`**
  Override the model for the selected provider.

- **`--base-url`**
  Override the default API base URL for the selected provider.

- **`--api-key`**
  Override the API key for the selected provider.

- **`--config-path`**
  Show or override the persisted configuration file path. Default: `~/.autocommit.json`.

### First-Time Setup
```bash
python run.py --setup
```

You are prompted to select a provider and model, and to enter or confirm the API key for your provider. If using Ollama, enter the host URL instead of an API key. Configuration is saved to `~/.autocommit.json`.

### Example Usage
```bash
python run.py --llm
python run.py --llm --provider openai --model gpt-4o-mini
python run.py --llm --provider ollama --base-url http://localhost:11434/api/chat --model llama3.3
python run.py --llm --provider anthropic --model claude-3-5-haiku-20241022
```

### Backward Compatibility
The original `--openai` behavior has been preserved in spirit through the new `--llm` flow. Provider/model defaults are stored locally, so repeat invocations can stay simple:

```bash
python run.py --llm
python run.py --llm --push
```
