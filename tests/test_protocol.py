import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pc", "tools"))
from protocol import encode, decode, extract_frames, crc16_ccitt, FRAME_SIZE

# Vecteur de référence : à reprendre à l'identique dans les tests C et C# (voir docs/protocol.md)
GOLDEN_FIELDS = dict(seq=1, t_ms=1000, rpm=8000, tps_d=500, map_dkpa=1000, lambda_m=1000,
                     vbat_c=1380, clt_d=900, iat_d=350, egt=700, flags=2)
GOLDEN_HEX = "A55A0101E8030000401FF401E803E803640584035E01BC020200E5BF"


class TestProtocol(unittest.TestCase):
    def test_crc_check_value(self):
        # valeur de contrôle standard CRC-16/CCITT-FALSE
        self.assertEqual(crc16_ccitt(b"123456789"), 0x29B1)

    def test_golden_vector(self):
        self.assertEqual(encode(**GOLDEN_FIELDS).hex().upper(), GOLDEN_HEX)

    def test_roundtrip(self):
        d = decode(encode(**GOLDEN_FIELDS))
        self.assertEqual(d["rpm"], 8000)
        self.assertEqual(d["clt_d"], 900)
        self.assertEqual(len(encode(**GOLDEN_FIELDS)), FRAME_SIZE)

    def test_negative_temperature(self):
        f = dict(GOLDEN_FIELDS, iat_d=-150)
        self.assertEqual(decode(encode(**f))["iat_d"], -150)

    def test_corrupted_crc_rejected(self):
        b = bytearray(encode(**GOLDEN_FIELDS)); b[10] ^= 0x01
        with self.assertRaises(ValueError):
            decode(bytes(b))

    def test_stream_resync(self):
        good = encode(**GOLDEN_FIELDS)
        buf = bytearray(b"\x00\xA5\x01\xFF" + good + b"\xA5" + good)
        frames = extract_frames(buf)
        self.assertEqual(len(frames), 2)


if __name__ == "__main__":
    unittest.main()
