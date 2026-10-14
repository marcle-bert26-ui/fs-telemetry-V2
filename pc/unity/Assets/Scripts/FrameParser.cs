using System;
using System.Collections.Generic;

namespace FsTelemetry
{
    /// <summary>Trame décodée, en unités physiques. Miroir de firmware/common/telemetry_frame.h.</summary>
    public struct TelemetryData
    {
        public byte Seq;
        public uint TimeMs;
        public int Rpm;
        public float TpsPercent;
        public float MapKpa;
        public float Lambda;
        public float VbatV;
        public float CoolantC;
        public float IntakeC;
        public int EgtC;
        public ushort Flags;
        public bool CanTimeout => (Flags & 1) != 0;
    }

    /// <summary>Parseur de flux octets -> trames. Appeler Feed() depuis le thread de lecture série.</summary>
    public class FrameParser
    {
        public const int FrameSize = 28;
        public const byte ProtocolVersion = 1;
        private readonly List<byte> _buf = new List<byte>(256);

        public static ushort Crc16(byte[] d, int start, int len)
        {
            ushort crc = 0xFFFF;
            for (int i = start; i < start + len; i++)
            {
                crc ^= (ushort)(d[i] << 8);
                for (int b = 0; b < 8; b++)
                    crc = (crc & 0x8000) != 0 ? (ushort)((crc << 1) ^ 0x1021) : (ushort)(crc << 1);
            }
            return crc;
        }

        public List<TelemetryData> Feed(byte[] data, int count)
        {
            var result = new List<TelemetryData>();
            for (int i = 0; i < count; i++) _buf.Add(data[i]);

            while (true)
            {
                int s = IndexOfSync();
                if (s < 0) { if (_buf.Count > 1) _buf.RemoveRange(0, _buf.Count - 1); break; }
                if (s > 0) _buf.RemoveRange(0, s);
                if (_buf.Count < FrameSize) break;

                byte[] f = _buf.GetRange(0, FrameSize).ToArray();
                if (TryDecode(f, out var t)) { result.Add(t); _buf.RemoveRange(0, FrameSize); }
                else _buf.RemoveAt(0);
            }
            return result;
        }

        private int IndexOfSync()
        {
            for (int i = 0; i + 1 < _buf.Count; i++)
                if (_buf[i] == 0xA5 && _buf[i + 1] == 0x5A) return i;
            return -1;
        }

        public static bool TryDecode(byte[] f, out TelemetryData t)
        {
            t = default;
            if (f.Length != FrameSize || f[0] != 0xA5 || f[1] != 0x5A || f[2] != ProtocolVersion) return false;
            if (BitConverter.ToUInt16(f, 26) != Crc16(f, 2, FrameSize - 4)) return false;

            // Little-endian (AVR et x86/ARM) : BitConverter OK. Valeurs INVALID_* (0xFFFF / 0x8000) à gérer en UI.
            t.Seq = f[3];
            t.TimeMs = BitConverter.ToUInt32(f, 4);
            t.Rpm = BitConverter.ToUInt16(f, 8);
            t.TpsPercent = BitConverter.ToUInt16(f, 10) / 10f;
            t.MapKpa = BitConverter.ToUInt16(f, 12) / 10f;
            t.Lambda = BitConverter.ToUInt16(f, 14) / 1000f;
            t.VbatV = BitConverter.ToUInt16(f, 16) / 100f;
            t.CoolantC = BitConverter.ToInt16(f, 18) / 10f;
            t.IntakeC = BitConverter.ToInt16(f, 20) / 10f;
            t.EgtC = BitConverter.ToInt16(f, 22);
            t.Flags = BitConverter.ToUInt16(f, 24);
            return true;
        }
    }
}
