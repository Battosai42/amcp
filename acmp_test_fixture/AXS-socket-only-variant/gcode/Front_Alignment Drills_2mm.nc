(G-CODE GENERATED BY FLATCAM v8.991 - www.flatcam.org - Version Date: 2019/12/27)

(Name: Front_Alignment Drills_2mm)
(Type: G-code from Excellon)
(Units: MM)

(Created on Friday, 21 February 2020 at 13:04)

(Feedrate: 200.0 mm/min)
(Feedrate rapids 1500.0 mm/min)

(Z_Cut: -2.0 mm)
(Z_Move: 2.0 mm)
(Z Toolchange: 15.0 mm)
(X,Y Toolchange: 0.0000, 0.0000 mm)
(Z Start: None mm)
(Z End: 20.0 mm)
(Steps per circle: 64)
(Preprocessor Excellon: default)

(X range:    2.1750 ...    4.1750  mm)
(Y range:    2.1750 ...   48.6250  mm)

(Spindle Speed: None RPM)
G21
G90
G94




G01 F200.00
G00 Z2.0000

M03
G00 X3.1750 Y3.1750
G01 Z-2.0000
G01 Z0
G00 Z2.0000
G00 X3.1750 Y3.1750
G01 Z-2.0000
G01 Z0
G00 Z2.0000
G00 X3.1750 Y47.6250
G01 Z-2.0000
G01 Z0
G00 Z2.0000
G00 X3.1750 Y47.6250
G01 Z-2.0000
G01 Z0
G00 Z2.0000
M05
G00 Z20.00
G00 X0.0 Y0.0

