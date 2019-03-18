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
const int sensor = 22;
const int openSpace = 20; // No car is parked(value can be adjusted depending on testing zone
// defines variables for distance detection
long duration0; // high values if the distance is far
long duration1;
int frontSensorVal = 100; // distance will be between 0-4000 so it doesn't need to be a long
int backSensorVal = 100;
int count = 0; // keeps track of the state the parking algorithm is in
int holes = 0; // revolutions of the car wheel tracked
int spaceFlag = 0;
double rev = 0;
/////////////////////////////////////////////////////////////////////////////////////////////////

void countHoles(){
  holes = holes+1;
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
void motorsOn(){
    m.motor(4,FORWARD,255);
    m.motor(3,FORWARD,255);
    m.motor(2,FORWARD,255);
    m.motor(1,FORWARD,255);
}
void breakMotors(){
      m.motor(4,RELEASE,0);
      m.motor(3,RELEASE,0);
      m.motor(2,RELEASE,0);
      m.motor(1,RELEASE,0);
}
void motorsBack(){
    m.motor(4,BACKWARD,255);
    m.motor(3,BACKWARD,255);
    m.motor(2,BACKWARD,255);
    m.motor(1,BACKWARD,255);
}
void turnLeft(){
    m.motor(4,BACKWARD,255);
    m.motor(3,FORWARD,255);
    m.motor(2,FORWARD,255);
    m.motor(1,BACKWARD,255);
}  
void turnRight(){
    m.motor(4,FORWARD,255);
    m.motor(3,BACKWARD,255);
    m.motor(2,BACKWARD,255);
    m.motor(1,FORWARD,255);
} 
void setup() {
pinMode(52, OUTPUT);
pinMode(51,OUTPUT);
pinMode(46, OUTPUT);
pinMode(47,OUTPUT);
pinMode(trigPin0, OUTPUT); // Sets the trigPin as an Output
pinMode(trigPin1, OUTPUT); // Sets the trigPin as an Output
pinMode(echoPin0, INPUT); // Sets the echoPin as an Input
pinMode(echoPin1, INPUT); // Sets the echoPin as an InputInput
pinMode(sensor,INPUT);
Serial.begin(9600); // Starts the serial communication
digitalWrite(46, LOW);
digitalWrite(47,HIGH);
digitalWrite(52, LOW);
digitalWrite(51,HIGH);
Serial.begin(9600); // Starts the serial communication
attachInterrupt(digitalPinToInterrupt(21),countHoles,CHANGE);
}
void loop() {
  if(count == 0){
    motorsOn();
    count = 1;
    duration0 = trigRead(trigPin0,echoPin0);
    duration1 = trigRead(trigPin1,echoPin1);
    
  }
  if(count == 1){
    while(frontSensorVal >= openSpace){
      duration0 = trigRead(trigPin0,echoPin0);
      frontSensorVal = duration0 * .034/2;
      Serial.print("Distance for Front Sensor Step1: ");
      Serial.println(frontSensorVal);
    }
    Serial.println("Loop 1 finished");
    count = 2;
  }
  if(count == 2){
    while(backSensorVal >= openSpace){
      duration1 = trigRead(trigPin1,echoPin1);
      backSensorVal = duration1 * .034/2;
      Serial.print("Distance for Back Sensor Step2: ");
      Serial.println(backSensorVal);
    }
    delay(100);
    Serial.println("Loop 2 finished");
    count = 3;
  }
  if(count == 3){
    while(backSensorVal <= openSpace){
      duration1 = trigRead(trigPin1,echoPin1);
      backSensorVal = duration1 * .034/2;
      Serial.print("Distance for Back Sensor Step3: ");
      Serial.println(backSensorVal);    
    }
    Serial.println("Loop 3 finished");
    holes = 0;
    count = 4;
  }
  if(count == 4)
  {
      duration0 = trigRead(trigPin0,echoPin0);
      frontSensorVal = duration0 * .034/2;
      Serial.print("Distance for Front Sensor Step4: ");
      Serial.println(frontSensorVal);
    if(frontSensorVal >= openSpace){
      Serial.println("Car fits must check for extra distance");
      count = 5;
    }
    else{
      count = 1;
      frontSensorVal = 100;
      backSensorVal = 100;
    }
    Serial.println("Loop 4 finished");
  }
  if(count == 5){
    while(holes <= 50 && spaceFlag == 0){
      duration0 = trigRead(trigPin0,echoPin0);
      frontSensorVal = duration0 * .034/2;  
      Serial.print("Distance for Front Sensor Step5: ");
      Serial.println(frontSensorVal);  
      Serial.println(holes);
      Serial.println(spaceFlag);
      if(frontSensorVal <= openSpace){
        spaceFlag = 1;
      }
    }
    if(spaceFlag == 1){
      count = 1;
      frontSensorVal = 100;
      backSensorVal = 100;
      spaceFlag = 0;
    }
    else{
      Serial.print("Total revolutions for car space is ");
      Serial.println(rev);
      Serial.println("Loop 5 finished");
      count = 6;
    }
  }
  if(count == 6){
    if(holes < 140){
      count = 6;
    }
    else{
      count = 7;
      rev = holes;
      holes = 0;
    }

  }
  if(count == 7){
      motorsBack();
  while(holes <(rev/2)-5){
    Serial.println(holes);
  }
  breakMotors();
  delay(500);
  holes = 0;
  turnLeft();
  while(holes<50){
    Serial.println(holes);
  }
  breakMotors();
  delay(500);
  holes = 0;
  motorsBack();
  while(holes<65){
    Serial.println(holes);
  }
  breakMotors();
  delay(500);
  holes = 0;
  turnRight();
  while(holes<60){
    Serial.println(holes);
  }
  breakMotors();
  delay(500);
  while(1);
  }
  
}
