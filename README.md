# X-Ray-Fluorescence
Spyder Project Python Code files for a GUI that allows for the analysis of X-Ray Fluorescence events for .raw and .tiff filetypes  

# Capabilities
- Allows the creation of a Dark Frame from a CMOS based sensor [Will create an averaged frame from a directory of either .raw or .tiff dark frames].
- Takes in raw / unprocessed data (i.e. frames from the detector with x-rays incident on them), background subtracts using the selected dark frame, then using a custom, 3x3, 5x5, or 7x7 algorithm, finds all x-ray events (single pixel and split events) and creates a histogram in an interactive plot for analysis.
- Allows analysed data to be saved, exported, and imported.
- Custom Region of Interest (ROI's) and search parameters for identifying and troubleshooting different areas of the CMOS sensor.

# How To Use
Run the CAS_Recreation.py script. This will open the GUI.
