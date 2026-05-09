# CAN Log Summarizer

A local-first tool that turns CAN bus logs into plain-English summaries using a self-hosted LLM. Built for HIL (Hardware-in-the-Loop) and V&V engineers who want fast triage of test logs without sending data to the cloud.

## What it does

1. You upload a CAN log (`.asc`, more formats coming) to a Telegram bot
2. The bot routes it to a local FastAPI service
3. The service parses the log against a DBC, decodes signals, and computes statistics
4. A locally-running LLM (Ollama + Llama 3.1 / Mistral) interprets the statistics and replies with a structured summary
5. The reply lands back in your Telegram chat

Everything runs on your own server. Nothing leaves your network unless you choose otherwise.

## Why

If you do HIL or V&V work, you generate dozens of CAN logs per day. Triaging them manually is time-consuming. Cloud-based tools require sending vehicle data through someone else infrastructure, fine for some teams, a non-starter for OEMs and Tier 1 suppliers handling pre-release projects.

This is a working prototype of the local-first alternative.

## Status

This is an early-stage personal project. The pipeline works end-to-end, you can upload a `.asc` file via Telegram and receive a generated summary. Several known issues are tracked and being fixed; see Known issues below.

## Architecture

[Telegram] -> [n8n Master Router] -> [n8n CAN Summarizer workflow] -> [FastAPI service] -> [parser + cantools + signal filter] -> [Ollama (local LLM)] -> [structured reply back to Telegram]

Server stack: Debian 13, Docker (n8n, Open WebUI), Ollama (system service, GPU-accelerated on RTX 3080), Python 3 + FastAPI + cantools + python-can.

## Components

- `src/api.py` - FastAPI service with `/upload-and-summarize` endpoint
- `src/parser.py` - minimal `.asc` parser (being replaced; see Known issues)
- `src/summarize_log.py` - main pipeline: parse, decode, summarise, prompt LLM
- `src/llm_backend.py` - thin wrapper over Ollama HTTP API
- `src/signal_filter.py` - strips diagnostic signals (CRCs, counters) from the LLM-facing summary so the model focuses on real data
- `src/generate_log.py`, `src/generate_speed_log.py` - synthetic test log generators
- `data/dbcs/toyota.dbc` - bundled DBC from comma.ai opendbc project (https://github.com/commaai/opendbc), MIT licensed

## Setup

The project is currently designed for the author specific server setup. A clean reproducible setup guide will follow once the architectural refactor is complete.

For now, the broad strokes:

    git clone <repo-url>
    cd can-log-summarizer
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn src.api:app --host 0.0.0.0 --port 8000

Make sure Ollama is running locally with at least one model pulled (e.g. `ollama pull llama3.1:8b`).

The Telegram integration uses n8n (https://n8n.io) workflows that call the FastAPI service. Setup notes for the n8n side will be added once they are stable.

## Known issues

A diagnostic pass identified 11 issues in the current code. They are being fixed as part of an ongoing architectural refactor. Highest priority:

- The current `.asc` parser drops `Tx` frames, error frames, and some extended-ID variants because of a strict regex. Will be replaced with python-can ASCReader.
- `except Exception` blocks swallow decoding errors silently. Need typed exception handling and logging.
- Multi-channel logs are aggregated into a single signal bucket, channel information is lost.
- No automated tests yet. Adding pytest coverage as the first refactor step.

The full diagnostic list is being tracked separately and will move into GitHub Issues once this repo is published.

## Roadmap

Near-term:

- Bug fixes (above)
- Architectural refactor: split parsers from summarizer, common `Frame` model
- BLF format support (in addition to `.asc`)
- Pytest test suite

Medium-term:

- Anomaly detection over decoded signals
- Multi-format support (`.trc`, `.log`, `.mf4`)
- Web UI in addition to Telegram

Longer-term:

- Failure summariser (consume test logs, draft bug reports)
- DBC validator
- Other HIL-engineer workflow tools

## License

MIT - see LICENSE.

## Acknowledgements

- comma.ai opendbc (https://github.com/commaai/opendbc) for the bundled `toyota.dbc`
- cantools (https://github.com/cantools/cantools) and python-can (https://github.com/hardbyte/python-can) for the heavy lifting on CAN format parsing
- Ollama (https://ollama.com) for making local LLM hosting accessible
- n8n (https://n8n.io) for workflow automation
