# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 15:48:06 2023

@author: cm846
"""

import numpy as np
import matplotlib.pyplot as plt

x = np.arange(0, 512)
y = np.arange(0, 512)
arr = np.zeros((y.size, x.size))

cx = 384. # X Centre
cy = 320. # Y Centre
r = 58. # 155 pixels radius

# Area  = pi * (r)**2
#       = 3.1415 * (155*0.000015)**2
#       = 1.698e-05 m**2
#       = 16.98 mm**2

# The two lines below could be merged, but I stored the mask
# for code clarity.
mask = ((x[np.newaxis,:]-cx)/1)**2 + ((y[:,np.newaxis]-cy)/1)**2 < r**2
test= np.argwhere(mask == np.max(mask))

arr[mask] = 123.

plt.imshow(mask)
# This plot shows that only within the circle the value is set to 123.
# plt.figure(figsize=(6, 6))
# plt.pcolormesh(x, y, arr)
# plt.colorbar()
# plt.show()



import numpy as np
from matplotlib import pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename


Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
file = askopenfilename(multiple=False)
event_info = np.loadtxt(file)#.astype(int)
# image_info = np.loadtxt(image_info_d, dtype='<u2')#.astype(int)



a = event_info
sg = [1500, 1650, 10, 160]
# COPPER # sg = [2000, 2350, 550, 850] # x1, x2, y1, y2 (0, 4154, 0, 4112)
b = a[ (sg[0]<a[:,1]) & (a[:,1]<sg[1]) ] # Filter rows (0 - 4154)
c = b[ (sg[2]<b[:,2]) & (b[:,2]<sg[3]) ] # Filter cols (0 - 4112)
event_sum = c[:,-1]
count_rate = np.unique(c[:,0], return_counts=True)[1]
print(file)
print(np.mean(count_rate))
beam_var.append(np.mean(count_rate))

rows = event_info[:,1]
cols = event_info[:,2]
event_sum = event_info[:,-1]







