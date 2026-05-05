#include <Servo.h>
#include <Arduino_RouterBridge.h>
#include <MsgPack.h>

//GLOBAL VARIABLES
Servo testServo; 
int servoPin = 9;
int target_x = 200; 

// THE SETTER FUNCTION
int setTarget(int x) {
  target_x = x;
  return 1; // Gives the RPC Bridge something to send back to Python
}

void setup() {
  testServo.attach(servoPin);
  Bridge.begin();
  
  //REGISTER THE FUNCTION
  Bridge.provide("setTarget", setTarget); 
  
  //Start Serial Monitor for debugging
  Monitor.begin(9600);
  delay(1000);
  Monitor.println("--- AUTONOMOUS TURRET ONLINE ---");
  
  //Initialize servo in the STOP position
  testServo.writeMicroseconds(1428); 
}

void loop() {
  int speedPulse = 1428; 
  int screenCenter = 200; // Center of camera feed
  
  //Calculate the distance from the center
  int error = target_x - screenCenter;

  // --- LOGIC GATE 1: SCANNING ---
  if (target_x == 0) {
    speedPulse = 1450; // Slow spin to search
    Monitor.print("STATUS: SCANNING | ");
  } 
  
  // --- LOGIC GATE 2: TRACKING ---
  else {
    //DEADZONE: If target is within 25 pixels of the center, STOP!
    if (abs(error) < 25) {
      speedPulse = 1428; 
      Monitor.print("STATUS: LOCKED   | ");
    }
    //Target is to the RIGHT (Positive error)
    else if (error > 25) {
      //Move right, speed scales with distance
      speedPulse = map(error, 26, 200, 1431, 1600);
      Monitor.print("STATUS: TRACK R  | ");
    }
    //Target is to the LEFT (Negative error)
    else if (error < -25) {
      //Move left, speed scales with distance
      speedPulse = map(error, -26, -200, 1427, 1250);
      Monitor.print("STATUS: TRACK L  | ");
    }
  }

  //SEND COMMAND TO MOTOR
  testServo.writeMicroseconds(speedPulse);

  //PRINT DIAGNOSTICS
  Monitor.print("TargetX: ");
  Monitor.print(target_x);
  Monitor.print(" | Error: ");
  Monitor.print(error);
  Monitor.print(" | Pulse: ");
  Monitor.println(speedPulse);

  delay(50); //50ms delay keeps the loop running smoothly at 20Hz
}