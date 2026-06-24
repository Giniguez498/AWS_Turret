
# Automated Weapon Station


# Python Script: This script allows for object detection and tracking.


# Gabriel Iniguez

import cv2 # Computer vision library that handles the framing and AI.
import time # Allows for delays.
import mmap # Memory map: Allows python to talk to physical hardware memory.
import os # Operating system tool: Allows for opening of Linux files.
import struct # Converts standard python numbers into binary data for the FPGA.
import smbus2 # Library for the I2C protocol to read from the distanc sensor.


# HARDWARE CONFIGURATION AND CONSTANTS

#----Camera setup----
FRAME_WIDTH = 1280
FRAME_HEIGHT = 800
CENTER_X = 640 # Center of screen (left/right).
CENTER_Y = 400 # Center of the screen (up/down).
TARGET_DEADZONE = 30 # 30-pixel "grace area" so servos do not jitter.

#----FPGA AXI Bridge setup (Servos)----
AXI_MASTER_BASE = 0xFF200000 # Address in the Aglix 5 where the SystemVerilog servos live.
PAN_SERVO_OFFSET = 0x00 # Panning servo is at the base address.
TILT_SERVO_OFFSET = 0x04 # Tilting servo is 4 bytes away.

#Servo timings (500us - 2500us)
PWM_MIN = 500
PWM_MAX = 2500
#Variables to hold the current direction (start them off in the neutral zone).
pan_pwm = 1500
tilt_pwm = 1500

#----I2C Modulino setup----
I2C_BUS = 0; # Agilex 5 hardware I2C bus number.
MODULINO_ADDRESS = 0x29 # Default hardware I2C address.
bus = smbus2.SMBus(I2C_BUS) # Turn on the I2C bus.


# HARDWARE HELPER FUNCTIONS

def write_fpga_register(offset, value):
   """This function bridges the Python software to SystemVerilog hardware.
   It takes a microsecond value (1500) and puts it directly into the FPGA
   memory."""

   try:
      # Open /dev/mem
      f = os.open("dev/mem", os.O_RDWR | os.O_SYNC)
      # Map a chunck of memory starting at the AXI base address.
      mem = mmap.mmap(f, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=AXI_MASTER_BASE)
      # Pack our value into an unsigned 32-bit integer and write it to the FPGA.\
      mem[offset:offset+4] = struct.pack("<L", value)

      #close the memory map
      mem.close()
      os.close(f)
   except Exception as e:
      print(f"FPGA Memory Error: {e}")

def read_distance():
   """Reads the VL53L4CD modulino via I2C"""
   #Returns the sensor distance
   dummy_distance = 850 # Distance of object (mm)
   return dummy_distance

def fire_weapon():
   """Trigger the GPIO Pin to shoot"""
   print(">>> Engaging Target! <<<")
   #Later code will be added here to trigger the firing mechanism.
   time.sleep(0.1)


   # MAIN METHOD FOR VISION & CONTROL LOOP

def main():
   global pan_pwm, tilt_pwm

   print("Initializing Camera...")

   # Connect to the camera (0 means to grab first camera plugged into board)
   cap = cv2.VideoCapture(0)

   # Force to use specified resolution
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

   # Check if camera turned on
   if not cap.isOpened():
      print("Error: Could not start camera.")
      return
   
   print("Turret Armed. Press q  in the video windown to quit.")

   while True:

      # 1. Grab frame: Takes a single pictue from the live video feed.
      ret, frame = cap.read()
      if not ret:
         continue # If frame fails, skip this loop and try again.

      # 2. Vision Processing 

      if len(frame.shape) == 3:
         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      else:
         gray = frame

         #Binary thresholding
         _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

         #Look at high contrast amsk and draw outlines (contours) around the white blobs.
         contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

         #Default states
         target_locked = False
         dist_mm = 9999

      if contours:
         # Pick the single biggest bright blob (flashlight)
         largest_contour = max(contours, key=cv2.contourArea)

            # Only track if it is a decent size (Area > 500 pixels)
         if cv2.contourArea(largest_contour) > 500:
            # Draws an invisible bounding box around the blob
            x, y, w, h = cv2.boundingRect(largest_contour)

            # Calculate the center of the bounding box
            target_x = x + (w // 2)
            target_y = y + (h // 2)

            # Draws a visible green rectangle and red dot on the live feed
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 2)
            cv2.circle(frame, (target_x, target_y), 5, (255, 255, 255), -1)

            target_locked = True

      
         # 3. ACTUATION LOGIC (MOVING SERVOS)
      if target_locked:

         error_pan = target_x - CENTER_X
         error_tilt = target_y - CENTER_Y

         # If target is outside the 20-pixel deadzone, Move the servo
         if abs(error_pan) > TARGET_DEADZONE:
         
         # Multiply the error by 0.1 to calculate a small step.
         # Add the step to current servo position
            pan_pwm += int( error_pan * 0.1)

         #Prevent the math from having the servo go beyond their limits
            pan_pwm = max(PWM_MIN, min(PWM_MAX, pan_pwm))

         #Send the new position the the FPGA
         write_fpga_register(PAN_SERVO_OFFSET, pan_pwm)

         if abs(error_tilt) > TARGET_DEADZONE:
            tilt_pwm += int(error_tilt * 0.1)
            tilt_pwm = max(PWM_MIN, min(PWM_MAX, tilt_pwm))
            write_fpga_register(TILT_SERVO_OFFSET, tilt_pwm)

         
         # 4. RANGING & FIRING LOGIC
         if abs(error_pan) <= TARGET_DEADZONE and abs(error_tilt) <= TARGET_DEADZONE:
            dist_mm = read_distance()
            cv2.putText(frame, f"LOCKED - Dist: {dist_mm}mm", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            if dist_mm < 1000:
               fire_weapon()
            
            # Show the processed image in a new window
      cv2.imshow("Turret Vision Pipline", frame)

      if cv2.waitKey(1) & 0xFF == ord('q'):
         break

         # 5. CLEANUP
   cap.release()
   cv2.destroyAllWindows()

   # Set the servos back to neutral position
   write_fpga_register(PAN_SERVO_OFFSET, 1500)
   write_fpga_register(TILT_SERVO_OFFSET, 1500)

if __name__ == "__main__":
            main()







   