#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "config.h"
#include "telemetry_frame.h"

#define CAN_ID_EXTENDED_FLAG 0x80000000UL
#define CAN_ID_VALUE_MASK    0x1FFFFFFFUL

#if CAN_BATTERY_ENABLED
static_assert(CAN_BATTERY_EXTENDED == 0 || CAN_BATTERY_EXTENDED == 1,
              "CAN_BATTERY_EXTENDED must be 0 or 1");
static_assert(CAN_BATTERY_BIG_ENDIAN == 0 || CAN_BATTERY_BIG_ENDIAN == 1,
              "CAN_BATTERY_BIG_ENDIAN must be 0 or 1");
static_assert(CAN_BATTERY_ID <= (CAN_BATTERY_EXTENDED ? 0x1FFFFFFFUL : 0x7FFUL),
              "CAN_BATTERY_ID is out of range for its CAN frame type");
static_assert(CAN_BATTERY_BYTE_OFFSET <= 6,
              "CAN_BATTERY_BYTE_OFFSET must leave room for two bytes in a CAN frame");
static_assert(CAN_BATTERY_SCALE_DENOMINATOR > 0,
              "CAN_BATTERY_SCALE_DENOMINATOR must be greater than zero");
static_assert(CAN_BATTERY_SCALE_NUMERATOR <= 32767UL,
              "CAN_BATTERY_SCALE_NUMERATOR must not exceed 32767");
static_assert(CAN_BATTERY_SCALE_DENOMINATOR <= 32767UL,
              "CAN_BATTERY_SCALE_DENOMINATOR must not exceed 32767");
static_assert(CAN_BATTERY_OFFSET_CV >= -32768L && CAN_BATTERY_OFFSET_CV <= 32767L,
              "CAN_BATTERY_OFFSET_CV must fit in a signed 16-bit value");
#endif

static inline bool can_decode(uint32_t id, bool extended, const uint8_t *d,
                              uint8_t len, TelemetryFrame *f) {
#if CAN_BATTERY_ENABLED
  if (d == NULL || f == NULL || len > 8) return false;
  if (id != CAN_BATTERY_ID || extended != (CAN_BATTERY_EXTENDED != 0)) return false;
  if (len < CAN_BATTERY_BYTE_OFFSET + 2) return false;

  uint16_t raw;
#if CAN_BATTERY_BIG_ENDIAN
  raw = ((uint16_t)d[CAN_BATTERY_BYTE_OFFSET] << 8) |
        d[CAN_BATTERY_BYTE_OFFSET + 1];
#else
  raw = d[CAN_BATTERY_BYTE_OFFSET] |
        ((uint16_t)d[CAN_BATTERY_BYTE_OFFSET + 1] << 8);
#endif
  if (raw == INVALID_U16) return false;

  int32_t valueCv =
      (int32_t)(((uint32_t)raw * CAN_BATTERY_SCALE_NUMERATOR) /
                CAN_BATTERY_SCALE_DENOMINATOR) +
      CAN_BATTERY_OFFSET_CV;
  if (valueCv < 0 || valueCv >= INVALID_U16) return false;

  f->vbat_c = (uint16_t)valueCv;
  return true;
#else
  (void)id;
  (void)extended;
  (void)d;
  (void)len;
  (void)f;
  return false;
#endif
}
