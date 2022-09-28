# GRCon 22 Vital Signs

This flowgraph implements the demo shown at GRCon 22 for Respiratory and Heart Rate sensing and estimation

- `vitalSignsTraditional.grc` implements the demonstration shown.  The python script `plotRTGR.py` implemnets a real-time plotting and animation using matplotlib/FuncAnimation
- `vitalSigns.grc` implements an alternative FFT based phase estimation approach with a much higher downsampling rate.
