import cantools
from parser import parse_asc

dbc = cantools.database.load_file("data/dbcs/toyota.dbc")
frames = parse_asc("data/samples/sample.asc")

decoded = 0
unknown = 0

for frame in frames:
    try:
        msg = dbc.get_message_by_frame_id(frame["can_id"])
        signals = msg.decode(frame["data"])
        print(frame["time"], hex(frame["can_id"]), msg.name, signals)
        decoded += 1
    except KeyError:
        unknown += 1
    except Exception as e:
        print("Decode error:", hex(frame["can_id"]), e)

print()
print(f"Decoded: {decoded}")
print(f"Unknown CAN IDs: {unknown}")
