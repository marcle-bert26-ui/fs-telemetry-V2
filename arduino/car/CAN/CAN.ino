// =====================================================================
//  Télémétrie voiture - ETAPE 1 : lecture CAN MaxxECU uniquement
//  Carte : Arduino Nano + module MCP2515
//  Moniteur série : 115200 bauds
//
//  Messages attendus (réglés dans MTune, little endian) :
//    0x600 : RPM | TPS | MAP | Lambda      (4 x 16 bits)
//    0x601 : Batterie | Eau | Air | EGT    (4 x 16 bits, températures signées)
// =====================================================================
#include <SPI.h>
#include <mcp_can.h>      // bibliothèque "mcp_can" de coryjfowler
#include <MsTimer2.h>

// ------------------------- Réglages -------------------------
#define PIN_CAN_CS      10
#define CAN_QUARTZ      MCP_8MHZ   // mets MCP_16MHZ si le quartz du module porte "16.000"
#define LISTEN_ONLY     1          // 0 = normal (acquitte, n'émet jamais), 1 = écoute seule
#define AFFICHER_BRUT   0          // 1 = affiche chaque trame CAN reçue (utile pour dépanner)

#define ID_MSG_A        0x600
#define ID_MSG_B        0x601

#define PERIODE_AFFICHAGE_MS  5000
#define TIMEOUT_CAN_MS        500

// ------------- Variables partagées avec l'interruption -------------
volatile uint16_t cptAffichage = PERIODE_AFFICHAGE_MS;
volatile bool     affichagePret = false;
volatile uint16_t cptTimeout = TIMEOUT_CAN_MS;
volatile bool     canTimeout = true;

// ------------------------- Variables CAN -------------------------
MCP_CAN CAN(PIN_CAN_CS);
bool canOk = false;

// Valeurs brutes reçues (unités = celles réglées dans MTune)
uint16_t rpm = 0, tps = 0, mapKpa = 0, lambda = 0, vbat = 0;
int16_t  clt = 0, iat = 0, egt = 0;

uint16_t nbMsgA = 0, nbMsgB = 0;   // compteurs pour vérifier la cadence



// ------------------------- Setup / loop -------------------------
void setup() {
  // Setup du mode Serial
  Serial.begin(115200);   


  // Setup de la lecture CAN
  canOk = (CAN.begin(MCP_STDEXT, CAN_500KBPS, CAN_QUARTZ) == CAN_OK);
  if (canOk) {
    CAN.setMode(LISTEN_ONLY ? MCP_LISTENONLY : MCP_NORMAL);
    Serial.println(F("CAN OK (500 kbit/s)"));
  } else {
    Serial.println(F("CAN ECHEC : verifier cablage, quartz (8/16 MHz) et alimentation 5 V"));
  }

  // Setup des interruptions temporelles
  MsTimer2::set(1, tocante);   // période 1 ms
  MsTimer2::start();
}

void loop() {
  if (canOk) lireCan();

  if (affichagePret) {
    noInterrupts(); 
    affichagePret = false; 
    interrupts();
    afficher();
  }
}

// ------------------------- Interruption 1 ms -------------------------
void tocante() {
  // Patie pour afiicher dans le lecteur serial toutes les PERIODE_AFFICHAGE_MS ms
  if (cptAffichage > 0) {
    cptAffichage--;
  } else {
    cptAffichage = PERIODE_AFFICHAGE_MS;
    affichagePret = true;
  }

  // Partie qui coupe la lecture CAN pendant l'ecriture
  if (cptTimeout > 0) {
    cptTimeout--;
  } else {
    canTimeout = true;
  }
}

// ------------------------- Affichage -------------------------
void afficher() {
  bool to;
  noInterrupts(); to = canTimeout; interrupts();

  Serial.print(F("0x600:")); Serial.print(nbMsgA);
  Serial.print(F("Hz 0x601:")); Serial.print(nbMsgB);
  Serial.print(F("Hz | RPM=")); Serial.print(rpm);
  Serial.print(F(" TPS=")); Serial.print(tps);
  Serial.print(F(" MAP=")); Serial.print(mapKpa);
  Serial.print(F(" LAMBDA=")); Serial.print(lambda);
  Serial.print(F(" | VBAT=")); Serial.print(vbat);
  Serial.print(F(" EAU=")); Serial.print(clt);
  Serial.print(F(" AIR=")); Serial.print(iat);
  Serial.print(F(" EGT=")); Serial.print(egt);
  Serial.println(to ? F(" | ECU: TIMEOUT") : F(" | ECU: OK"));

  nbMsgA = 0;
  nbMsgB = 0;
}


// ------------------------- Lecture 16 bits little endian -------------------------
uint16_t lireU16(const uint8_t *d, uint8_t i) {
  return (uint16_t)(d[i] | (d[i + 1] << 8));
}

// ------------------------- Lecture CAN -------------------------
void lireCan() {
  while (CAN.checkReceive() == CAN_MSGAVAIL) {
    unsigned long id;
    uint8_t len;
    uint8_t buf[8];

    if (CAN.readMsgBuf(&id, &len, buf) != CAN_OK) return;
    id &= 0x1FFFFFFFUL;   // retire les bits de drapeau ajoutés par la bibliothèque

#if AFFICHER_BRUT
    Serial.print(F("ID 0x")); Serial.print(id, HEX);
    Serial.print(F(" len ")); Serial.print(len);
    Serial.print(F(" :"));
    for (uint8_t i = 0; i < len; i++) { Serial.print(' '); Serial.print(buf[i], HEX); }
    Serial.println();
#endif

    if (len < 8) continue;

    if (id == ID_MSG_A) {
      rpm    = lireU16(buf, 0);
      tps    = lireU16(buf, 2);
      mapKpa = lireU16(buf, 4);
      lambda = lireU16(buf, 6);
      nbMsgA++;
    } else if (id == ID_MSG_B) {
      vbat = lireU16(buf, 0);
      clt  = (int16_t)lireU16(buf, 2);
      iat  = (int16_t)lireU16(buf, 4);
      egt  = (int16_t)lireU16(buf, 6);
      nbMsgB++;
    } else {
      continue;   // ID inconnu : ignoré
    }

    // Message ECU valide reçu : on relance le compteur de timeout
    noInterrupts();
    cptTimeout = TIMEOUT_CAN_MS;
    canTimeout = false;
    interrupts();
  }
}
