// Firmware voiture : CAN (listen-only) -> TelemetryFrame -> LoRa 868 MHz
#include <Arduino.h>
#include <SPI.h>
#include <mcp_can.h>
#include <LoRa.h>
#include <avr/wdt.h>
#include "config.h"
#include "can_map.h"
#include "telemetry_frame.h"

static MCP_CAN can(PIN_CAN_CS);
static TelemetryFrame frame;
static uint32_t lastCanMs = 0;
static uint32_t lastTxMs  = 0;
static bool canOk = false;

static void pollCan() {
  while (can.checkReceive() == CAN_MSGAVAIL) {
    unsigned long id;
    uint8_t len;
    uint8_t buf[8];
    if (can.readMsgBuf(&id, &len, buf) != CAN_OK) return;
    bool extended = (id & CAN_ID_EXTENDED_FLAG) != 0;
    id &= CAN_ID_VALUE_MASK;  // retire les bits de flag (extended/RTR) de la lib
    if (can_decode(id, extended, buf, len, &frame)) lastCanMs = millis();
  }
}

static void sendFrame() {
  uint32_t now = millis();
  frame.t_ms = now;
  frame.seq++;
  if (now - lastCanMs > CAN_TIMEOUT_MS) frame.flags |= FLAG_CAN_TIMEOUT;
  else frame.flags &= (uint16_t)~FLAG_CAN_TIMEOUT;
  frame_seal(&frame);

  LoRa.beginPacket();
  LoRa.write((const uint8_t *)&frame, FRAME_SIZE);
  LoRa.endPacket(true);  // asynchrone : ne bloque pas la lecture CAN
}

void setup() {
#if SERIAL_DEBUG
  Serial.begin(115200);
#endif
  frame_init(&frame);

  canOk = (can.begin(MCP_STDEXT, CAN_BITRATE, CAN_MCP_CLOCK) == CAN_OK);
  if (canOk) can.setMode(MCP_LISTENONLY);  // ne jamais émettre / acquitter sur le bus ECU
#if SERIAL_DEBUG
  Serial.println(canOk ? F("CAN ok") : F("CAN FAIL"));
#endif

  LoRa.setPins(PIN_LORA_CS, PIN_LORA_RST, PIN_LORA_DIO0);
  bool loraOk = LoRa.begin((long)LORA_FREQ_HZ);
  if (loraOk) {
    LoRa.setSpreadingFactor(LORA_SF);
    LoRa.setSignalBandwidth((long)LORA_BW_HZ);
    LoRa.setTxPower(LORA_TX_DBM);
    LoRa.enableCrc();
  }
#if SERIAL_DEBUG
  Serial.println(loraOk ? F("LoRa ok") : F("LoRa FAIL"));
#endif

  wdt_enable(WDTO_1S);
}

void loop() {
  wdt_reset();
  if (canOk) pollCan();

  uint32_t now = millis();
  if (now - lastTxMs >= TX_PERIOD_MS) {
    lastTxMs = now;
    sendFrame();
  }
}
