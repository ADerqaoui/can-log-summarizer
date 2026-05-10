# Test reports

Output directory for pytest runs. Reports are timestamped and archived
here for historical comparison.

## Layout

    test_reports/
      latest/                 symlink to the most recent run's directory
      history/
        2026-05-10_032500/    run timestamp (UTC, sortable)
          pytest-report.html  full HTML report from pytest-html
          coverage/           coverage HTML report directory
          junit.xml           JUnit XML format (CI-compatible)
          stdout.log          captured pytest stdout
          summary.txt         short text summary, one line per test
      trends/                 future: rolled-up stats over time

## What gets committed to git

**Committed:** `summary.txt` files inside `history/<timestamp>/`. These
are small plain-text files (one line per test, pass/fail) that diff
nicely and let `git log` show how test results changed over time.

**Ignored:** HTML reports, coverage HTML, JUnit XML, stdout logs, the
`latest/` symlink, and `trends/`. These are regenerated on every run
and would bloat the repo.

## Retention policy

Local reports under `history/` accumulate forever unless pruned. There
is no automatic cleanup yet - when this becomes a concern, a cleanup
script will be added.

For now: if `history/` ever grows above ~1 GB, manually delete old
runs. The committed `summary.txt` files preserve the historical
record of what passed when.

## summary.txt format

One line per test, in the form:

    PASSED   tests/unit/test_parser.py::test_parse_asc_basic
    FAILED   tests/unit/test_parser.py::test_parse_asc_with_tx
    SKIPPED  tests/system/test_real_data.py::test_comma2k19_segment

Plus a footer summary line:

    TOTAL: 42 passed, 1 failed, 1 skipped

This format is human-readable, grep-able, and produces useful diffs
when committed.
