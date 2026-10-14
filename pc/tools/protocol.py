"""Encodage / décodage de la trame de télémétrie (miroir de telemetry_frame.h)."""
import struct

PROTOCOL_VERSION = 1
SYNC = b"\xA5\x5A"
FRAME_SIZE = 28
# sync0 sync1 version seq | t_ms | rpm tps map lambda vbat | clt iat egt | flags | crc
_FMT = "<BBBBIHHHHHhhhHH"
assert struct.calcsize(_FMT) == FRAME_SIZE

FIELDS = ("sync0", "sync1", "version", "seq", "t_ms", "rpm", "tps_d", "map_dkpa",
          "lambda_m", "vbat_c", "clt_d", "iat_d", "egt", "flags", "crc")


def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def encode(seq, t_ms, rpm, tps_d, map_dkpa, lambda_m, vbat_c, clt_d, iat_d, egt, flags=0) -> bytes:
    head = struct.pack(_FMT[:1] + "BBBBIHHHHHhhhH", 0xA5, 0x5A, PROTOCOL_VERSION, seq & 0xFF, t_ms,
                       rpm, tps_d, map_dkpa, lambda_m, vbat_c, clt_d, iat_d, egt, flags)
    return head + struct.pack("<H", crc16_ccitt(head[2:]))


def decode(frame: bytes) -> dict:
    if len(frame) != FRAME_SIZE:
        raise ValueError("taille invalide")
    values = dict(zip(FIELDS, struct.unpack(_FMT, frame)))
    if frame[:2] != SYNC:
        raise ValueError("sync invalide")
    if values["version"] != PROTOCOL_VERSION:
        raise ValueError("version inconnue")
    if values["crc"] != crc16_ccitt(frame[2:-2]):
        raise ValueError("CRC invalide")
    return values


def extract_frames(buffer: bytearray):
    """Extrait les trames valides d'un flux d'octets (re-synchronisation sur 0xA5 0x5A). Modifie buffer."""
    out = []
    while True:
        i = buffer.find(SYNC)
        if i < 0:
            del buffer[:-1]  # garde 1 octet au cas où 0xA5 est en fin de flux
            break
        if i > 0:
            del buffer[:i]
        if len(buffer) < FRAME_SIZE:
            break
        candidate = bytes(buffer[:FRAME_SIZE])
        try:
            out.append(decode(candidate))
            del buffer[:FRAME_SIZE]
        except ValueError:
            del buffer[:1]  # faux sync : on avance d'un octet
    return out
