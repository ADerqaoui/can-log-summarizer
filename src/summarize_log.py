import sys
import cantools
from parser import parse_asc
from llm_backend import ask_ollama
from signal_filter import filter_for_llm

DEFAULT_MODEL = "llama3.1:8b"

DEFAULT_PROMPT_TEMPLATE = """
You are an automotive HIL/V&V engineer.

Interpret the following decoded CAN log summary.

Rules:
- Do not invent signals.
- Only discuss signals listed in the Python summary.
- Mention if many frames were unknown or decoding coverage is low.
- Keep the explanation useful for a test engineer.
- Use clear engineering language.
- Diagnostic signals (checksums, CRCs, counters, alive flags) have been filtered out before this summary reached you. Do not speculate about their absence.

Return:
1. Overall interpretation
2. Notable signal behavior
3. Possible test scenario
4. Data quality notes

CAN SUMMARY:
{summary}
"""

def summarize_values(values):
    numeric = [v for v in values if isinstance(v, (int, float))]

    if not numeric:
        return {
            "count": len(values),
            "latest": values[-1] if values else None
        }

    return {
        "count": len(numeric),
        "min": min(numeric),
        "max": max(numeric),
        "avg": sum(numeric) / len(numeric),
        "first": numeric[0],
        "last": numeric[-1],
    }

def build_python_summary(frames, decoded_frames,
                         unknown_frames,
                         decode_errors,
                         signals,
                         dbc_path,
                         log_path):

    lines = []

    lines.append("CAN Log Python Summary")
    lines.append("======================")
    lines.append(f"DBC file: {dbc_path}")
    lines.append(f"Log file: {log_path}")
    lines.append(f"Frames parsed: {len(frames)}")
    lines.append(f"Decoded frames: {decoded_frames}")
    lines.append(f"Unknown frames: {unknown_frames}")
    lines.append(f"Decode errors: {decode_errors}")
    lines.append("")
    lines.append("Decoded Signals")
    lines.append("===============")

    for signal, values in sorted(signals.items()):
        summary = summarize_values(values)

        if "min" in summary:
            lines.append(
                f"{signal}: "
                f"count={summary['count']}, "
                f"min={summary['min']:.2f}, "
                f"max={summary['max']:.2f}, "
                f"avg={summary['avg']:.2f}, "
                f"first={summary['first']:.2f}, "
                f"last={summary['last']:.2f}"
            )
        else:
            lines.append(
                f"{signal}: "
                f"count={summary['count']}, "
                f"latest={summary['latest']}"
            )

    return "\n".join(lines)

def main():

    dbc_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "data/dbcs/toyota.dbc"
    )

    log_path = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "data/samples/speed_sample.asc"
    )

    model_name = (
        sys.argv[3]
        if len(sys.argv) > 3
        else DEFAULT_MODEL
    )

    dbc = cantools.database.load_file(dbc_path)
    frames = parse_asc(log_path)

    decoded_frames = 0
    unknown_frames = 0
    decode_errors = 0

    signals = {}

    for frame in frames:

        try:
            msg = dbc.get_message_by_frame_id(frame["can_id"])
            decoded = msg.decode(frame["data"])

            decoded_frames += 1

            for signal_name, value in decoded.items():

                key = f"{msg.name}.{signal_name}"

                if key not in signals:
                    signals[key] = []

                signals[key].append(value)

        except KeyError:
            unknown_frames += 1

        except Exception:
            decode_errors += 1

    py_summary = build_python_summary(
        frames,
        decoded_frames,
        unknown_frames,
        decode_errors,
        signals,
        dbc_path,
        log_path
    )

    llm_summary = filter_for_llm(py_summary)
    prompt = DEFAULT_PROMPT_TEMPLATE.format(
        summary=llm_summary
    )

    llm_interpretation = ask_ollama(
        prompt,
        model=model_name
    )

    print(py_summary)
    print()
    print(f"LLM Interpretation ({model_name})")
    print("================================")
    print(llm_interpretation)

if __name__ == "__main__":
    main()
