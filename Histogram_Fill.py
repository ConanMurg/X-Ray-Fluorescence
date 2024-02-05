# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 12:22:36 2024

@author: cm846
"""

import numpy as np
from numpy import pi
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

#Define the function we're graphing
def gaussian(x, sigma):
    N = pow(2*pi,-0.5)/sigma
    Z = x/sigma
    return N*np.exp(-Z*Z/2)

#Default standard deviation of 1
std0=1

#Set up initial default data
X = np.arange(-5,5,0.1)
Y = gaussian(X,std0)

#Create an axis for main graph
fig, ax = plt.subplots(1,1)
ax.set_xlim([-5,5])
ax.set_ylim([0,1])

#[line] will be modified later with new Y values
[line]=ax.plot(X,Y)
#this moves the figure up so that it's not on top of the slider
fig.subplots_adjust(bottom=0.4)

#Create slider
min_slider_ax = fig.add_axes([0.25,0.25,0.65,0.03])
min_slider = Slider(min_slider_ax, 'Min Slider', 1,20, valinit=std0, valstep=1)


#Create slider
max_slider_ax = fig.add_axes([0.25,0.1,0.65,0.03])
max_slider = Slider(max_slider_ax, 'Max Slider', 1,20, valinit=std0, valstep=1)


def line_update(val):
    ax.fill_between([-5,5], [1,1], facecolor='white', alpha=1)  # fill white
    #ax.fill_between(X, [1 for v in Y], facecolor='white', alpha=1)  # fill white
    # Y = gaussian(X,sigma_slider.val)
    # line.set_ydata(Y)
    print(min_slider.val)
    print(max_slider.val)
    print(len(X[min_slider.val:max_slider.val]))
    ax.fill_between(X[min_slider.val:max_slider.val], Y[min_slider.val:max_slider.val], facecolor='blue', alpha=0.30) # fill blue
    fig.canvas.draw_idle()

#Call the above function when the slider is changed
max_slider.on_changed(line_update)
min_slider.on_changed(line_update)
line_update(0)  # fill curve first time

plt.show()
