import cantools
from pathlib import Path

dbc = cantools.database.load_file("data/dbcs/toyota.dbc")
msg = dbc.get_message_by_name("SPEED")

speeds = [0, 5, 12, 25, 40, 55, 70, 85, 100, 80, 50, 20, 0]

lines = [
    "date Sun May 03 08:00:00.000 2026",
    "base hex  timestamps absolute",
    "internal events logged",
    "Begin Triggerblock Thu Jan 01 01:00:00.0 1970",
    " 0.000000 Start of measurement",
]

for i, speed in enumerate(speeds):
    data = msg.encode({
        "ENCODER": i % 256,
        "SPEED": speed,
        "CHECKSUM": 0,
    })

    hex_bytes = " ".join(f"{b:02X}" for b in data)
    lines.append(f" {i * 0.100000:.6f} 2 0B4 Rx d 8 {hex_bytes}")

lines.append("End Triggerblock")

Path("data/samples/speed_sample.asc").write_text("\n".join(lines) + "\n")

print("Created data/samples/speed_sample.asc")
