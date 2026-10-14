// Firmware base (stand) : LoRa -> validation -> USB série (trame binaire brute, 115200 bauds)
#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include "telemetry_frame.h"

#define PIN_LORA_CS   10
#define PIN_LORA_RST   9
#define PIN_LORA_DIO0  2
#define LORA_FREQ_HZ  868E6
#define LORA_SF       7
#define LORA_BW_HZ    250E3

static TelemetryFrame rx;

void setup() {
  Serial.begin(115200);
  LoRa.setPins(PIN_LORA_CS, PIN_LORA_RST, PIN_LORA_DIO0);
  while (!LoRa.begin((long)LORA_FREQ_HZ)) delay(250);
  LoRa.setSpreadingFactor(LORA_SF);
  LoRa.setSignalBandwidth((long)LORA_BW_HZ);
  LoRa.enableCrc();
}

void loop() {
  int size = LoRa.parsePacket();
  if (size != FRAME_SIZE) {
    while (LoRa.available()) LoRa.read();  // purge si taille inattendue
    return;
  }
  uint8_t *p = (uint8_t *)&rx;
  for (int i = 0; i < FRAME_SIZE; i++) p[i] = (uint8_t)LoRa.read();
  if (frame_valid(&rx)) {
    Serial.write(p, FRAME_SIZE);  // le PC re-synchronise sur 0xA5 0x5A et recontrôle le CRC
  }
  // TODO (backlog) : trame de lien séparée avec RSSI/SNR (LoRa.packetRssi())
}
