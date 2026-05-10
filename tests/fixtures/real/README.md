# Real-world test fixtures

CAN log data sourced from comma.ai's openpilot fleet. Used as the basis
for system-level tests that exercise the full pipeline against realistic
production data.

## Source

Data from the **comma2k19** dataset:

- Repository: https://github.com/commaai/comma2k19
- Description: 33 hours of California highway driving, 2019 segments,
  collected with comma EONs from a Toyota over a 20km section of
  California's 280 highway.

## License

The comma2k19 dataset is published by comma.ai under terms documented
in their repository. The example segment included here is for
non-commercial research and development use.

When this project is used commercially, real-data tests using this
fixture should either be skipped or replaced with synthetic equivalents.

## Conversion

comma2k19 ships in capnp format, not ASC. Frames are extracted and
written as ASC using a conversion script (to be added in
`tests/fixtures/real/scripts/`).

The conversion preserves:
- Timestamps (relative to segment start)
- CAN arbitration IDs
- Channel numbers
- Frame data bytes
- DLC

The conversion does NOT preserve:
- Original capnp metadata
- Camera frames
- IMU data
- GPS data

## Files

(To be populated as fixtures are added.)
