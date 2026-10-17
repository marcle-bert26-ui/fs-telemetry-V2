
// -------------- Interruption timer ----------

// on va enlever tous les delay pour ca on met des variables qui se réduise jusqu'a 0 quand le delay est passé pour attend le code ne sera pas bloqué par le delay
#include <MsTimer2.h>
int tempoAngle = 10;
int tempoHauteur = 15;
int tempoBase = 15;
int tempoOuverture = 1000;
int tempoFermeture = 500;

void setup() {
  // Serial
  Serial.begin(9600);
  while (!Serial);

  // ------- Interruption timer -------
  MsTimer2::set(1, tocante);  // 1ms period
  MsTimer2::start();
}

void loop() {
 
}


// ------- Interruption timer -------
void tocante() {// cette fonction permet de supprimer tous les delays, elle est appellée toutes les milli secondes
// on a des tempos pour chaque delay différents des qu'un moteur n'a plus le droit de bouger car il dois attendre 15ms 
//alors on diminue le compteur et des que le comteur est arrivé a 0 alors le compteur est remis au début.

// timer du moteur angle / moteur de gauche
  if (tempoAngle != 0 {
    tempoAngle--;
  } else  {
    tempoAngle = 10;
  }
  // timer du moteur de la base / axe z
  if (tempoBase != 0  {
    tempoBase--;
  } else {
    tempoBase = 15;
  }
  
  // timer du moteur hauteur / moteur de droite
  if (tempoHauteur != 0) {
    tempoHauteur--;
  } else{
    tempoHauteur = 15;
  }
}
