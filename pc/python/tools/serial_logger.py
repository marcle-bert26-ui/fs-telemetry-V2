"""Record decoded frames from the base serial port as CSV."""
import argparse, csv, time, serial
from pc.python.telemetry.protocol import extract_frames, FIELDS

ap = argparse.ArgumentParser()
ap.add_argument("port"); ap.add_argument("--baud", type=int, default=115200)
ap.add_argument("--out", default=f"log_{int(time.time())}.csv")
a = ap.parse_args()

buf = bytearray()
with serial.Serial(a.port, a.baud, timeout=0.1) as s, open(a.out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
    while True:
        buf += s.read(256)
        for fr in extract_frames(buf):
            w.writerow(fr); f.flush()
