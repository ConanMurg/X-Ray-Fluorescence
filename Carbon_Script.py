import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from tkinter import Tk
from tkinter.filedialog import askopenfilename


Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing


#############
# choose the Event-Info_Threshold... .CMS file
#############
files_bg = askopenfilename(multiple=True)                # select the carbon_background CMS file 
files = askopenfilename(multiple=True)                 # select the carbon CMS file


for nr, file in enumerate(files):
    a = np.loadtxt(file)
    
# the circular mask parameters (coordinates and radius)
    # circle_x = 1850         # x coordinate for Si
    circle_x = 1391 + 94 #+ 350
    # circle_y = 2915         # y coordinates for Si
    circle_y = 2341
    circle_r = 155         # radius of the circular mask 
    
    x = np.arange(0, 4154)
    y = np.arange(0, 4112)
    arr = np.zeros((y.size, x.size))


# reduce search grid size (ignore this part of the code - just improves the speed)
    sg = [circle_x - circle_r-1, circle_x + circle_r+1, circle_y - circle_r - 1, circle_y + circle_r + 1]
    b = a[ (sg[0]<a[:,1]) & (a[:,1]<sg[1]) ] # Filter rows (0 - 4154)
    c = b[ (sg[2]<b[:,2]) & (b[:,2]<sg[3]) ] # Filter cols (0 - 4112)


# create a circular mask to filter search grid
    Circular_x = c[:, 1].astype(int) # X
    Circular_x = (Circular_x - circle_x) ** 2
    Circular_y = c[:, 2].astype(int) # Y
    Circular_y = (Circular_y - circle_y) ** 2
    mask = Circular_x + Circular_y < circle_r**2 # Circular Mask
    
    d = c[mask] # filter the events table by the circular mask 
    
    event_sum_data = d[:,-1] # find the sum of the 3x3 events that occur inside the circular mask
    
    


    


######################################################
# Carbon background subtraction
######################################################


for nr, file in enumerate(files_bg):
    a = np.loadtxt(file)


    sg = [circle_x - circle_r-1, circle_x + circle_r+1, circle_y - circle_r - 1, circle_y + circle_r + 1]
    b = a[ (sg[0]<a[:,1]) & (a[:,1]<sg[1]) ] # Filter rows (0 - 4154)
    c = b[ (sg[2]<b[:,2]) & (b[:,2]<sg[3]) ] # Filter cols (0 - 4112)


    Circular_x = c[:, 1].astype(int) # X
    Circular_x = (Circular_x - circle_x) ** 2
    Circular_y = c[:, 2].astype(int) # Y
    Circular_y = (Circular_y - circle_y) ** 2
    mask = Circular_x + Circular_y < circle_r**2 # Circular Mask
    
    d = c[mask] # filter the events by the circular mask 
    
    event_sum_bg = d[:,-1] # all of the 3x3 background inside the circular mask


# Now that we have found all the events inside the circle for the data and background files, we can create the histograms of each before subtracting them.    
plt.figure()
data_hist = plt.hist(event_sum_data, bins=np.arange(0, 1501, 1))[0]    
background_hist = plt.hist(event_sum_bg, bins=np.arange(0, 1501, 1), alpha= 0.5)[0]


Carbon_hist = data_hist - background_hist
Carbon_hist[Carbon_hist < 0] = 0 # Remove any values that are negative 


plt.figure()
plt.plot(np.arange(0, 1500, 1), Carbon_hist) # Plot the histogram of all the carbon events


Min_adu = 20 # adjust these based on the histogram plot
Max_adu = 60 # adjust these based on the histogram plot


print(f'Number of events between {Min_adu} and {Max_adu}: {np.sum(Carbon_hist[Min_adu:Max_adu+1])}') # Finds the number of events inside the Carbon peak (between 20 and 60 ADU - possibly adjust this based on the histogram plot)








#############################################
# Show where the circle is centered on the image (allows us to adjust the where the circular mask is placed and optimize the counts inside our ROI)
#############################################


files_img = askopenfilename(multiple=True) # Select the Event-Result-Image… .RAW files.
for file in files_img:
    dark = np.memmap(file, dtype='>u2').astype(int)
    plt.figure()




    plt.imshow(dark.reshape((4112, 4154)), vmin= 0, vmax = 1)
    # Circle
    axes = plt.gca()
    Drawing_uncolored_circle = plt.Circle( (circle_x, circle_y),
                                          circle_r ,
                                          fill = False )
    axes.add_artist( Drawing_uncolored_circle )