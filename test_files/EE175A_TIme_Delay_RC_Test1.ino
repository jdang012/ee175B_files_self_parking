unsigned long DELAY_TIME = 3000; // 3 sec to test time delay for RC car(will use velocity later on)
unsigned long delayStart = 0; // the time the delay started
const int trigPin = 6;
const int echoPin = 2;
//const int motor1 = 3; this is for future purposes
//const int motor2 = 4;
const int carLength = 30; // RC is 30cm long? will change value later
unsigned long cycle = 0; // used to measure time
long duration;
int distance;
void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);
}

void loop() {
digitalWrite(trigPin,LOW);
delayMicroseconds(5);
digitalWrite(trigPin,HIGH);
delayMicroseconds(15);
digitalWrite(trigPin, LOW);
duration = pulseIn(echoPin,HIGH);
distance = duration*.034/2; // calculating distance with speed of sound and temperature 
if(distance >= carLength){
  ++cycle;
  delayStart = 20*cycle;
  if((delayStart >= DELAY_TIME)) // if start is greater then the delay the space is free
  {
    //digitalWrite(motor1, LOW); motors should turn off
    //digitalWrite(motor2, LOW);
    Serial.println("Space is free"); // space is free but this is a basic version of code
    //delay(1000); possible delay for the motors
    cycle = 0; // resets the cycle just to show functionality
    delayStart = 0; // same as cycle
  }
}
else{
  delayStart = 0;
  cycle = 0;
}
}
