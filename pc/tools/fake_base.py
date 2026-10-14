"""Simule la station de base : génère des trames réalistes pour développer Unity sans hardware.

Usage :
  python pc/tools/fake_base.py --tcp 5555            # serveur TCP (Unity se connecte à 127.0.0.1:5555)
  python pc/tools/fake_base.py --serial COM7         # envoie sur un port série (paire virtuelle com0com / socat)
Options : --hz 10  --drop 0.05 (taux de pertes simulé)  --corrupt 0.02 (trames corrompues)
"""
import argparse, math, random, socket, time
from protocol import encode


def sample(seq, t):
    rpm = int(6000 + 4000 * math.sin(t * 0.8))
    tps = int(500 + 500 * math.sin(t * 0.8 + 0.4))         # 0.1 %
    mapk = int(1000 + 600 * max(0, math.sin(t * 0.8)))      # 0.1 kPa
    lam = int(1000 - 80 * math.sin(t * 1.5))                # 0.001
    vbat = int(1350 + 20 * math.sin(t * 0.3))               # 0.01 V
    clt = int(850 + 5 * t) if t < 20 else 900               # 0.1 °C
    iat = int(350 + 10 * math.sin(t * 0.1))
    egt = int(650 + 150 * max(0, math.sin(t * 0.8)))
    return encode(seq, int(t * 1000), rpm, tps, mapk, lam, vbat, clt, iat, egt, flags=0b10)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tcp", type=int)
    g.add_argument("--serial")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--hz", type=float, default=10)
    ap.add_argument("--drop", type=float, default=0.0)
    ap.add_argument("--corrupt", type=float, default=0.0)
    a = ap.parse_args()

    if a.tcp:
        srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", a.tcp)); srv.listen(1)
        print(f"En attente d'un client sur 127.0.0.1:{a.tcp} ...")
        conn, _ = srv.accept(); send = conn.sendall
    else:
        import serial
        port = serial.Serial(a.serial, a.baud); send = port.write

    seq, t0 = 0, time.time()
    while True:
        frame = bytearray(sample(seq, time.time() - t0)); seq += 1
        if random.random() >= a.drop:
            if random.random() < a.corrupt:
                frame[random.randrange(2, 26)] ^= 0xFF
            send(bytes(frame))
        time.sleep(1 / a.hz)


if __name__ == "__main__":
    main()
