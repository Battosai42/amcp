# amcp
**WORK IN PROGRESS!**

ampc is an automated measurement tool of crystal parameters using a vector network analyser. 

![Gui_Example](python3/gui/images/gui_overview.png)

## Project Description
This Project is intended to automate the measurement of crystals up to about 150MHz using a cheap VNA such as the miniVNA or nanoVNA. The measurement method requires a passive test-fixture according to IEC-444 which is a douple-pi network terminating the crystal at 12.5Ohm.

## Feedback
I would be very interessted to hear some feedback from people finding this project interessting, have suggestions or even started using it. Please contact me by mail (git.b42@gmail.com).

## Project Status
### Software
- [X] Basic Gui
- [X] Basic Functions
  - [X] Phase-Shift Method
  - [X] -3dB Bandwidth Method
  - [X] Export as SPICE/Spectre model file (untested)
  - [X] Save/Load Tool Setup
- [ ] Advanced Functions
  - [ ] Support Threading
  - [ ] Automated VNA setup for easier use

#### Hardware Support
- [X] miniVNA tiny 
- [X] nanoVNA 
- [ ] Generic Wrapper for other VNAs

### Hardware
- [ ] Example Test-Fixture (IEC-444)
