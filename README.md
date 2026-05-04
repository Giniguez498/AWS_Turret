
# Autonomous 3D-Printed Tracking Turret

An autonomous, computer-vision tracking turret featuring a custom 3D-printed gear system, 
continuous 360° rotation via a central slip ring, and a heavy-duty 35kg servo.

## Tech Stack
* **Software:** Python (Object Tracking), Arduino C/C++
* **Hardware:** Arduino Uno Q, 35kg Servo, 22.4mm Slip Ring, 95mm Lazy Susan
* **Design & Fab:** Fusion 360, Bambu Lab P1S 

## Core Features
* **Custom Gear Drive:** 165mm Ring Gear driven by a 35mm Pinion Gear with "starburst" servo horn pocket.
* **Continuous Rotation:** Central slip ring drop-zone prevents wire tangling during infinite 360° panning.
* **Modular Chassis:** 246x246mm internal bay housing the MCU, independent high-amp battery, and USB dock.

## Roadmap
- [x] Base chassis & slip ring routing
- [ ] Custom Pinion Gear design (Taper-cut 6-arm pocket)
- [ ] 165mm Main Ring Gear & Turntable modeling
- [ ] Python tracking script integration with Arduino serial communication.
