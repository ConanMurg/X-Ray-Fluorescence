# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 09:43:38 2023

@author: cm846
"""

import os
import glob
import numpy as np
from natsort import natsorted
from tifffile import imread
from matplotlib import pyplot as plt
from heapq import nsmallest

from scipy.signal import savgol_filter


scale = 4

dark = imread("Theseus_QE/Non-OBF 30C/Dark_-30C.tiff")

# dark = imread("CIS_NonOBF_Carbon/Averaged Dark Frames/-40C_Dark.tiff")
dark = dark.astype(int)


blank = np.zeros((512, 512), int)
# dirs = "Theseus_QE/Non-OBF 30C/SXR-Phosphorus"
dirs = "Theseus_QE/KEVEX/KEVEX-Titanium"

hotpixels = np.load('Theseus_QE/Non-OBF 30C/15_ADU_HotpixelMap.npy').tolist()

for directory in [directory[0] for directory in os.walk(dirs)]:
    print(directory)
    file = natsorted(glob.glob(os.path.join(directory, '*.tiff')))
    for f in file:
        xray10 = imread(f).astype(int)
        sub10 = np.subtract(xray10, dark)
        sub10= sub10[::scale, ::scale]
        
        for i in range(sub10.shape[0]):
                diff = sub10[i, 256:512]
                heights, bins= np.histogram(diff, bins = np.arange(np.amin(diff), np.amax(diff)+1, 1))
                heights = heights.astype(int)
                bins = np.delete(bins, len(bins)-1)
                y_values, temp_l, temp_r = [], [], []
                y_values = heights.tolist()
                peak_height = max(y_values)
                mean = bins[y_values.index(peak_height)]
                sub10[i,256:512] = sub10[i,256:512] - mean
                
        for i in range(sub10.shape[0]):
                diff = sub10[i, 0:256]
                heights, bins= np.histogram(diff, bins = np.arange(np.amin(diff), np.amax(diff)+1, 1))
                heights = heights.astype(int)
                bins = np.delete(bins, len(bins)-1)
                y_values, temp_l, temp_r = [], [], []
                y_values = heights.tolist()
                peak_height = max(y_values)
                mean = bins[y_values.index(peak_height)]
                sub10[i,0:256] = sub10[i,0:256] - mean
        
        
        sshape = sub10.shape
        sub10 = sub10.flatten()
        sub10[hotpixels] = -10001
        sub10 = sub10.reshape(sshape)
        
        blank[(sub10 > 30) & (sub10 < 1000)] +=1
        
    if len(file) > 0: 
        plt.figure()
        plt.imshow(blank, vmax=5, vmin=0)
        # plt.imshow(blank[256:384,:], vmax=1, vmin=0)


# raise SystemExit


blank2 = blank[256:384,:] # Only Q3

scale = 8
summed = np.zeros((int(128/scale), int(512/scale)), int)
for x in range(scale):
    for y in range(scale):
        summed = summed + blank2[x::scale, y::scale]
plt.figure()
plt.imshow(summed, vmin = np.amin(summed), vmax = np.amax(summed))


plt.imshow(summed)
s_mean = np.mean(summed)
s_std = np.std(summed)
print('')
print('Both')
print(f'Mean: {s_mean}')
print(f'Std: {s_std}')
print(f'Ratio: {s_std/s_mean}')

summedLR = summed[:, int(512/scale/2):int(512/scale)]
plt.figure('OBF')
plt.imshow(summedLR)
s_mean = np.mean(summedLR)
s_std = np.std(summedLR)
print('')
print('OBF')
print(f'Mean: {s_mean}')
print(f'Std: {s_std}')
print(f'Ratio: {s_std/s_mean}')
print(np.amax(summedLR))
print(len(summedLR[summedLR == np.amax(summedLR)]))
print(np.amin(summedLR))
print(len(summedLR[summedLR == np.amin(summedLR)]))


summedLR = summed[:, 0:int(512/scale/2)]
plt.figure('Non-OBF')
plt.imshow(summedLR)
s_mean = np.mean(summedLR)
s_std = np.std(summedLR)
print('')
print('Non-OBF')
print(f'Mean: {s_mean}')
print(f'Std: {s_std}')
print(f'Ratio: {s_std/s_mean}')
print(np.amax(summedLR))
print(len(summedLR[summedLR == np.amax(summedLR)]))
print(np.amin(summedLR))
print(len(summedLR[summedLR == np.amin(summedLR)]))

np.nonzero(summedLR == np.amin(summedLR))

# Y 4, X 60 MAX 240, 272

# Y 24, X 46 MIN 184, 352