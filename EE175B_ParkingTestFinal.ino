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
char dir;
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
void slightRight(){
    m.motor(4,FORWARD,255);
    m.motor(3,FORWARD,240);
    m.motor(2,FORWARD,240);
    m.motor(1,FORWARD,255);
}
void slightLeft(){
    m.motor(4,FORWARD,240);
    m.motor(3,FORWARD,255);
    m.motor(2,FORWARD,255);
    m.motor(1,FORWARD,240);
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
  if(count == 0){ //In this state the Pi is controlling the motor speeds through input commands
  while(!Serial.available()); // waiting for Pi command
    dir = Serial.read(); // read the command direction
    if (dir =='R'){ // Turn the car to the right to straighten out
      slightRight();
      count = 0;
    }
    else if (dir =='L'){ // Turn the car to the left to straighten out
          slightLeft();
          count = 0;
      }
      else if (dir =='S'){ // The car is now straight so we continue to the next state
          count = 1;
          breakMotors();
          delay(1000);
          
          
      }
  }
  if(count == 1){
    count = 2;
    motorsOn();
    duration0 = trigRead(trigPin0,echoPin0);
    duration1 = trigRead(trigPin1,echoPin1);
    
  }
  if(count == 2){ // In this state the first sensor must find a car before beginning to look for parking due to testing limitations
      duration0 = trigRead(trigPin0,echoPin0);
      frontSensorVal = duration0 * .034/2; // Read distance value for front Sensor
//      Serial.print("Distance for Front Sensor Step1: ");
//      Serial.println(frontSensorVal);
     if(frontSensorVal >= openSpace){ // If front sensor sees open space keep taking sensor value polls
        count = 2;
      }
      else{
//        Serial.println("Loop 1 finished");
        count = 3; // If a car is detected move to the next state
      }
  }
  if(count == 3){ // In this state the back sensor must read the same car the first sensor read
      duration1 = trigRead(trigPin1,echoPin1);
      backSensorVal = duration1 * .034/2; // Reads back sensor value
//      Serial.print("Distance for Back Sensor Step2: ");
//      Serial.println(backSensorVal);
      if(backSensorVal >= openSpace){ // If back sensor sees open space keep taking sensor value polls
        count = 3;
    }
    else{
      delay(100);
      Serial.println (100); //act as parking flag, must be more than 20
//      Serial.println("Loop 2 finished");
      count = 4; // If the car is detected move to the next state
    }
  }
  if(count == 4){ // In this state the back sensor must pass the car in order to determine if there is enough space
      duration1 = trigRead(trigPin1,echoPin1);
      backSensorVal = duration1 * .034/2;
//      Serial.print("Distance for Back Sensor Step3: ");
//      Serial.println(backSensorVal);  
    if(backSensorVal <= openSpace){
      count = 4; // Stay in this state if first car is still spotted
    }
    else{
 //     Serial.println("Loop 3 finished");
      holes = 0; // start tracking distance which gives the size of the parking spot
      count = 5; // Move to the next state
    }
  }
  if(count == 5) // In this state we see if the front sensor value is open or if it detects a car
  {
      duration0 = trigRead(trigPin0,echoPin0);
      frontSensorVal = duration0 * .034/2;
//      Serial.print("Distance for Front Sensor Step4: ");
//      Serial.println(frontSensorVal);
    if(frontSensorVal >= openSpace){ // if open space then the car length fits but needs more room
//      Serial.println("Car fits must check for extra distance");
      count = 6;
//      Serial.println("Loop 4 finished");
    }
    else{
      count = 2; // Car didn't fit look for another parking spot
      frontSensorVal = 100; // reset the sensor value
      backSensorVal = 100; // reset the sensor value
    }
  }
  if(count == 6){ // In this state we see if another car will get in the way of the parking algorithm over a set distance
      duration0 = trigRead(trigPin0,echoPin0);
      frontSensorVal = duration0 * .034/2;  
//      Serial.print("Distance for Front Sensor Step5: ");
//      Serial.println(frontSensorVal);  
//      Serial.println(holes);
//      Serial.println(spaceFlag);
      if(frontSensorVal <= openSpace){ // If a car is detected before enough space is found we cannot park
        spaceFlag = 1; // sets the flag 
      }
    if(spaceFlag == 1){ // this will reset the values of all sensors and start looking for another space
      count = 2;
      frontSensorVal = 100;
      backSensorVal = 100;
      spaceFlag = 0;
    }
    else if(spaceFlag == 0 && holes <= 50){ // if the car has not moved two and a half revolutions then keep polling values
      count = 6;
    }
    else{ // Enough space was found move to the next state
      delay(100);
//      Serial.print("Total revolutions for car space is ");
//      Serial.println(rev);
//      Serial.println("Loop 5 finished");
      count = 7;
    }
  }
  if(count == 7){
    if(holes<120){
      count = 7;
    }
    else{
      count = 8;
      breakMotors();
      delay(1000);
      rev = holes;
      holes = 0;
    }
  }
  if(count == 8){  //parking algorithm starts in this state
      motorsBack();
  while(holes <(rev/4)){ // go back 1/4th the distance of the spot
    Serial.println(holes);
  }
  breakMotors();
  delay(500);
  holes = 0;
  turnLeft();
  while(holes<50){ // this value is equal to a 60 degree turn
    Serial.println(holes);
  }
  breakMotors();
  delay(500);
  holes = 0;
  motorsBack();
  while(holes<95){ // the car moves back a little under 5 revolutions of the wheel
    Serial.println(holes);
  }
  breakMotors();
  delay(500);
  holes = 0;
  turnRight();
  while(holes<50){ // straightens car out in the parking spot
    Serial.println(holes);
  }
  breakMotors();
  delay(500);
  count = 9; // goes to the next state which doesn't exist so it ends the program
  }
}
