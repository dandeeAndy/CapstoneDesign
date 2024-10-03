const int relayPin = 3;

void setup() {
  // Set the relay pin as an output
  pinMode(relayPin, OUTPUT);
  // Start serial communication at 9600 baud rate
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read(); // Read the incoming byte
    if (command == '1') {
      digitalWrite(relayPin, HIGH); // Turn relay ON
    } else if (command == '0') {
      digitalWrite(relayPin, LOW); // Turn relay OFF
    }
  }
}