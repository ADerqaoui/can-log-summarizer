# Test suite for can-log-summarizer

This directory contains the automated test suite. The structure mirrors
common Python testing practice with three tiers (unit, integration, system)
and a shared fixtures directory.

## Layout

    tests/
      unit/          fast, isolated tests, no external dependencies
      integration/   tests across multiple components, may use real Ollama
      system/        tests on real-world data, slow, run on schedule
      fixtures/      sample CAN logs and DBCs used as test inputs
        synthetic/   small generated logs with known content
        real/        comma2k19 segments converted to ASC
        dbcs/        DBC files used for testing decoding
      conftest.py    shared pytest fixtures (paths, helpers)

## Running the tests

The full suite:

    pytest

A specific tier:

    pytest -m unit
    pytest -m integration
    pytest -m system

Single test file:

    pytest tests/unit/test_parser.py

Single test:

    pytest tests/unit/test_parser.py::test_parse_asc_basic

With coverage:

    pytest --cov=src --cov-report=html

## Markers

Tests are categorized with pytest markers, declared in `pytest.ini`:

- `unit` - fast, no I/O beyond fixture files, no Ollama, no network
- `integration` - multi-component, may hit Ollama via mock or real call
- `system` - real comma2k19 data, slow, run unattended on schedule
- `slow` - any test taking >1s; can be excluded with `pytest -m "not slow"`

## Fixtures

Test fixtures (sample input files) live in `tests/fixtures/`. See
`tests/fixtures/README.md` for the index of what each fixture is for.

Fixtures are committed to git. Treat them as part of the contract: if a
fixture changes, every test using it needs review.

## Reports

Test runs produce reports in `../test_reports/`. See
`../test_reports/README.md` for the report format and retention policy.
