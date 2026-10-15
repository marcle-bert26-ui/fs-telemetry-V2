#pragma once

// ---- Brochage Nano (SPI partagé : D11 MOSI, D12 MISO, D13 SCK) ----
#define PIN_CAN_CS    10
#define PIN_CAN_INT    2
#define PIN_LORA_CS    8
#define PIN_LORA_RST   9
#define PIN_LORA_DIO0  3

// ---- CAN ----
#define CAN_MCP_CLOCK  MCP_8MHZ   // ATTENTION : vérifier le quartz du module (8 ou 16 MHz)
#define CAN_BITRATE    CAN_500KBPS
#define CAN_TIMEOUT_MS 500        // sans trame ECU pendant ce délai => FLAG_CAN_TIMEOUT

// ---- Sortie batterie MaxxECU (référence initiale, à calibrer sur le bus) ----
#ifndef CAN_BATTERY_ENABLED
#define CAN_BATTERY_ENABLED            1
#endif
#ifndef CAN_BATTERY_ID
#define CAN_BATTERY_ID                 0x601UL
#endif
#ifndef CAN_BATTERY_EXTENDED
#define CAN_BATTERY_EXTENDED           0
#endif
#ifndef CAN_BATTERY_BYTE_OFFSET
#define CAN_BATTERY_BYTE_OFFSET        0
#endif
#ifndef CAN_BATTERY_BIG_ENDIAN
#define CAN_BATTERY_BIG_ENDIAN         0
#endif
#ifndef CAN_BATTERY_SCALE_NUMERATOR
#define CAN_BATTERY_SCALE_NUMERATOR    1UL
#endif
#ifndef CAN_BATTERY_SCALE_DENOMINATOR
#define CAN_BATTERY_SCALE_DENOMINATOR  1UL
#endif
#ifndef CAN_BATTERY_OFFSET_CV
#define CAN_BATTERY_OFFSET_CV          0L
#endif

// ---- Radio ----
#define LORA_FREQ_HZ   868E6
#define LORA_SF        7
#define LORA_BW_HZ     250E3
#define LORA_TX_DBM    14         // limite légale EU 868 MHz (selon sous-bande) : à vérifier
#define TX_PERIOD_MS   100        // 10 Hz

// ---- Divers ----
#define SERIAL_DEBUG   1
