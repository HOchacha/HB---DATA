#define USE_ARDUINO_INTERRUPTS true    // Set-up low-level interrupts for most acurate BPM math.
#include <PulseSensorPlayground.h>     // Includes the PulseSensorPlayground Library.   
#include <SoftwareSerial.h>
#define samplingSector 50
#define RX 10
#define TX 11

PulseSensorPlayground pulseSensor;  // Creates an instance of the PulseSensorPlayground object called "pulseSensor"
SoftwareSerial BTSerial(RX, TX);

//  Variables
const int PulseWire = 0;       // PulseSensor PURPLE WIRE connected to ANALOG PIN 0
const int LED13 = 13;          // The on-board Arduino LED, close to PIN 13.
int Threshold = 510;           // Determine which Signal to "count as a beat" and which to ignore.
short LocalThershold[samplingSector] ={};       
short loopTimes = 0;
short Signal;
String set = "\0";
int level =0;

void setup() {   
  
  Serial.begin(115200);          // For Serial Monitor
  BTSerial.begin(115200);
  Serial.setTimeout(100);
  // Configure the PulseSensor object, by assigning our variables to it. 
  pulseSensor.analogInput(PulseWire);   
  //pulseSensor.blinkOnPulse(LED13);       //auto-magically blink Arduino's LED with heartbeat.
  pulseSensor.setThreshold(Threshold);   

  // Double-check the "pulseSensor" object was created and "began" seeing a signal. 
  if (pulseSensor.begin()) {
      //Serial.println("PSSACTV");
  }
  
}



void loop() {
  if(level == 0)
  {
    if(Serial.read())
    {
      level = 1;
      //Serial.println("level 2 actv");
    }
  }
  else if (level == 1) 
  {
    int myBPM = pulseSensor.getBeatsPerMinute();
    if (pulseSensor.sawStartOfBeat()) 
    { 
          
          //Serial.println(myBPM);                       
    }
    //short D = analogRead(0);
    //Serial.print(" a ");
    //Serial.println(D);
    
    delay(10);
  }
  else
  {
    
  }
}

  
