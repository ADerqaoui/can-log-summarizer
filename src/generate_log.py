"""Generate a synthetic CAN log using a Toyota DBC for testing the parser."""
import can
import cantools
import random
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DBC_FILE = PROJECT_ROOT / "data" / "dbcs" / "toyota.dbc"
OUTPUT_FILE = PROJECT_ROOT / "data" / "samples" / "sample.asc"
DURATION_S = 5.0
FAKE_DATE = datetime(2026, 5, 3, 8, 0, 0)
NUM_ERROR_FRAMES = 3

def steer_signals(t):
    return {"STEER_ANGLE": 5.0 * t, "STEER_FRACTION": 0.0, "STEER_RATE": 5.0}

def wheel_signals(t):
    base = 30.0 + t * 2
    return {
        "WHEEL_SPEED_FR": base,
        "WHEEL_SPEED_FL": base,
        "WHEEL_SPEED_RR": base - 0.2,
        "WHEEL_SPEED_RL": base - 0.2,
    }

def brake_signals(t):
    pressure = 50.0 if 2.8 < t < 3.4 else 0.0
    return {"BRAKE_PRESSURE": pressure, "BRAKE_PRESSED": 1 if pressure > 0 else 0}

def gear_signals(t):
    return {"GEAR": 8}

MESSAGES = [
    ("STEER_ANGLE_SENSOR", 0.010, steer_signals),
    ("WHEEL_SPEEDS",       0.020, wheel_signals),
    ("BRAKE_MODULE",       0.020, brake_signals),
    ("GEAR_PACKET",        0.100, gear_signals),
]

def safe_encode(db, msg_name, signals):
    msg_def = db.get_message_by_name(msg_name)
    full = {sig.name: 0 for sig in msg_def.signals}
    for k, v in signals.items():
        if k in full:
            full[k] = v
    return msg_def.encode(full), msg_def.frame_id

def generate_log():
    db = cantools.database.load_file(str(DBC_FILE))

    with open(OUTPUT_FILE, "w") as f:
        writer = can.io.ASCWriter(f)
        next_send = {name: 0.0 for name, _, _ in MESSAGES}
        t = 0.0
        frame_count = 0
        error_times = sorted(random.sample(
            [round(x * 0.1, 1) for x in range(5, int(DURATION_S * 10))],
            NUM_ERROR_FRAMES))

        while t <= DURATION_S:
            for name, cycle, sig_func in MESSAGES:
                if t >= next_send[name]:
                    try:
                        data, frame_id = safe_encode(db, name, sig_func(t))
                        msg = can.Message(
                            timestamp=t,
                            arbitration_id=frame_id,
                            data=data,
                            is_extended_id=False,
                            channel=1,
                        )
                        writer.on_message_received(msg)
                        frame_count += 1
                    except Exception as e:
                        print(f"  WARN: could not encode {name}: {e}")
                    next_send[name] += cycle

            if error_times and abs(t - error_times[0]) < 0.005:
                err = can.Message(timestamp=t, is_error_frame=True, channel=1)
                writer.on_message_received(err)
                error_times.pop(0)
                frame_count += 1

            t += 0.001

        writer.stop()

    fake_date_str = FAKE_DATE.strftime("%a %b %d %H:%M:%S.000 %Y")
    with open(OUTPUT_FILE, "r") as f:
        lines = f.readlines()
    lines[0] = f"date {fake_date_str}\n"
    with open(OUTPUT_FILE, "w") as f:
        f.writelines(lines)

    print(f"Wrote {frame_count} frames over {DURATION_S} s to {OUTPUT_FILE}")
    print(f"  ~{NUM_ERROR_FRAMES} ErrorFrames sprinkled in")
    print(f"  Header date overwritten to {fake_date_str}")

if __name__ == "__main__":
    generate_log()
