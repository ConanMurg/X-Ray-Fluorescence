# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 15:06:10 2024

@author: cm846
"""
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import matplotlib.colors as mcolors
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing


file = askopenfilename() # select the event-info CMS file
if file == '':
    raise SystemExit()
a = np.loadtxt(file)

sg = [2100, 3600, 1700, 3700]
# 4154 x Col 2
# 4112 y Col 1

b = a[ (sg[0]<a[:,1]) & (a[:,1]<sg[1]) ] # Filter rows (0 - 4154)
c = b[ (sg[2]<b[:,2]) & (b[:,2]<sg[3]) ] # Filter cols (0 - 4112)

Min_adu = 110
Max_adu = 180
# nitrogen: 42 - 85  # 47 - 88
# oxygen: 55 - 120
# copper L: 110 - 180
# magnesium: 150 - 220
# aluminum: 200 - 270
# Silicon: 220 - 300
# phosphorus: 270 - 345

filtered = c[ (Min_adu<c[:,-1]) & (c[:,-1]<Max_adu+1) ] 


blank = np.zeros((4112, 4154), int)
for nr, i in enumerate(range(len(filtered))):
    blank[int(filtered[nr, 2]), int(filtered[nr, 1])] += 1

plt.figure()
plt.imshow(blank.reshape((4112, 4154)), vmin= 0, vmax = 0.5)



# placeholder[0] =  np.einsum('...ij->...j', placeholder) 