#include <SPI.h>
#include <mcp_can.h>
#define PIN_CAN_CS 10
#define CAN_QUARTZ MCP_8MHZ
MCP_CAN CAN(PIN_CAN_CS);
uint32_t tA = 0, tB = 0;

void put16(byte *d, byte i, uint16_t v) { d[i] = v & 0xFF; d[i + 1] = v >> 8; }

void setup() {
  Serial.begin(115200);
  if (CAN.begin(MCP_STDEXT, CAN_500KBPS, CAN_QUARTZ) != CAN_OK) { Serial.println("CAN ECHEC"); while (1); }
  CAN.setMode(MCP_NORMAL);
}

void loop() {
  uint32_t now = millis();
  if (now - tA >= 50) {          // 20 Hz
    tA = now;
    byte d[8];
    put16(d, 0, 8000); put16(d, 2, 500); put16(d, 4, 1000); put16(d, 6, 1000);
    CAN.sendMsgBuf(0x600, 0, 8, d);
  }
  if (now - tB >= 100) {         // 10 Hz
    tB = now;
    byte d[8];
    put16(d, 0, 1380); put16(d, 2, 900); put16(d, 4, (uint16_t)(int16_t)-150); put16(d, 6, 700);
    CAN.sendMsgBuf(0x601, 0, 8, d);
  }
}