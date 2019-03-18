#include <MotorDriver.h>

MotorDriver m;
// defines pins numbers
const int trigPin0 = 48; // front sensor
const int trigPin1 = 49; // back sensor
const int echoPin0 = 50;
const int echoPin1 = 53;
// Important constants for the parking algorithm
const int frontLeft = 4;
const int frontRight = 3;
const int backRight = 2;
const int backLeft = 1;
const int openSpace = 30; // No car is parked(value can be adjusted depending on testing zone)
// defines variables for distance detection
long duration0; // extremly high values if the distance is far
long duration1; // same as duration0
int frontSensorVal; // distance will be between 0-4000 so it doesn't need to be a long
int backSensorVal; // same as front sensor
/////////////////////////////////////////////////////////////////////////////////////////////////

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
Serial.begin(9600); // Starts the serial communication
}
void loop() {
  if(searchFlag == 0 && parkFlag == 0){
    m.motor(4,FORWARD,255);
    m.motor(3,FORWARD,255);
    m.motor(2,FORWARD,255);
    m.motor(1,FORWARD,255);
    duration0 = trigRead(trigPin0,echoPin0); // utilizes function to recieve four distinct values for each ultrasonic sensor
    // Calculating the distance
    frontSensorVal= duration0*0.034/2; // uses a formula for speed of sound and temperature to acquire distance in centimeters
    Serial.print("Distance for Front Sensor Step1: ");
    Serial.println(frontSensorVal);
  }
  if(frontSensorVal <= openSpace && searchFlag == 0 && parkFlag == 0){ // This means the sensor detected a car and we know the distance from that car
    distCar1 = frontSensorVal;
    searchFlag = 1;
    duration1 = trigRead(trigPin1,echoPin1);
    backSensorVal = duration1*0.034/2; // uses a formula for speed of sound and temperature to acquire distance in centimeters
    while(backSensorVal >= distCar1+2){ // The 2 adds as an additional buffer in case car moves slighlty
      duration1 = trigRead(trigPin1,echoPin1);
      backSensorVal = duration1*0.034/2; // uses a formula for speed of sound and temperature to acquire distance in centimeters
      Serial.print("Distance for Back Sensor Step1: ");
      Serial.println(backSensorVal);
    }
    while(backSensorVal<= distCar1+2){
      duration1 = trigRead(trigPin1,echoPin1);
      backSensorVal = duration1*0.034/2; // uses a formula for speed of sound and temperature to acquire distance in centimeters
      Serial.print("Distance for Back Sensor Step2: ");
      Serial.println(backSensorVal);
      }
  }
  if(searchFlag == 1){ // this means its searching for an open spot
    delay(500);
     duration0 = trigRead(trigPin0,echoPin0);
     frontSensorVal= duration0*0.034/2;
     Serial.print("Distance for Front Sensor Step2: ");
     Serial.println(frontSensorVal);
    if(frontSensorVal >= distCar1 && parkFlag == 0){ //front sensor did not detect a car
      Serial.println("Parking Space Found! Beginning Parking Procedure");
      searchFlag = 0;
      parkFlag = 1;
      m.motor(4,RELEASE,0);
      m.motor(3,RELEASE,0);
      m.motor(2,RELEASE,0);
      m.motor(1,RELEASE,0);
    }
    else{
      searchFlag = 0;
      frontSensorVal = 0;
      backSensorVal = 0;
      distCar1 = 0;
      
    }
  }
  if(parkFlag == 1){
    delay(1000);
    Serial.println("Parking in Progress");
  }
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
