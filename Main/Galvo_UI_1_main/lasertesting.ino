// // STM32F411CEU6 Black Pill - Dynamic Galvo UI Power & Gating Control

// // Galvo Inputs
// const int PIN_ANALOG_IN = PA0; // Galvo Pin 35 (0-3.3V after divider)
// const int PIN_PWM_IN    = PA8; // Galvo Pin 33 (Laser On/Off / Gating signal)

// // Laser DB25 Outputs
// const int DATA_PINS[8] = {PB0, PB1, PB2, PB3, PB4, PB5, PB6, PB7}; // D0 to D7
// const int PIN_LATCH   = PB8; // DB25 Pin 9 (Latch)
// const int PIN_BOOSTER = PB9; // DB25 Pin 19 (Booster Output)

// // Hysteresis tracking to prevent power bus jitter
// uint8_t currentPowerByte = 255; 

// void setLaserPowerByte(uint8_t powerByte) {
//   // 1. Output the 8-bit value across PB0-PB7
//   for (int i = 0; i < 8; i++) {
//     bool bitVal = (powerByte >> i) & 0x01;
//     digitalWrite(DATA_PINS[i], bitVal ? HIGH : LOW);
//   }

//   // 2. Pulse Pin 9 (Latch) HIGH to update the internal power register
//   digitalWrite(PIN_LATCH, HIGH);
//   delayMicroseconds(5); 
//   digitalWrite(PIN_LATCH, LOW);
// }

// void setup() {
//   // Initialize Input Pins
//   pinMode(PIN_ANALOG_IN, INPUT_ANALOG);
//   pinMode(PIN_PWM_IN, INPUT);

//   // Initialize Output Pins
//   for (int i = 0; i < 8; i++) {
//     pinMode(DATA_PINS[i], OUTPUT);
//     digitalWrite(DATA_PINS[i], LOW);
//   }
//   pinMode(PIN_LATCH, OUTPUT);
//   pinMode(PIN_BOOSTER, OUTPUT);
  
//   digitalWrite(PIN_LATCH, LOW);
//   digitalWrite(PIN_BOOSTER, LOW);

//   // Initial startup delay for hardwired Pin 18 (MO) seed laser stabilization
//   delay(500);

//  // 1. Read raw ADC (0V -> 0, 3.27V -> ~4058)
//   int rawADC = analogRead(PIN_ANALOG_IN); 

// // 2. Map 0 to 4058 across the full 0 to 255 power byte range
//   int calculatedPower = map(rawADC, 0, 4058, 0, 255);

// // 3. Clamp output to safe 8-bit limits
//   uint8_t targetPowerByte = constrain(calculatedPower, 0, 255);

// }

// void loop() {
//   // 1. Dynamic Power Control from UI (Galvo Pin 35 -> PA0)
//   int rawADC = analogRead(PIN_ANALOG_IN); // 12-bit ADC (0 to 4095)
//   uint8_t targetPowerByte = map(rawADC, 0, 4095, 0, 255);

//   // Update DB25 power bus only when the UI slider changes
//   if (abs((int)targetPowerByte - (int)currentPowerByte) >= 2) {
//     currentPowerByte = targetPowerByte;
//     setLaserPowerByte(currentPowerByte);
//   }

//   // 2. Real-Time Firing Control from UI (Galvo Pin 33 -> PA8 -> PB9)
//   // When UI fires the laser pulse/mark command, drive Booster HIGH
//   bool isFiring = digitalRead(PIN_PWM_IN);
//   digitalWrite(PIN_BOOSTER, isFiring ? HIGH : LOW);
// }


// STM32F411CEU6 Black Pill - Dynamic Galvo UI Power & Gating Control (With Auto-Off Safety)

// STM32F411CEU6 Black Pill - Analog Power & Booster Control
// (Galvo Pin 33 PWM is connected directly to DB25 Pin 20 PRR)

// Galvo Input
// const int PIN_ANALOG_IN = PA0; // Galvo Pin 35 (0-3.27V after divider)

// // Laser DB25 Outputs
// const int DATA_PINS[8] = {PB0, PB1, PB2, PB3, PB4, PB5, PB6, PB7}; // D0 to D7 (Pins 1-8)
// const int PIN_LATCH   = PB8; // DB25 Pin 9 (Latch)
// const int PIN_BOOSTER = PB9; // DB25 Pin 19 (Booster Output)

// // Threshold below which Analog is considered 0V / UI Disconnected (~0.04V)
// const int ADC_OFF_THRESHOLD = 50; 

// uint8_t currentPowerByte = 0; 

// // Writes 8-bit byte to PB0-PB7 and pulses Latch (PB8)
// void setLaserPowerByte(uint8_t powerByte) {
//   for (int i = 0; i < 8; i++) {
//     bool bitVal = (powerByte >> i) & 0x01;
//     digitalWrite(DATA_PINS[i], bitVal ? HIGH : LOW);
//   }

//   digitalWrite(PIN_LATCH, HIGH);
//   delayMicroseconds(5); 
//   digitalWrite(PIN_LATCH, LOW);
// }

// // Immediately kills high-power output and zeroes out power register
// void turnLaserOff() {
//   digitalWrite(PIN_BOOSTER, LOW); // Kill Booster output
//   if (currentPowerByte != 0) {
//     currentPowerByte = 0;
//     setLaserPowerByte(0);         // Set laser power byte to 00h
//   }
// }

// void setup() {
//   // Initialize Analog Input Pin
//   pinMode(PIN_ANALOG_IN, INPUT_ANALOG);

//   // Initialize Output Pins
//   for (int i = 0; i < 8; i++) {
//     pinMode(DATA_PINS[i], OUTPUT);
//     digitalWrite(DATA_PINS[i], LOW);
//   }
//   pinMode(PIN_LATCH, OUTPUT);
//   pinMode(PIN_BOOSTER, OUTPUT);
  
//   digitalWrite(PIN_LATCH, LOW);
//   digitalWrite(PIN_BOOSTER, LOW);

//   // Initial startup delay for hardwired Pin 18 (MO) seed laser stabilization
//   delay(500);

//   // Force laser completely OFF at boot until UI provides active voltage
//   turnLaserOff();
// }

// void loop() {
//   int rawADC = analogRead(PIN_ANALOG_IN);

//   // SAFETY CHECK: If Analog signal is OFF or Disconnected (< 0.04V / 0% Power)
//   if (rawADC < ADC_OFF_THRESHOLD) {
//     turnLaserOff();
//     return; // Exit loop early
//   }

//   // --- UI IS CONNECTED & SENDING POWER ---

//   // 1. Map raw ADC (0-3.27V -> 0-4058) to 8-bit power byte (0-255)
//   int calculatedPower = map(rawADC, ADC_OFF_THRESHOLD, 4058, 0, 255);
//   uint8_t targetPowerByte = constrain(calculatedPower, 0, 255);

//   // 2. Update DB25 power bus only when the UI power slider changes
//   if (abs((int)targetPowerByte - (int)currentPowerByte) >= 2) {
//     currentPowerByte = targetPowerByte;
//     setLaserPowerByte(currentPowerByte);
//   }

//   // 3. Keep Booster ON while valid analog power is present 
//   digitalWrite(PIN_BOOSTER, HIGH);
// }

// STM32F411CEU6 Black Pill - Galvo D0 Sequential Firing & Power Control

// Galvo Inputs
// const int PIN_ANALOG_IN   = PA0;  // Galvo Pin 35 (0-3.27V Power reference)
// const int PIN_GALVO_D0_IN = PA1; // Galvo D0 Pin 19 (5V-Tolerant Trigger Input)
 

// // Laser DB25 Outputs
// const int DATA_PINS[8] = {PB0, PB1, PB2, PB3, PB4, PB5, PB6, PB7}; // DB25 Pins 1-8 (D0-D7)
// const int PIN_LATCH    = PB8;  // DB25 Pin 9 (Latch)
// const int PIN_MO       = PA2; // DB25 Pin 18 (Master Oscillator / MO)
// const int PIN_BOOSTER  = PB9;  // DB25 Pin 19 (Booster / Emission)

// const int ADC_OFF_THRESHOLD = 50; 
// uint8_t currentPowerByte = 0;
// bool laserIsFiring = false;

// // Write 8-bit power data and pulse Latch (PB8)
// void setLaserPowerByte(uint8_t powerByte) {
//   for (int i = 0; i < 8; i++) {
//     bool bitVal = (powerByte >> i) & 0x01;
//     digitalWrite(DATA_PINS[i], bitVal ? HIGH : LOW);
//   }
//   digitalWrite(PIN_LATCH, HIGH);
//   delayMicroseconds(5);
//   digitalWrite(PIN_LATCH, LOW);
// }

// // Immediate Shutdown Sequence
// void turnLaserOff() {
//   digitalWrite(PIN_BOOSTER, LOW); // 1. Cut Booster high-power emission first
//   delayMicroseconds(20);
//   digitalWrite(PIN_MO, LOW);      // 2. Shut off Master Oscillator seed
//   laserIsFiring = false;
// }

// void setup() {
//   // Inputs
//   pinMode(PIN_ANALOG_IN, INPUT_ANALOG);
//   pinMode(PIN_GALVO_D0_IN, INPUT);

//   // Outputs
//   for (int i = 0; i < 8; i++) {
//     pinMode(DATA_PINS[i], OUTPUT);
//     digitalWrite(DATA_PINS[i], LOW);
//   }
//   pinMode(PIN_LATCH, OUTPUT);
//   pinMode(PIN_MO, OUTPUT);
//   pinMode(PIN_BOOSTER, OUTPUT);

//   digitalWrite(PIN_LATCH, LOW);
//   digitalWrite(PIN_MO, LOW);
//   digitalWrite(PIN_BOOSTER, LOW);

//   turnLaserOff();
// }

// void loop() {
//   // --- 1. Dynamic Power Control ---
//   int rawADC = analogRead(PIN_ANALOG_IN);

//   if (rawADC >= ADC_OFF_THRESHOLD) {
//     int calculatedPower = map(rawADC, ADC_OFF_THRESHOLD, 4058, 0, 255);
//     uint8_t targetPowerByte = constrain(calculatedPower, 0, 255);

//     if (abs((int)targetPowerByte - (int)currentPowerByte) >= 2) {
//       currentPowerByte = targetPowerByte;
//       setLaserPowerByte(currentPowerByte);
//     }
//   }

//   // --- 2. Sequential Laser Firing Logic ---
//   bool galvoTrigger = digitalRead(PIN_GALVO_D0_IN);

//   if (galvoTrigger && (rawADC >= ADC_OFF_THRESHOLD)) {
//     if (!laserIsFiring) {
//       // Step 1: Turn ON Master Oscillator (PA2 -> DB25 Pin 18)
//       digitalWrite(PIN_MO, HIGH);

//       // Step 2: Stabilization delay (100 microseconds)
//       delayMicroseconds(100);

//       // Step 3: Turn ON Booster (PB9 -> DB25 Pin 19)
//       digitalWrite(PIN_BOOSTER, HIGH);
      

//       laserIsFiring = true;
//     }
//   } else {
//     // If Galvo D0 drops LOW or UI power is 0V, shut off immediately
//     if (laserIsFiring) {
//       turnLaserOff();
//     }
//   }
// }

// STM32F411CEU6 Black Pill - Laser Power, Main Firing, & Red Dot Control

// Galvo Inputs
const int PIN_ANALOG_IN   = PA0;  // Galvo Pin 35 (0-3.27V Power Reference)
const int PIN_GALVO_D0_IN = PA1; // Galvo D0 Pin 19 (Main Laser Trigger - 5V Tolerant)
const int PIN_GALVO_D2_IN = PA3;  // Galvo D2 Pin 20 (Red Dot Trigger - 3.3V Max!)

// Laser DB25 & Red Dot Outputs
const int DATA_PINS[8]    = {PB0, PB1, PB2, PB3, PB4, PB5, PB6, PB7}; // DB25 Pins 1-8 (D0-D7)
const int PIN_LATCH       = PB8;  // DB25 Pin 9 (Latch)
const int PIN_MO          = PA2; // DB25 Pin 18 (Master Oscillator / MO)
const int PIN_BOOSTER     = PB9;  // DB25 Pin 19 (Booster / Emission)
const int PIN_RED_DOT_OUT = PA4;  // Red Dot Laser Control Pin

const int ADC_OFF_THRESHOLD = 50; 
uint8_t currentPowerByte = 0;
bool laserIsFiring = false;

// Write 8-bit power data and pulse Latch (PB8)
void setLaserPowerByte(uint8_t powerByte) {
  for (int i = 0; i < 8; i++) {
    bool bitVal = (powerByte >> i) & 0x01;
    digitalWrite(DATA_PINS[i], bitVal ? HIGH : LOW);
  }
  digitalWrite(PIN_LATCH, HIGH);
  delayMicroseconds(5);
  digitalWrite(PIN_LATCH, LOW);
}

// Immediate Main Laser Shutdown Sequence
void turnLaserOff() {
  digitalWrite(PIN_BOOSTER, LOW); // 1. Cut high-power booster emission first
  delayMicroseconds(20);
  digitalWrite(PIN_MO, LOW);      // 2. Shut off Master Oscillator seed
  laserIsFiring = false;
}

void setup() {
  // Inputs
  pinMode(PIN_ANALOG_IN, INPUT_ANALOG);
  pinMode(PIN_GALVO_D0_IN, INPUT_PULLDOWN);
  pinMode(PIN_GALVO_D2_IN, INPUT_PULLDOWN);

  // Laser Outputs
  for (int i = 0; i < 8; i++) {
    pinMode(DATA_PINS[i], OUTPUT);
    digitalWrite(DATA_PINS[i], LOW);
  }
  pinMode(PIN_LATCH, OUTPUT);
  pinMode(PIN_MO, OUTPUT);
  pinMode(PIN_BOOSTER, OUTPUT);

  // Red Dot Output
  pinMode(PIN_RED_DOT_OUT, OUTPUT);

  // Initial States
  digitalWrite(PIN_LATCH, LOW);
  digitalWrite(PIN_MO, LOW);
  digitalWrite(PIN_BOOSTER, LOW);
  digitalWrite(PIN_RED_DOT_OUT, LOW);

  turnLaserOff();
}

void loop() {
  // --- 1. Red Dot Laser Control (Galvo D2 -> PA3 -> PA4) ---
  bool redDotTrigger = digitalRead(PIN_GALVO_D2_IN);
  digitalWrite(PIN_RED_DOT_OUT, redDotTrigger ? HIGH : LOW);

  // --- 2. Dynamic Power Control ---
  int rawADC = analogRead(PIN_ANALOG_IN);

  if (rawADC >= ADC_OFF_THRESHOLD) {
    int calculatedPower = map(rawADC, ADC_OFF_THRESHOLD, 4058, 0, 255);
    uint8_t targetPowerByte = constrain(calculatedPower, 0, 255);

    if (abs((int)targetPowerByte - (int)currentPowerByte) >= 2) {
      currentPowerByte = targetPowerByte;
      setLaserPowerByte(currentPowerByte);
    }
  }

  // --- 3. Main Laser Sequential Firing Logic ---
  bool galvoMainTrigger = digitalRead(PIN_GALVO_D0_IN);

  if (galvoMainTrigger && (rawADC >= ADC_OFF_THRESHOLD)) {
    if (!laserIsFiring) {
      digitalWrite(PIN_MO, HIGH);     // Step 1: MO ON
      delayMicroseconds(100);         // Step 2: Stabilization delay
      digitalWrite(PIN_BOOSTER, HIGH); // Step 3: Booster ON
      laserIsFiring = true;
    }
  } else {
    if (laserIsFiring) {
      turnLaserOff();
    }
  }
}