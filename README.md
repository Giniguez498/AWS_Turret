# Autonomous 3D-Printed Tracking Turret

An autonomous, computer-vision tracking turret utilizing a "dual-brain"
architecture built on the Agilex 5 FPGA SoC DE-25 standard board. Sytem tracks
a specific target using a trained AI model and determines if target is within
the effective range before triggering the firing mechanism, bringing the target
down.

## Tech Stack
* **Software:** SystemVerilog (Hardware control), Python (Object Tracking)
* **Hardware:** DE-25 standard Agilex 5 FPGA Soc, 2X 35kg digital Servo, Arducam monochrome 120fps camera,
* Modulino distance ToF laser distance sensor
* **Design & Fab:** Fusion 360, Bambu Lab P1S 



## Architecture Pivot 
Originally the project was aimed to untilize the SBC Arduino Uno Q.
While the Arduino UNO Q is a SBC with a dual-brain architecture, it better serves for lightweight AI tasks. When processing the python script for object detection and tracking, the video feed was very slow and laggy and the UNO Q would get very hot quickly. It quickly became apparent that the UNO Q was not going to cut it.

I have now decided to shift the core Architecture from a hybrid SBC (MPU + MCU) to a SoC (ARM HPS + FPGA Fabric). I will now be utilizing the DE-25 Agilex 5 SoC.

Making the switch allows for: 
* Offloading the "heavy lifting" from sequential software loops to parallel hardware logic.
* Nanosecond precision timing for the 333HZ servos without jitter.
Dedicated ARM Cortex HPS to process 120fps global shutter and tracking models.
* Computational headroom to eleminate the camera latency and overheating.

Ultimately, this upgrade transforms the Automated Weapon Station from a constrained proof-of-concept into a highly responsive, real-time tracking system. With the core processing bottlenecks resolved, the next phase of development will focus on creating the python script for object tracking and training an AI model for object detection.
[README.md](https://github.com/user-attachments/files/27412745/README.md)
