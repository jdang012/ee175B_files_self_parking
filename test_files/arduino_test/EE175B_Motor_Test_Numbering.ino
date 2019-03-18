#include <MotorDriver.h>

MotorDriver m;
int count = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  m.motor(1,FORWARD,255);
  while(count <= 20){
    if(digitalRead(sensor)){
      count = count + 1;
      while(digitalRead(sensor));
    }
  }
  m.motor(1,RELEASE,0);
  Serial.print("one revolution was made: shut down motors");
  

}
