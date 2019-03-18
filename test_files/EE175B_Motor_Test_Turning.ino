#include <MotorDriver.h>


MotorDriver m;
const int frontLeft = 4;
const int frontRight = 3;
const int backRight = 2;
const int backLeft = 1;
const int sensor = 21;
int rev = 0;
void countRev(){
  rev = rev + 1;
}
void setup()
{
 Serial.begin(9600);
 attachInterrupt(digitalPinToInterrupt(sensor),countRev,CHANGE);
}


void loop()
{
  delay(3000);
  m.motor(frontLeft,BACKWARD,255);
  m.motor(backLeft,BACKWARD,255);
  m.motor(frontRight,BACKWARD,150);
  m.motor(backRight,BACKWARD,150);
  delay(2000);
  m.motor(frontLeft,RELEASE,0);
  m.motor(backLeft,RELEASE,0);
  m.motor(frontRight,RELEASE,0);
  m.motor(backRight,RELEASE,0);
  delay(500);
  m.motor(frontLeft,BACKWARD,150);
  m.motor(backLeft,BACKWARD,150);
  m.motor(frontRight,BACKWARD,255);
  m.motor(backRight,BACKWARD,255);
  delay(2000);
  m.motor(frontLeft,RELEASE,0);
  m.motor(backLeft,RELEASE,0);
  m.motor(frontRight,RELEASE,0);
  m.motor(backRight,RELEASE,0);
  delay(500);
  Serial.println(rev);
  
 

}
