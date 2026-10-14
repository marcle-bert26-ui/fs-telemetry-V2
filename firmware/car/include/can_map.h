#pragma once
// Décodage des trames CAN de la MaxxECU (protocole "MaxxECU Default 1.2/1.3").
//
// A FAIRE (issue "Identifier les CAN ID MaxxECU") :
//   - relever IDs, offsets, tailles, endianness, échelles dans la doc MaxxECU
//     (section "Default CAN output") ET les confirmer en sniffant le bus.
//   - ne rien deviner : tant qu'un ID est UNSET, la valeur reste INVALID.
#include <stdint.h>
#include "telemetry_frame.h"

#define CANID_UNSET 0xFFFFFFFFUL

// Renseigner ici après vérification :
#define CANID_FAST_A  CANID_UNSET   // ex : RPM, TPS, MAP, lambda...
#define CANID_SLOW_A  CANID_UNSET   // ex : températures, tension batterie...

// Retourne true si la trame CAN a mis à jour le TelemetryFrame.
static inline bool can_decode(uint32_t id, const uint8_t *d, uint8_t len, TelemetryFrame *f) {
  (void)d; (void)len; (void)f;
  if (id == CANID_UNSET) return false;
  // TODO: switch (id) { case CANID_FAST_A: f->rpm = d[0] | (d[1] << 8); ... }
  return false;
}
