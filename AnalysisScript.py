import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import matplotlib.colors as mcolors
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing


def event_sorter(file, circle_x=2000, circle_y=2000, Min_adu=0, Max_adu=1000, r=155):
    """
    Min / Max ADU for different elements
        carbon: 20-60
        nitrogen: 42 - 85
        oxygen: 55 -120
        copper L: 110 - 180
        magnesium: 150 - 220
        aluminum: 180 - 250
        silicon: 220 - 300
        phosphorus: 270 - 345

    Parameters
    ----------
    file : string
        file path for the CMS file.
    circle_x : int
        X Coordinate of the Circle Center. The default is 2000.
    circle_y : int
        Y Coordinate of the Circle Center. The default is 2000.
    Min_adu : int
        Filter events between Min_adu and Max_adu. The default is 0.
    Max_adu : int
        Filter events between Min_adu and Max_adu. The default is 1000.
    r : int, optional
        Circle Radius. The default is 155.

    Returns
    -------
    None.

    """
    print(1)
    a = np.loadtxt(file)
    x = np.arange(0, 4154)
    y = np.arange(0, 4112)
    arr = np.zeros((y.size, x.size))
    sg = [circle_x - circle_r-1, circle_x + circle_r+1, circle_y - circle_r - 1, circle_y + circle_r + 1]
    b = a[ (sg[0]<a[:,1]) & (a[:,1]<sg[1]) ] # Filter rows (0 - 4154)
    c = b[ (sg[2]<b[:,2]) & (b[:,2]<sg[3]) ] # Filter cols (0 - 4112)
    Circular_x = c[:, 1].astype(int) # X
    Circular_x = (Circular_x - circle_x) ** 2
    Circular_y = c[:, 2].astype(int) # Y
    Circular_y = (Circular_y - circle_y) ** 2
    mask = Circular_x + Circular_y < circle_r**2 # Circular Mask
    d = c[mask] # filter the events table by the circular mask 
    event_sum = d[:,-1] # find the sum of the 3x3 events that occur inside the circular mask
    filtered = d[ (Min_adu<d[:,-1]) & (d[:,-1]<Max_adu+1) ] 
    main_color = mcolors.to_rgb('dodgerblue')
    highlight_color = mcolors.to_rgb('limegreen')

    plt.figure()
    binvals, bins, patches = plt.hist(event_sum, bins=np.arange(0, 1501, 1), color=main_color)
    # plt.hist(filtered[:,-1], bins=np.arange(0, 1501, 1))

    left_border = Min_adu
    right_border = Max_adu


    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    for p, x in zip(patches, bin_centers):
        #x, _ = p.get_xy()
        #w = p.get_width()
        if left_border < x  < right_border:
            f = 2*min(x-left_border, right_border-x) / (right_border - left_border)
            f = f ** 0.5
            p.set_facecolor(highlight_color)
            
    plt.axvspan(left_border, right_border, color='lightgoldenrodyellow', zorder=0)
    plt.show()
    return(len(filtered))
    
    
    
    
#############
# choose the Event-Info_Threshold... .CMS file
#############
file = askopenfilename() # select the event-info CMS file
if file == '':
    raise SystemExit()
a = np.loadtxt(file)

###############################
# the circular mask parameters (coordinates and radius)
###############################
circle_x = 1837         # x coordinate for Si + O 20C
circle_y = 2109         # y coordinates for Si + O 20C

# circle_x = 2000 # 20C Cu
# circle_y = 2910 # 20C cu

# circle_x = 2000
# circle_y = 2910

# circle_x = 1649 # P
# circle_y = 2600 # P -35C

# circle_x = 1695 # Cu
# circle_y = 2600 # Cu # -35C

# circle_x = 1604 # Mg -35C
# circle_y = 2848 # Mg

# circle_x = 1585 # N + O -35C
# circle_y = 2848 # N + O 

circle_x = 1725 # Cu 20C 21306F0-0001
circle_y = 2610

circle_x = 1582


circle_x = 1282
circle_y = 2509

circle_x = 1260
circle_y = 2670
# circle_x = 1630 # O 20C 21306F0-0001
# circle_y = 2848

# circle_x = 1930
# circle_y = 2800

# circle_x = 2521
# circle_y = 2832

circle_x = 2360 # Kevex
circle_y = 2315 # Kevex
    
circle_x = 3657 - 445
circle_y = 423

circle_x = 1777 # Cu L -35C
circle_y = 3328 # Cu L - 35C

circle_x = 2888 # mg
circle_y = 3004 # mg

circle_x = 1740 # p
circle_y = 2487 # p

# circle_x = 2438 # Cu L -35C
# circle_y = 1381 # Cu L - 35C

circle_x = 3450
circle_y = 2650





circle_x = 700
circle_y = 2000


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

event_sum = d[:,-1] # find the sum of the 3x3 events that occur inside the circular mask
# plt.figure()
# plt.hist(event_sum, bins=np.arange(0, 1501, 1))


###############################
# adjust these here to filter all events to just the peak of interest
###############################
Min_adu = 220
Max_adu = 310

# carbon: 20-60
# nitrogen: 42 - 85  # 47 - 88
# oxygen: 55 - 120
# copper L: 110 - 180
# magnesium: 150 - 220
# aluminum: 200 - 270
# Silicon: 220 - 300
# phosphorus: 270 - 345

# Ti 650 - 730
# Cr 790 - 880
# Fe 940 - 1035
# Ca 535 - 585
# Ga 1370 - 1470

filtered = d[ (Min_adu<d[:,-1]) & (d[:,-1]<Max_adu+1) ] 
print(len(filtered))
print(np.amax(d[:,0])-10)





divisor_tickness = 1
main_color = mcolors.to_rgb('dodgerblue')
highlight_color = mcolors.to_rgb('limegreen')
divisor_color = mcolors.to_rgb('crimson')

plt.figure()
binvals, bins, patches = plt.hist(event_sum, bins=np.arange(0, 1501, 1), color=main_color)
# plt.hist(filtered[:,-1], bins=np.arange(0, 1501, 1))

left_border = Min_adu
right_border = Max_adu


bin_centers = 0.5 * (bins[:-1] + bins[1:])
for p, x in zip(patches, bin_centers):
    #x, _ = p.get_xy()
    #w = p.get_width()
    if left_border < x  < right_border:
        f = 2*min(x-left_border, right_border-x) / (right_border - left_border)
        f = f ** 0.5
        p.set_facecolor(highlight_color)
    # elif left_border-divisor_tickness < x <= left_border or right_border <= x < right_border + divisor_tickness:
    #     p.set_facecolor(divisor_color)
        
plt.axvspan(left_border, right_border, color='lightgoldenrodyellow', zorder=0)
plt.show()
###############################################################
###############################################################
###############################################################




#############################################
# Show where the circle is centered on the image (allows us to adjust the where the circular mask is placed and optimize the counts inside our ROI)
#############################################

files_img = askopenfilename(multiple=True) # Select the Event-Result-Image… .RAW files.
for file in files_img:
    dark = np.memmap(file, dtype='>u2').astype(int)
    # print(np.mean(dark))
    # print(np.std(dark))
    fig = plt.figure()
    fig.set_size_inches(10.,10.)
    plt.imshow(dark.reshape((4112, 4154)), vmin= 0, vmax = 1)
    # plt.savefig("C:\\Users\\cm846\\OneDrive - University of Leicester\\MPO Images\\Oxygen.png", dpi=200)
    
    axes = plt.gca()
    Drawing_uncolored_circle = plt.Circle( (circle_x, circle_y), circle_r, fill = False)
    axes.add_artist(Drawing_uncolored_circle)
    
    # new 
    # mean: 241.20929161616294
    # std:  42.41248251667465

    # old
    # mean: 241.23086989896757
    # std:  42.39839917252359



# x 2100 - 3600
# y 1700 - 3700
