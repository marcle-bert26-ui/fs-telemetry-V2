// Trame de télémétrie - partagée voiture / base. Voir docs/protocol.md
// Toute modification => incrémenter PROTOCOL_VERSION + MAJ docs, FrameParser.cs, tests.
#pragma once
#include <stdint.h>

#define PROTOCOL_VERSION 1
#define FRAME_SYNC0 0xA5
#define FRAME_SYNC1 0x5A

// Valeur "donnée absente / périmée"
#define INVALID_U16 0xFFFF
#define INVALID_I16 ((int16_t)0x8000)

// Bits du champ flags
#define FLAG_CAN_TIMEOUT  (1u << 0)  // plus de trame ECU reçue
#define FLAG_ECU_ALIVE    (1u << 1)
#define FLAG_LOW_VBAT     (1u << 2)

typedef struct __attribute__((packed)) {
  uint8_t  sync0;      // 0xA5
  uint8_t  sync1;      // 0x5A
  uint8_t  version;    // PROTOCOL_VERSION
  uint8_t  seq;        // compteur circulaire (détection de pertes)
  uint32_t t_ms;       // millis() côté voiture
  uint16_t rpm;        // tr/min
  uint16_t tps_d;      // 0.1 %
  uint16_t map_dkpa;   // 0.1 kPa
  uint16_t lambda_m;   // 0.001 lambda
  uint16_t vbat_c;     // 0.01 V
  int16_t  clt_d;      // 0.1 °C  (eau)
  int16_t  iat_d;      // 0.1 °C  (air admission)
  int16_t  egt;        // 1 °C
  uint16_t flags;
  uint16_t crc;        // CRC16-CCITT-FALSE sur octets [2 .. 25]
} TelemetryFrame;

#define FRAME_SIZE 28
static_assert(sizeof(TelemetryFrame) == FRAME_SIZE, "TelemetryFrame size mismatch");

// CRC16-CCITT-FALSE : poly 0x1021, init 0xFFFF, sans reflexion, xorout 0
static inline uint16_t crc16_ccitt(const uint8_t *data, uint16_t len) {
  uint16_t crc = 0xFFFF;
  while (len--) {
    crc ^= (uint16_t)(*data++) << 8;
    for (uint8_t i = 0; i < 8; i++)
      crc = (crc & 0x8000) ? (uint16_t)((crc << 1) ^ 0x1021) : (uint16_t)(crc << 1);
  }
  return crc;
}

static inline void frame_init(TelemetryFrame *f) {
  f->sync0 = FRAME_SYNC0; f->sync1 = FRAME_SYNC1; f->version = PROTOCOL_VERSION;
  f->seq = 0; f->t_ms = 0;
  f->rpm = f->tps_d = f->map_dkpa = f->lambda_m = f->vbat_c = INVALID_U16;
  f->clt_d = f->iat_d = f->egt = INVALID_I16;
  f->flags = 0; f->crc = 0;
}

static inline void frame_seal(TelemetryFrame *f) {
  f->crc = crc16_ccitt(((const uint8_t *)f) + 2, FRAME_SIZE - 4);
}

static inline bool frame_valid(const TelemetryFrame *f) {
  return f->sync0 == FRAME_SYNC0 && f->sync1 == FRAME_SYNC1 &&
         f->version == PROTOCOL_VERSION &&
         f->crc == crc16_ccitt(((const uint8_t *)f) + 2, FRAME_SIZE - 4);
}
