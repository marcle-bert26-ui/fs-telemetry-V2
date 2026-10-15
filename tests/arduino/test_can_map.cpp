#include <assert.h>
#include <stdint.h>

#include "can_map.h"

static void write_raw(uint8_t *payload, uint16_t raw) {
#if CAN_BATTERY_BIG_ENDIAN
  payload[CAN_BATTERY_BYTE_OFFSET] = (uint8_t)(raw >> 8);
  payload[CAN_BATTERY_BYTE_OFFSET + 1] = (uint8_t)raw;
#else
  payload[CAN_BATTERY_BYTE_OFFSET] = (uint8_t)raw;
  payload[CAN_BATTERY_BYTE_OFFSET + 1] = (uint8_t)(raw >> 8);
#endif
}

int main() {
  TelemetryFrame frame;
  frame_init(&frame);
  uint8_t payload[8] = {};
  const uint16_t raw = 1380;
  write_raw(payload, raw);
  const int32_t expected =
      (int32_t)(((uint32_t)raw * CAN_BATTERY_SCALE_NUMERATOR) /
                CAN_BATTERY_SCALE_DENOMINATOR) +
      CAN_BATTERY_OFFSET_CV;

  assert(can_decode(CAN_BATTERY_ID, CAN_BATTERY_EXTENDED != 0, payload,
                    sizeof(payload), &frame));
  assert((int32_t)frame.vbat_c == expected);

  const uint16_t previous = frame.vbat_c;
  assert(!can_decode(CAN_BATTERY_ID + 1, CAN_BATTERY_EXTENDED != 0, payload,
                     sizeof(payload), &frame));
  assert(frame.vbat_c == previous);
  assert(!can_decode(CAN_BATTERY_ID, CAN_BATTERY_EXTENDED == 0, payload,
                     sizeof(payload), &frame));
  assert(!can_decode(CAN_BATTERY_ID, CAN_BATTERY_EXTENDED != 0, payload,
                     CAN_BATTERY_BYTE_OFFSET + 1, &frame));
  assert(!can_decode(CAN_BATTERY_ID, CAN_BATTERY_EXTENDED != 0, payload, 9,
                     &frame));
  assert(!can_decode(CAN_BATTERY_ID, CAN_BATTERY_EXTENDED != 0, NULL,
                     sizeof(payload), &frame));

  uint8_t invalid_payload[8] = {};
  write_raw(invalid_payload, INVALID_U16);
  assert(!can_decode(CAN_BATTERY_ID, CAN_BATTERY_EXTENDED != 0,
                     invalid_payload, sizeof(invalid_payload), &frame));
  assert(frame.vbat_c == previous);
  return 0;
}
