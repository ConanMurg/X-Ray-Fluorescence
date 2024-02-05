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
# from matplotlib.widgets import Cursor
# import matplotlib.widgets as widgets
from tkinter import Tk
from tkinter.filedialog import askdirectory

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing

class SnaptoCursor(object):
    def __init__(self, ax, x, y):
        self.ax = ax
        self.ly = ax.axvline(color='k', alpha=0.2)  # the vert line
        self.marker, = ax.plot([0],[0], marker="o", color="crimson", zorder=3) 
        self.x = x
        self.y = y
        self.txt = ax.text(0.7, 0.9, '')

    def mouse_move(self, event):
        if not event.inaxes: return
        x, y = event.xdata, event.ydata
        indx = np.searchsorted(self.x, [x])[0]
        x = self.x[indx]
        y = self.y[indx]
        self.ly.set_xdata(x)
        self.marker.set_data([x],[y])
        self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
        self.txt.set_position((x,y))
        self.ax.figure.canvas.draw_idle()


class dummy():
    key = 0


def mca_reader(file, e=1000):
    # Read in File
    with open(file) as f:
        lines = f.readlines()
        
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

    return [l, o]


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
    l, o = mca_reader(filenames[file])

    # Clear the axes
    plt.cla()

    # Create a bar chart of the data
    bars = ax.bar(o, l, align='center', width=o[-1]-o[-2]) # linewidth = '0.5')
    # Find the max height
    max_height = np.amax(l)

    # Set a minimum max height
    if max_height < 30: max_height = 30

    ax.set_ylim([0, max_height*1.2])
    ax.set_xlim([-0.001, 12])

    plt.vlines(energies[displayer], ymin=0, ymax=max_height*1.1, lw=0.5, linestyles=(0, (5,10)), color='black')

    # Label data points
    h = [1.1, 1.05, 1, 1.05, 1.1, 1.05, 1, 1.05, 1.1, 1.05, 1, 1.05,
         1.1, 1.05, 1, 1.05, 1.1, 1.05, 1, 1.05, 1.1, 1.05, 1, 1.05,
         1.1, 1.05, 1, 1.05, 1.1, 1.05, 1, 1.05, 1.1, 1.05, 1, 1.05,
         1.1, 1.05, 1, 1.05, 1.1, 1.05, 1, 1.05, 1.1, 1.05, 1, 1.05,
         1.1, 1.05, 1, 1.05, 1.1, 1.05, 1, 1.05, 1.1, 1.05, 1, 1.05]

    h = [x * max_height for x in h]

    for i, xy in enumerate(zip(energies[displayer], [i for i in h])):
        plt.annotate(labels[displayer][i], xy=xy, textcoords='data')

    plt.subplots_adjust(top=0.984, bottom=0.04, left=0.022, right=0.99, hspace=0.163, wspace=0.052)
    txt = os.path.basename(os.path.normpath(filenames[file]))
    angle = txt.split("_", 1)[0]
    # angle = txt.split("_", 2)[1]
    plt.legend([f'{angle} Degrees'], loc='upper right')
    fig.canvas.draw_idle()



# Find all files in a directory
directory = askdirectory()
# directory = '//uol.le.ac.uk/root/staff/home/c/cm846/My Documents/Calibration/02_06_23'
filenames = natsorted(glob.glob(os.path.join(directory, '*.mca')))

fig, ax = plt.subplots(nrows=1, ncols=1)

labels = ['C', 'Ca-L', 'Ca-L', 'O', 'F', 'Fe-L', 'Fe-L', 'Ni-L', 'Ni-L', 'Cu-L', 'Cu-L',
          'Na', 'Ga-La', 'Ga-Lb', 'Ge-L', 'Ge-L', 'Mg', 'As-L', 'Mg', 'As-L', 'Al', 'Al',
          'Si', 'Si', 'P-Ka', 'P-Kb', 'S', 'S', 'Cl', 'Cl',
          'Sn', 'K', 'Sn', 'Ca-Ka', 'Ca-Kb',  'Sc', 'Sc',
          'Ti', 'Ti', 'Va', 'Cr', 
          'Va', 'Mn', 'Cr', 'Fe-Ka',
          'Mn',  'Co', 'Fe-Kb',  'Ni-Ka', 'Co', 'Cu', 'Ni-Kb',  'Cu', 
          'Ga', 'Au', 'Ge', 'Ga',  'As', 'Ge',  'As']

energies = [0.277, 0.341, 0.345, 0.525, 0.677, 0.705, 0.718, 0.849, 0.866, 0.928, 0.947,
            1.04, 1.098, 1.125, 1.188, 1.218, 1.254, 1.282, 1.302, 1.317,  1.486, 1.557, 
            1.74, 1.837, 2.01, 2.139, 2.309, 2.465, 2.622, 2.812,
            3.444, 3.59, 3.663, 3.692, 4.013, 4.093, 4.464,
            4.512, 4.933, 4.953, 5.415,
            5.428,  5.9, 5.947, 6.405,
             6.492, 6.931, 7.059,  7.48, 7.649, 8.046, 8.267, 8.904, 
            9.251, 9.713, 9.886, 10.267,  10.543, 10.982,  11.726]

# energies = [0.277, 0.525, 1.04, 1.254, 1.302, 1.486, 1.557, 
#             1.74, 1.837, 2.01, 2.139, 2.309, 2.465, 2.622, 2.812,
#             3.692, 4.013, 0.341, 0.345,  4.512, 4.933, 4.953, 5.428, 5.415, 5.947, 
#             5.9, 6.492, 6.405, 7.059, 6.931, 7.649, 7.48, 8.267, 8.046, 8.904, 0.928, 0.947,
#             9.251, 10.267, 9.886, 10.982, 10.543, 11.726, 1.282, 1.317, 
#             3.444, 3.663,
#             1.188, 1.218,
#             0.677, 0.705, 0.718,
#             4.093, 4.464,
#             0.849, 0.866,
#             9.713,
#             3.59,
#             1.098, 1.125]

energies = np.array(energies)
labels = np.array(labels)

displayer = [False]*len(labels)

# elements = ['C', 'O', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ca', 'Ti', 'Va', 'Cr',
#             'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Ga', 'Ge', 'As', 'As-L', 'Sn', 'Ge-L']

els = [
        # 'C', 
        # 'O', 
       # 'Na', 
        # 'Mg', 
        'Al', 
        'Si',
        # 'P-Ka',
        'P-Kb', 
        # 'S', 
        'Cl', 
        # 'Ca-L'
        # 'Ti', 
        # 'Va', 
        'Cr',
        'Mn', 
        # 'Fe-Ka',
        # 'Fe-Kb',
       # 'Co', 
        # 'Ni-Ka',
        # 'Ni-Kb',
        # 'Cu', 
        # 'Cu-L',
        # 'Ga', 
        'Ge', 
        # 'As', 
        # 'As-L',
        'Sn',
        'Ge-L',
       # 'F',
        # 'Fe-L',
       # 'Sc',
       # 'Ni-L',
       # 'Au',
       # 'K',
       'Ga-Lb',
       'Ca-Ka',
       'Ca-Kb',
       'Blank'
       ]

for el in els:
    v = [i for i,x in enumerate(labels) if x==el]
    for c in v:
        displayer[c] = True
        
# file = 46
file = 70

next_plot(dummy(), first=1)
# cursor = SnaptoCursor(ax, o, l)
# cid =  plt.connect('motion_notify_event', cursor.mouse_move)

# cursor = Cursor(ax, horizOn=True, vertOn=True, useblit=True,
#                 color = 'r', linewidth = 1)
fig.canvas.mpl_connect('key_press_event', next_plot)





# from larch.xrf import create_mca
# x = create_mca(np.array(l), 2048, real_time=60.000000, live_time=24.138000, slope=1, offset=3)
# x.save_mcafile("TestingMCAsave")
