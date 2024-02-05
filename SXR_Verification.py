# -*- coding: utf-8 -*-
"""
Created on Fri May 26 12:46:33 2023

@author: cm846
"""
import os
import glob
import numpy as np
from natsort import natsorted
from matplotlib import pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askdirectory

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing

class dummy():
    key = 0

def mca_reader(file, e=1000):
    # Read in File
    with open(file) as f:
        lines = f.readlines()
    
    time = [item for item in lines if 'START_TIME' in item][0]
    time = time.split(" ", 3)[3].strip()
    secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(time.split(':'))))
    
    # Read in Calibration Settings
    adus, evs = [], []
    ind = lines.index('LABEL - Channel\n') + 1
    try:
        ind_end = lines.index('<<ROI>>\n')
    except:
        ind_end = lines.index('<<DATA>>\n')
    calib = lines[ind:ind_end]
    
    for i, val in enumerate(calib):
        adu, ev = map(float, calib[i].split(" "))
        adus.append(adu)
        evs.append(ev)
    
    # Find m*x + c values
    slope, intercept = np.polyfit(adus, evs, deg=1)
    slope = round(slope, 7)
    intercept = round(intercept, 7)
    # print(slope)
    # print(intercept)
    
    # Read in Data
    start = lines.index("<<DATA>>\n") + 1
    end = lines.index('<<END>>\n')
    
    # Calibrate data from adu to ev
    l = [eval(i) for i in lines[start:end]]
    o= []
    for i in range(len(l)):
        o.append(i*slope+intercept)
    
    # Cut data off at specified point
    l = l[0:e]
    o = o[0:e]

    return [l, o, secs]

def next_plot(j, first=0):
    global file, filenames
    if j.key == "a":
        file -= 1

    elif j.key == "d":
        file += 1

    elif first == 0:
        return

    # Boundary conditions for file
    if file < 0:
        file = len(filenames) -1
        
    if file >= len(filenames):
        file = 0

    # Read in the data
    l, o, secs = mca_reader(filenames[file])
    # Clear the axes
    plt.cla()

    # Create a bar chart of the data
    bars = ax.bar(o, l, align='center', width=o[-1]-o[-2]) # linewidth = '0.5')
    # Find the max height
    max_height = np.amax(l)

    # Set a minimum max height
    if max_height < 30: max_height = 30

    ax.set_ylim([0, max_height*1.2])
    ax.set_xlim([-0.001, 10])

    plt.vlines(energies[displayer], ymin=0, ymax=max_height*1.1, lw=0.5, linestyles=(0, (5,10)), color='black')

    # Label data points
    h = [1.1, 1.05, 1, 1.05]
    h = [x * max_height for x in h]

    for i, xy in enumerate(zip(energies[displayer], [i for i in h])):
        plt.annotate(labels[displayer][i], xy=xy, textcoords='data')

    plt.subplots_adjust(top=0.984, bottom=0.08, left=0.1, right=0.96, hspace=0.163, wspace=0.052)
    txt = os.path.basename(os.path.normpath(filenames[file]))
    angle = txt.split("_", 1)[0]
    try:
        print(txt.split("_", 2)[2])
    except:
        print(txt.split("_", 1)[0])
    # angle = angle.split(".", 1)[0].rstrip('0123456789')
    # angle = txt.split("_", 2)[1]
    
    # ang = txt.split("_", 4)[4]
    # ang = ang.split(".", 1)[0]
    ang = ""
    
    if angle == "C" or angle == "Carbon":
        cnts = np.sum(l[17:33])

    elif angle == "O" or angle == "Oxygen":
        cnts = np.sum(l[33:57])

    elif angle == "Si" or angle == "Silicon":
        cnts = np.sum(l[129:151])

    elif angle == "Al" or angle == "Aluminium":
        cnts = np.sum(l[105:131])

    elif angle == "Cu" or angle == "Copper":
        cnts = np.sum(l[68:96])

    elif angle == "F" or angle == "Fluorine":
        cnts = np.sum(l[43:67])

    elif angle == "Mg" or angle == "Magnesium":
        cnts = np.sum(l[89:113])

    elif angle == "P" or angle == "Phosphorus" or angle == "Phosphorous":
        cnts = np.sum(l[150:173])

    else: cnts = 0
    print(cnts)
    # print(secs)
    plt.legend([f'Element: {filenames[file]}'], loc='upper right')
    fig.canvas.draw_idle()
    plt.xlabel("Energy (KeV)")
    plt.ylabel("X-Ray Counts")



# Find all files in a directory
directory = askdirectory()
filenames = natsorted(glob.glob(os.path.join(directory, '*.mca')))

fig, ax = plt.subplots(nrows=1, ncols=1)

labels = ['C', 'O', 'Si', 'Si', 'Cl', 'Cl', 'Na', 'S', 'S']
energies = [0.277,  0.525,  1.74, 1.837, 2.622, 2.812, 1.04, 2.309, 2.465]


energies = np.array(energies)
labels = np.array(labels)

displayer = [False]*len(labels)
els = ['Cl','Na', 'S']

for el in els:
    v = [i for i,x in enumerate(labels) if x==el]
    for c in v:
        displayer[c] = True
        
# file = 46
file = 0




next_plot(dummy(), first=1)
fig.canvas.mpl_connect('key_press_event', next_plot)
