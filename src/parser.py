from pathlib import Path
import re

ASC_FRAME_RE = re.compile(
    r"^\s*(?P<time>\d+\.\d+)\s+(?P<channel>\d+)\s+(?P<can_id>[0-9A-Fa-f]+)x?\s+Rx\s+d\s+(?P<dlc>\d+)\s+(?P<data>(?:[0-9A-Fa-f]{2}\s*)+)"
)

def parse_asc(path: str):
    frames = []
    for line in Path(path).read_text(errors="ignore").splitlines():
        m = ASC_FRAME_RE.match(line)
        if not m:
            continue

        frames.append({
            "time": float(m.group("time")),
            "channel": int(m.group("channel")),
            "can_id": int(m.group("can_id"), 16),
            "dlc": int(m.group("dlc")),
            "data": bytes.fromhex(m.group("data")),
        })
    return frames

if __name__ == "__main__":
    frames = parse_asc("data/samples/sample.asc")
    print(f"Parsed {len(frames)} frames")
    for f in frames[:10]:
        print(f)
