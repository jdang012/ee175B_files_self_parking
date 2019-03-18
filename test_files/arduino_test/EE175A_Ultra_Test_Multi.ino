// defines pins numbers
const int trigPin0 = 48;
const int trigPin1 = 49;
const int echoPin0 = 50;
const int echoPin1 = 53;
// defines variables
long duration0; // high values if the distance is far
long duration1;
int distance0; // distance will be between 0-4000 so it doesn't need to be a long
int distance1;
void setup() {
pinMode(52, OUTPUT);
pinMode(51,OUTPUT);
pinMode(46, OUTPUT);
pinMode(47,OUTPUT);
pinMode(trigPin0, OUTPUT); // Sets the trigPin as an Output
pinMode(trigPin1, OUTPUT); // Sets the trigPin as an Output
pinMode(echoPin0, INPUT); // Sets the echoPin as an Input
pinMode(echoPin1, INPUT); // Sets the echoPin as an InputInput
Serial.begin(9600); // Starts the serial communication
digitalWrite(46, LOW);
digitalWrite(47,HIGH);
digitalWrite(52, LOW);
digitalWrite(51,HIGH);
}
long trigRead(int trigPin,int echoPin){ // function created to do the ultrasonic testing without having to repeat it multiple times
  digitalWrite(trigPin, LOW); // sets up a clean signal for trigPin
  delayMicroseconds(5);
  // Sets the trigPin on HIGH state for 15 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(15);
  digitalWrite(trigPin, LOW); // returns the pin to low state
  return pulseIn(echoPin,HIGH); // produces the value recieved by echoPin
}
void loop() {
//duration0 = trigRead(trigPin0,echoPin0); // utilizes function to recieve four distinct values for each ultrasonic sensor
duration1 = trigRead(trigPin1,echoPin1);
// Calculating the distance
//distance0= duration0*0.034/2; // uses a formula for speed of sound and temperature to acquire distance in centimeters 
distance1= duration1*0.034/2;
// Prints the distance on the Serial Monitor for each ultrasonic sensor
Serial.print("Distance: ");
//Serial.print(distance0);
//Serial.print(", ");
Serial.println(distance1);
}
