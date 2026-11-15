# Local Linux Hardware Q&A Assistant

## Overview
A local command-line assistant that answers natural-language questions about Linux hardware using system inspection tools and a locally hosted LLM through Ollama.

## Features
- CPU information using `lscpu`
- Memory information using `free`
- Storage information using `lsblk`
- GPU information using `lspci`
- Memory slot information using `dmidecode` when available
- Natural-language questions using Ollama (`llama3.2:3b`)
- Safe tool execution using an allow-list
- Command timeouts and error handling
- Structured JSON parsing
- Explicit handling of unavailable hardware information

## Technology Stack
- Python 3.11
- Ollama
- Llama 3.2:3b
- Typer
- Pydantic
- Pytest
- Linux system utilities

## Setup

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Ollama is running and the model is available:

   ```bash
   ollama pull llama3.2:3b
   ```

4. Configure the Ollama server address if it is hosted outside WSL:

   ```bash
   export OLLAMA_HOST="http://YOUR_HOST_IP:11434"
   ```

5. Start the assistant:

   ```bash
   python -m app.main
   ```

## Run Tests

```bash
python -m pytest -v
```

## Security
- Only predefined hardware inspection tools are permitted.
- Arbitrary shell commands are rejected.
- Commands execute with `shell=False` and a timeout.
- Hardware information is collected locally.
- Missing or inaccessible information is reported rather than guessed.

## Environment Limitations
This project was developed and tested in Ubuntu 20.04 under WSL2 on Windows 11. WSL exposes virtualized hardware information, so some physical hardware details, such as RAM slots, motherboard information, and physical GPU specifications, may not be accessible.

## Project Structure

```text
app/
  main.py
  tools/
  services/
  models/
tests/
requirements.txt
README.md
```
