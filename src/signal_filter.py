"""Filter diagnostic signals out of a summary before sending to the LLM.

The full Python summary is the engineer's source of truth and stays unfiltered.
This filter produces a noise-reduced view for LLM consumption only — the LLM
behaves more like a human reader who skips past checksums and counters.
"""

DIAGNOSTIC_PATTERNS = [
    "CHECKSUM",
    "CRC",
    "COUNTER",
    "ALIVE",
    "ENCODER",
    "RESERVED",
    "PAD",
    "UNUSED",
]


def is_diagnostic_signal(line: str) -> bool:
    """Return True if a summary line refers to a diagnostic-style signal.

    Match is case-insensitive, substring-based. Operates on the part of the
    line before the colon (the signal name), not the values, to avoid
    false positives from numeric data.
    """
    if ":" not in line:
        return False
    signal_name = line.split(":", 1)[0].upper()
    return any(pattern in signal_name for pattern in DIAGNOSTIC_PATTERNS)


def filter_for_llm(summary_text: str) -> str:
    """Return a copy of the summary with diagnostic signal lines removed.

    Adds a footer noting how many lines were dropped, so the LLM understands
    the view is curated rather than complete.
    """
    kept = []
    dropped = 0
    for line in summary_text.splitlines():
        if is_diagnostic_signal(line):
            dropped += 1
        else:
            kept.append(line)

    if dropped > 0:
        kept.append("")
        kept.append(
            f"Note: {dropped} diagnostic signal(s) "
            "(checksums, counters, CRC, alive flags, etc.) "
            "have been omitted from this view."
        )

    return "\n".join(kept)


if __name__ == "__main__":
    # Quick self-test
    sample = """CAN Log Python Summary
======================
Frames parsed: 100

Decoded Signals
===============
STEER_ANGLE_SENSOR.STEER_ANGLE: count=50, min=0.00, max=25.00, avg=12.50
STEER_ANGLE_SENSOR.CHECKSUM: count=50, min=0, max=255, avg=127.50
WHEEL_SPEEDS.WHEEL_SPEED_FR: count=25, min=30.00, max=40.00, avg=35.00
WHEEL_SPEEDS.COUNTER: count=25, min=0, max=15, avg=7.50
BRAKE_MODULE.BRAKE_PRESSURE: count=25, min=0.00, max=50.00, avg=10.00"""

    print("=== ORIGINAL ===")
    print(sample)
    print()
    print("=== FILTERED ===")
    print(filter_for_llm(sample))
