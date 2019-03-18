unsigned long DELAY_TIME = 1500; // 1.5 sec
unsigned long delayStart = 0; // the time the delay started
bool delayRunning = false; // true if still waiting for delay to finish
bool ledOn = 0;

void setup() {
  
  Serial.begin(9600);

  // start delay
  delayStart = millis();
  delayRunning = true;
}

void loop() {
  // check if delay has timed out
  if (delayRunning && ((millis() - delayStart) >= DELAY_TIME)) {
    delayStart += DELAY_TIME; // this prevents drift in the delays
    // toggle the led
    ledOn = !ledOn;
    if (ledOn) {
      Serial.println("on");
    } else {
      Serial.println("off");
    }
  }
}
