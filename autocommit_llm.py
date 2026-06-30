from __future__ import annotations

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

import requests

CONFIG_PATH = Path.home() / ".autocommit.json"


# ---------------------------------------------------------------------------
# Config persistence
# ---------------------------------------------------------------------------

def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_config(config: dict) -> None:
    CONFIG_PATH.write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def resolve_config_value(configured: Optional[str], fallback_env: str) -> Optional[str]:
    if configured:
        return configured
    return os.environ.get(fallback_env)


# ---------------------------------------------------------------------------
# First-run interactive setup
# ---------------------------------------------------------------------------

PROVIDERS = [
    {
        "key": "openai",
        "label": "OpenAI",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "o3-mini"],
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1/chat/completions",
        "payload": "openai",
    },
    {
        "key": "anthropic",
        "label": "Anthropic (Claude)",
        "models": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": "https://api.anthropic.com/v1/messages",
        "payload": "anthropic",
    },
    {
        "key": "google",
        "label": "Google (Gemini)",
        "models": [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemma-3-27b-it",
        ],
        "api_key_env": "GOOGLE_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/",
        "payload": "google",
    },
    {
        "key": "ollama",
        "label": "Ollama (local)",
        "models": ["llama3.3", "deepseek-coder-v2", "mistral", "qwen2.5:72b", "phi4"],
        "api_key_env": "OLLAMA_HOST",
        "base_url": "http://localhost:11434/api/chat",
        "payload": "ollama",
    },
    {
        "key": "groq",
        "label": "Groq",
        "models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1/chat/completions",
        "payload": "openai",
    },
]


def prompt_first_run() -> dict:
    print("Welcome to AutoCommit! Let's set up your LLM provider.\n")

    for idx, provider in enumerate(PROVIDERS, start=1):
        print(f"  [{idx}] {provider['label']}")
        for model in provider["models"]:
            print(f"       - {model}")
    print()

    while True:
        choice = input("Select a provider number (1-5): ").strip()
        if choice in {"1", "2", "3", "4", "5"}:
            provider = PROVIDERS[int(choice) - 1]
            break
        print("Please enter a number from 1 to 5.")

    print(f"\nAvailable models for {provider['label']}:")
    for idx, model in enumerate(provider["models"], start=1):
        print(f"  [{idx}] {model}")
    while True:
        model_choice = input("Select a model number or type a custom model name: ").strip()
        if model_choice.isdigit():
            idx = int(model_choice) - 1
            if 0 <= idx < len(provider["models"]):
                model = provider["models"][idx]
                break
        elif model_choice:
            model = model_choice
            break
        print("Please enter a valid model selection.")

    api_key = ""
    api_base = provider["base_url"]
    if provider["key"] == "ollama":
        override_host = True
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        api_base = host
        api_key = host
        if not (host.startswith("http://") or host.startswith("https://")):
            override_host = True
            new_host = input("Ollama host (default http://localhost:11434): ").strip() or host
            api_base = new_host.rstrip("/")
            api_key = api_base
    else:
        env_var = provider["api_key_env"]
        env_val = os.environ.get(env_var, "").strip()
        if env_val:
            use_env = input(f"Found env var {env_var}. Use it? [Y/n]: ").strip().lower()
            if use_env in ("", "y", "yes"):
                api_key = env_val
        if not api_key:
            api_key = input(f"Enter your {provider['label']} API key: ").strip()

    config = {
        "provider": provider["key"],
        "model": model,
        "api_key": api_key,
        "base_url": api_base,
        "payload": provider["payload"],
    }
    save_config(config)
    print(f"\nConfiguration saved to {CONFIG_PATH}")
    return config


def first_run_setup(force: bool = False) -> dict:
    existing = load_config() if not force else {}
    if existing and not force:
        return existing

    print("No configuration found. Starting first-time setup.\n")
    return prompt_first_run()


# ---------------------------------------------------------------------------
# LLM provider clients
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a helpful assistant that generates concise and descriptive Git commit messages. "
    "Return only the commit message text, no surrounding quotes or explanation."
)


def _openai_chat_completion(base_url: str, api_key: str, model: str, user_message: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": 50,
        "temperature": 0.5,
    }
    resp = requests.post(base_url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Provider error {resp.status_code}: {resp.text}")
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def _anthropic_chat_completion(base_url: str, api_key: str, model: str, user_message: str) -> str:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 200,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_message}],
    }
    resp = requests.post(base_url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Provider error {resp.status_code}: {resp.text}")
    data = resp.json()
    return data["content"][0]["text"].strip()


def _ollama_chat_completion(base_url: str, _, model: str, user_message: str) -> str:
    # base_url already includes host because Ollama endpoint is different
    headers = {"content-type": "application/json"}
    payload = {
        "model": model,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_message}],
        "stream": False,
        "options": {"num_predict": 100},
    }
    resp = requests.post(base_url, headers=headers, json=payload, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(f"Provider error {resp.status_code}: {resp.text}")
    data = resp.json()
    return data["message"]["content"].strip()


def _google_generate_content(base_url: str, api_key: str, model: str, user_message: str) -> str:
    # base_url for google is the root, we append model path & ?key=
    safe_model = model
    if not base_url.endswith("/"):
        base_url = base_url + "/"
    url = f"{base_url}models/{safe_model}:generateContent?key={api_key}"
    headers = {"content-type": "application/json"}
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {"maxOutputTokens": 100, "temperature": 0.5},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Provider error {resp.status_code}: {resp.text}")
    data = resp.json()
    return (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
        .strip()
    )


PROVIDER_CLIENTS = {
    "openai": _openai_chat_completion,
    "groq": _openai_chat_completion,
    "anthropic": _anthropic_chat_completion,
    "ollama": _ollama_chat_completion,
    "google": _google_generate_content,
}


# ---------------------------------------------------------------------------
# Public API for CLI scripts
# ---------------------------------------------------------------------------

def provider_requires_api_key(provider: str) -> bool:
    return provider not in {"ollama"}


def build_client(provider: str, base_url: str, api_key: str):
    if provider not in PROVIDER_CLIENTS:
        raise ValueError(f"Unsupported provider: {provider}")
    return PROVIDER_CLIENTS[provider], base_url, api_key if provider_requires_api_key(provider) else ""


def generate_commit_message(diff_output: str, client_fn, base_url: str, api_key: str, model: str) -> str:
    user_message = (
        "Based on the following Git diff, generate a concise commit message that clearly summarizes the changes made. "
        "Highlight any new features, bug fixes, or improvements while keeping the message succinct:\n\n"
        + diff_output
    )
    return client_fn(base_url, api_key, model, user_message)
