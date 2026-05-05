## Software Architecture
The software for this turret is split into two main parts: a Python script that handles the computer vision, and an Arduino C++ sketch that handles the motor control. They communicate in real-time over a local network bridge.

## Python: Computer Vision & Target Tracking 
The Python script uses the `arduino.app_bricks` library to run a live video feed and perform object detection.

### Detection: 
The script constantly scans the video frame for a person with a minimum confidence threshold of 50%.

### Coordinate Math: 
When a person is detected, it grabs their bounding box `[x_min, y_min, x_max, y_max]` and calculates the exact horizontal center (`center_x`) of the target.

### Communication: 
It uses `Bridge.call()` to send that `center_x` pixel coordinate down to the MCU. It also pushes detection stats to a local WebUI for monitoring.

### Scan Mode: 
If nobody is in the frame, the script automatically sends a target value of 0 to tell the microcontroller to start searching.

## C++ Arduino: Hardware Control & Logic 
The Arduino sketch receives the target coordinates from Python and drives a 35kg continuous rotation servo to aim the turret.