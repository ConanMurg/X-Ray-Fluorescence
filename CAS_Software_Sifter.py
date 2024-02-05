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
    # a = event_info
    # offset = -1000 # 220 #-235  # Positive is to the left, Negative to the right
    offset = 100
    y_offset = -147 
    # offset = offset - 55 # CU-L
    # y_offset = y_offset + 77 # CU-L
    
    # offset = offset + 27 # CU-L
    # y_offset = y_offset + 54
    
    # offset = 400 # CU-L
    # y_offset = -960  # CU-L
    # offset = 220
    
    offset = 455 # PHOSPHROUS
    y_offset= 2400 # PHOSPHROUS
    
    offset = 305 # SILICON
    y_offset = 2200 # SILICON
    
    # 218 x 218 
    sizereduce = 30 # 30 # -130
    
    # SXR
    sg = [1691-offset+sizereduce, 1909-offset-sizereduce, 2495-y_offset+sizereduce, 2713-y_offset-sizereduce]
    # sg = [1176-90, 1176+90, 3480-90, 3480+90]    
    # sg = [2359-109, 2359+109, 2010-109, 2010+109] 
    # KEVEX
    # sg = [2882-350, 2882+350, 2854-350, 2854+350] # KEVEX
    # sg = [2882-250, 2882+250, 2854-250, 2854+250] # KEVEX
    # sg = [3300, 4000, 50, 750]                      # KEVEX 700 x 700
    # sg = [3400, 3900, 50, 550]                      # KEVEX 500 x 500    
    # sg = [3500, 3800, 50, 350]                      # KEVEX 300 x 300       
    
    # BACKGROUND
    # sg = [3300, 3800, 100, 600]   # BACKGROUND
    
    # FULL
    # sg = [0, 4154, 0, 4112]
    
    # sg = [3877, 4077, 2515, 3015]    # SDD
    # sg = [3477, 3877, 2515, 3015]    # No SDD
    
    # circle_x = 1700 # Cu L
    # circle_y = 2700 # Cu L
    
    # circle_x = 1750 # +50 OXYGEN
    # circle_y = 2750 # OXYGEN
    
    
    # circle_x = 2375
    # circle_y = 2015
    
    # 3500, 3800, 50, 350
    # circle_x = 3650 # Default for SDD Shadow
    # circle_y = 200 # Default for SDD Shadow
    
    circle_x = 2050 # Al 20C
    circle_y = 950 # Al 20C
    
    circle_x = 1610
    circle_y = 390
    circle_x = 2900
    circle_y = 1380
    
    circle_x = 1575 # Si
    circle_y = 400 # Si
    
    circle_x = 1650 # Phosphorus
    circle_y = 470 # Phosphorus
    
    
    # circle_x = 2070
    # circle_y = 2606
    
    circle_x = 643
    circle_y = 2043
    
    circle_r = 155
    
    
    x = np.arange(0, 4154)
    y = np.arange(0, 4112)
    arr = np.zeros((y.size, x.size))
    
    
    # Area  = pi * (r)**2
    #       = 3.1415 * (155*0.000015)**2
    #       = 1.698e-05 m**2
    #       = 16.98 mm**2
    
    sg = [circle_x - circle_r-1, circle_x + circle_r+1, circle_y - circle_r - 1, circle_y + circle_r + 1]
    b = a[ (sg[0]<a[:,1]) & (a[:,1]<sg[1]) ] # Filter rows (0 - 4154)
    c = b[ (sg[2]<b[:,2]) & (b[:,2]<sg[3]) ] # Filter cols (0 - 4112)
    
    
    jaifnsdifn = c[:, 1].astype(int) # X
    jaifnsdifn = (jaifnsdifn - circle_x) ** 2
    
    jaifnsdifn2 = c[:, 2].astype(int) # Y
    jaifnsdifn2 = (jaifnsdifn2 - circle_y) ** 2
    
    combined = jaifnsdifn + jaifnsdifn2
    NEW_MASK = jaifnsdifn + jaifnsdifn2 < circle_r**2
    
    
    # mask = (x[np.newaxis,:]-circle_x)**2 + (y[:,np.newaxis]-circle_y)**2 < circle_r**2
    # test= np.argwhere(mask == np.max(mask)) # Coordinates inside circle
    # new_test = test[:,[1,0]]
        
    
        
    # # np.amax(new_test[:,0]) # 2529  X
    # # np.amax(new_test[:,1]) # 2169  Y
    # # np.amin(new_test[:,0]) # 2221  X
    # # np.amin(new_test[:,1]) # 1861  Y
    
    
    # NEW_mask = (x[np.newaxis,:]-circle_x)**2 + (y[:,np.newaxis]-circle_y)**2 < circle_r**2
    
    
    # sg = [circle_x - circle_r-1, circle_x + circle_r+1, circle_y - circle_r - 1, circle_y + circle_r + 1]
    # b = a[ (sg[0]<a[:,1]) & (a[:,1]<sg[1]) ] # Filter rows (0 - 4154)
    # c = b[ (sg[2]<b[:,2]) & (b[:,2]<sg[3]) ] # Filter cols (0 - 4112)
    
    
    # compare = c[:,1:3].tolist()
    # newer_test = new_test.tolist()
    # nr = 0
    # store = np.zeros((len(compare)), bool)
    # for i in range(len(compare)):
    #     if compare[i] in newer_test:
    #         store[i] = True
    #         # print(f' Success: {compare[i]}')
    #         nr += 1
    
    # print(nr)
    # stored = store.astype(bool)
    # d = c[stored]
    d = c[NEW_MASK]
    
    
    # # Sort Through Data
    # b = a[ (sg[0]<a[:,1]) & (a[:,1]<sg[1]) ] # Filter rows (0 - 4154)
    # c = b[ (sg[2]<b[:,2]) & (b[:,2]<sg[3]) ] # Filter cols (0 - 4112)
    
    event_sum = d[:,-1]
    
    # filtered = d[ (900<d[:,-1]) & (d[:,-1]<980) ] # Iron
    # filtered = d[ (1350<d[:,-1]) & (d[:,-1]<1440) ] # GaAs    
    # filtered = d[ (760<d[:,-1]) & (d[:,-1]<830) ] # Cr    
    # filtered = d[ (650<d[:,-1]) & (d[:,-1]<710) ] # Ti   
    # filtered = d[ (510<d[:,-1]) & (d[:,-1]<570) ] # Ca
    # filtered = d[ (180<d[:,-1]) & (d[:,-1]<250) ] # Aluminium
    # filtered = d[ (150<d[:,-1]) & (d[:,-1]<220) ] # Magnesium
    filtered = d[ (200<d[:,-1]) & (d[:,-1]<290) ] # Silicon
    # filtered = d[ (270<d[:,-1]) & (d[:,-1]<345) ] # Phosphorus
    # filtered = d[ (55<d[:,-1]) & (d[:,-1]<120) ] # Oxygen
    # filtered = d[ (110<d[:,-1]) & (d[:,-1]<180) ] # CuL
    
    # SXR
    # filtered = c[ (20<c[:,-1]) & (c[:,-1]<60) ] # Carbon
    # filtered = c[ (55<c[:,-1]) & (c[:,-1]<120) ] # Oxygen
    # filtered = c[ (110<c[:,-1]) & (c[:,-1]<180) ] # Copper-L
    # filtered = c[ (45<c[:,-1]) & (c[:,-1]<80) ] # Nitrogen
    # filtered = c[ (49<c[:,-1]) & (c[:,-1]<75) ] # Nitrogen
    # filtered = c[ (150<c[:,-1]) & (c[:,-1]<220) ] # Magnesium
    # filtered = c[ (180<c[:,-1]) & (c[:,-1]<250) ] # Aluminium
    # filtered = c[ (200<c[:,-1]) & (c[:,-1]<290) ] # Silicon
    # filtered = c[ (250<c[:,-1]) & (c[:,-1]<350) ] # Phosphorus 
    # filtered = c[ (285<c[:,-1]) & (c[:,-1]<345) ] # Phosphorus - Room Temp
    # KEVEX
    # filtered = c[ (512<c[:,-1]) & (c[:,-1]<570) ] # Calcium
    # filtered = c[ (525<c[:,-1]) & (c[:,-1]<585) ] # Calcium - Room Temp
    # filtered = c[ (640<c[:,-1]) & (c[:,-1]<714) ] # Titanium
    # filtered = c[ (740<c[:,-1]) & (c[:,-1]<835) ] # Chromium
    # filtered = c[ (780<c[:,-1]) & (c[:,-1]<850) ] # Chromium - Room Temp
        # 78842 Counts in 10064 Files, 700 x 700 ROI
        # 41184 Counts in 10064 Files, 500 x 500 ROI
    # filtered = c[ (880<c[:,-1]) & (c[:,-1]<985) ] # Iron
    # filtered = c[ (925<c[:,-1]) & (c[:,-1]<1000) ] # Iron - Room Temp
        # 59939 Counts in 10113	Files, 700 x 700 ROI
        # 32179 Counts in 10113	Files, 500 x 500 ROI
    # filtered = c[ (1310<c[:,-1]) & (c[:,-1]<1400) ] # GaAs
    # filtered = c[ (1350<c[:,-1]) & (c[:,-1]<1440) ] # GaAs - Room Temp
    # filtered = c[ (850<c[:,-1]) & (c[:,-1]<915) ] # GaAs - Room Temp ?????
    # filtered  = c
    plt.figure()
    v = plt.hist(event_sum, bins=np.arange(0, 1501, 1))[0]
    
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
    
    # sfjasfjnsdjk = dark
    # sfjasfjnsdjk[sfjasfjnsdjk<3] = 0
    # sfjasfjnsdjk[sfjasfjnsdjk>50] = 0
    plt.imshow(dark.reshape((4112, 4154)), vmin= 0, vmax = 1)
    
    # Circle
    axes = plt.gca()
    Drawing_uncolored_circle = plt.Circle( (circle_x, circle_y),
                                          circle_r ,
                                          fill = False )
    axes.add_artist( Drawing_uncolored_circle )


# Rectangle
# ax = plt.gca()
# rect = Rectangle((sg[0],sg[2]),sg[1]-sg[0],sg[3]-sg[2],linewidth=1,edgecolor='r',facecolor='none')
# ax.add_patch(rect)


