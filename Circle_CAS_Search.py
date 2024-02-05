    # -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 13:19:29 2023

@author: cm846
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from tkinter import Tk
from tkinter.filedialog import askopenfilename

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
files = askopenfilename(multiple=True)


for nr, file in enumerate(files):
    a = np.loadtxt(file)
    # a = np.loadtxt(file, max_rows = 50000000) # .astype(int)
    # a = a[0:(50000000-1473), :]

# AL COATING
    # circle_y = 2606 # CuL
    # circle_x = 2040 # CuL -35C
    circle_y = 3115 # Si
    circle_x = 1635 # Si -35C
    # circle_x = 2050 # Al
    # circle_y = 1375 # Al -35C    
    # circle_x = 1954 # Mg
    # circle_y = 2554 # Mg -35C
    
# No AL COATING
    # circle_x = 2360 # Al (1026)
    # circle_y = 1375 # Al -35C (2682)   
    # circle_x = 1560 # Mg
    # circle_y = 2440 # Mg -35C
    # circle_x = 1743 # P (1205)
    # circle_y = 2593 # P (3145)
    # circle_x = 1205 # Mg
    # circle_y =  2145 # Mg
    # circle_x = 2519 # Cr + Ga
    # circle_y =  2800 # Cr + Ga
    circle_x = 1600 # O (was 1690 for higher count 43955)
    circle_y =  2800 # O
    # circle_x = 935 # N
    # circle_y =  2800 # N
    # circle_x = 1830 # CuL
    # circle_y = 2800 # CuL
    # circle_x = 1840 # P
    # circle_y = 2850 # P
    # circle_x = 2315 # Mg
    # circle_y = 2971 # Mg
    circle_x = 1850 # Si -35C
    circle_y = 2915 # Si
   
    
    circle_r = 155
    
    x = np.arange(0, 4154)
    y = np.arange(0, 4112)
    arr = np.zeros((y.size, x.size))

    sg = [circle_x - circle_r-1, circle_x + circle_r+1, circle_y - circle_r - 1, circle_y + circle_r + 1]
    b = a[ (sg[0]<a[:,1]) & (a[:,1]<sg[1]) ] # Filter rows (0 - 4154)
    c = b[ (sg[2]<b[:,2]) & (b[:,2]<sg[3]) ] # Filter cols (0 - 4112)
    
    jaifnsdifn = c[:, 1].astype(int) # X
    jaifnsdifn = (jaifnsdifn - circle_x) ** 2 # X
    jaifnsdifn2 = c[:, 2].astype(int) # Y
    jaifnsdifn2 = (jaifnsdifn2 - circle_y) ** 2 # Y
    mask = jaifnsdifn + jaifnsdifn2 < circle_r**2 # Circle Mask
    
    d = c[mask]
    
    event_sum = d[:,-1]
    filtered = d[ (220<d[:,-1]) & (d[:,-1]<300) ] # Silicon
    
    # filtered = d[ (110<d[:,-1]) & (d[:,-1]<180) ] # CuL
    # filtered = d[ (42<d[:,-1]) & (d[:,-1]<85) ] # Nitrogen
    # filtered = d[ (55<d[:,-1]) & (d[:,-1]<120) ] # Oxygen
    # filtered = d[ (150<d[:,-1]) & (d[:,-1]<220) ] # Magnesium
    # filtered = d[ (180<d[:,-1]) & (d[:,-1]<250) ] # Aluminium
    # filtered = d[ (945<d[:,-1]) & (d[:,-1]<1010) ] # Iron
    # filtered = d[ (1350<d[:,-1]) & (d[:,-1]<1440) ] # GaAs    
    # filtered = d[ (780<d[:,-1]) & (d[:,-1]<865) ] # Cr    
    # filtered = d[ (650<d[:,-1]) & (d[:,-1]<725) ] # Ti   
    # filtered = d[ (540<d[:,-1]) & (d[:,-1]<590) ] # Ca
    # filtered = c[ (220<c[:,-1]) & (c[:,-1]<285) ] # Silicon
    # filtered = d[ (200<d[:,-1]) & (d[:,-1]<290) ] # Silicon
    # filtered = d[ (270<d[:,-1]) & (d[:,-1]<345) ] # Phosphorus
    # filtered = c[ (1350<c[:,-1]) & (c[:,-1]<1460) ] # GaAs - Room Temp


    # SXR
    # filtered = c[ (20<c[:,-1]) & (c[:,-1]<60) ] # Carbon
    # filtered = c[ (55<c[:,-1]) & (c[:,-1]<120) ] # Oxygen
    # filtered = c[ (110<c[:,-1]) & (c[:,-1]<180) ] # Copper-L
    # filtered = c[ (45<c[:,-1]) & (c[:,-1]<80) ] # Nitrogen
    # filtered = c[ (49<c[:,-1]) & (c[:,-1]<75) ] # Nitrogen
    plt.figure()
    v = plt.hist(event_sum, bins=np.arange(0, 1501, 1))[0]
    # v = plt.hist(a[:,-1], bins=np.arange(0, 1501, 1))[0]    
    # plt.figure()
    plt.hist(filtered[:,-1], bins=np.arange(0, 1501, 1))
    

    ######################################################
    # Carbon background subtraction
    ######################################################
    # a = event_info
    # b = a[ (sg[0]<a[:,1]) & (a[:,1]<sg[1]) ] # Filter rows (0 - 4154)
    # c = b[ (sg[2]<b[:,2]) & (b[:,2]<sg[3]) ] # Filter cols (0 - 4112)
    
    # event_sum_bg = c[:,-1]
    
    # a = data
    # b = a[ (sg[0]<a[:,1]) & (a[:,1]<sg[1]) ] # Filter rows (0 - 4154)
    # c = b[ (sg[2]<b[:,2]) & (b[:,2]<sg[3]) ] # Filter cols (0 - 4112)
    
    # event_sum_data = c[:,-1]
    
    # # new_var_bg = event_sum.tolist()
    # # new_list = new_var_bg + new_var_bg + new_var_bg[0:217]
    # # del new_var_bg
    
    # # plt.figure()
    # vn = plt.hist(event_sum_data, bins=np.arange(0, 1501, 1))[0]
    
    # ve = plt.hist(event_sum_bg, bins=np.arange(0, 1501, 1))[0]
    # newerrr = vn- ve
    # plt.plot(np.arange(0, 1500, 1), newerrr)
    # newerrr[newerrr < 0] = 0
    # print(np.sum(newerrr[20:61]))
    
    
    
    


Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
files = askopenfilename(multiple=True)
for file in files:
    dark = np.memmap(file, dtype='>u2').astype(int)
    plt.figure()


    plt.imshow(dark.reshape((4112, 4154)), vmin= 0, vmax = 1)
    # Circle
    axes = plt.gca()
    Drawing_uncolored_circle = plt.Circle( (circle_x, circle_y),
                                          circle_r ,
                                          fill = False )
    axes.add_artist( Drawing_uncolored_circle )

