# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 10:29:50 2023

@author: cm846
"""

from numpy import pi, sin, sqrt, log
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
import os


def Gamma2sigma(Gamma):
    '''Function to convert FWHM (Gamma) to standard deviation (sigma)'''
    return Gamma * sqrt(2) / ( sqrt(2 * log(2)) * 2 )

def signal(mean, width, height):
    return height * np.exp( - ((t-mean)/Gamma2sigma(width))**2 )



axis_color = 'lightgoldenrodyellow'

fig = plt.figure()
ax = fig.add_subplot(111)

def mouse_event(event):
    print(f'x: {np.around(event.xdata)}, y: {np.around(event.ydata)},'
          f' width: {np.around(width)}')
    mean = event.xdata
    height = event.ydata
    y1 = signal(mean, width, height)
    line.set_ydata(signal(mean, width_slider.val, height))
    fig.canvas.draw_idle()
cid = fig.canvas.mpl_connect('button_press_event', mouse_event)


# Adjust the subplots region to leave some space for the sliders and buttons
fig.subplots_adjust(left=0.25, bottom=0.25)


t = np.arange(-20, 4100, 0.1)
height = 6000
width = 7
mean = 0


maxy = 0
# plt.xlim(400,800)
plt.xlim(0, 500)
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
files = askopenfilename(multiple=True)
for nr, file in enumerate(files):
    # plt.figure()
    print(os.path.splitext(os.path.basename(file))[0])
    with open(file) as f:
        lines = f.readlines()
        x = [float(line.split()[0]) for line in lines]
        y = [float(line.split()[1]) for line in lines]
        # if nr == 0:
        #     x = [x - 432 for x in x]
        
        # if nr == 1:
        #     x = [x - 400 for x in x]
        
        # if nr == 2:
        #     x = [x - 362 for x in x]
        
        # if nr == 3:
        #     x = [x - 144 for x in x]
        
        # if nr == 0:
        #     x = [x - 276*5993/345/3.65*10 for x in x]
        
        # if nr == 1:
        #     x = [x - 254*5993/345/3.65*10 for x in x]
        
        # if nr == 2:
        #     x = [x - 230*5993/345/3.65*10 for x in x]
        
        # if nr == 3:
        #     x = [x - 73*5993/345/3.65*10 for x in x]
        if np.amax(y) > maxy:
            maxy = np.amax(y)

    ax.plot(x,y, label=f'{os.path.splitext(os.path.basename(file))[0]}',
             marker='o', markersize=2)
    x = np.array(x)
    # plt.xlim(100*5993/345/3.65*10, np.amax(x))
    # plt.ylim(1, maxy)
    # plt.yscale('log')
    # plt.xscale('log')
    
plt.legend()


# ax.plot(t, [10]*len(t))
# Draw the initial plot
# The 'line' variable is used for modifying the line later
[line] = ax.plot(t, signal(mean, width, height), linewidth=2, color='red')
# ax.set_xlim([-20, 50])
# ax.set_ylim([0, 10000])

# Add two sliders for tweaking the parameters



# # Define an axes area and draw a slider in it
width_slider_ax  = fig.add_axes([0.25, 0.15, 0.65, 0.03], facecolor=axis_color)
width_slider = Slider(width_slider_ax, 'Width', 1, 50, valinit=width, valstep=1)




# # Draw another slider
# freq_slider_ax = fig.add_axes([0.25, 0.1, 0.65, 0.03], facecolor=axis_color)
# freq_slider = Slider(freq_slider_ax, 'Freq', 0.1, 30.0, valinit=freq_0)



# Define an action for modifying the line when any slider's value changes
def sliders_on_changed(val):
    line.set_ydata(signal(mean, width_slider.val, height))
    fig.canvas.draw_idle()
width_slider.on_changed(sliders_on_changed)
# freq_slider.on_changed(sliders_on_changed)


# # Add a button for resetting the parameters
# reset_button_ax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
# reset_button = Button(reset_button_ax, 'Reset', color=axis_color, hovercolor='0.975')
# def reset_button_on_clicked(mouse_event):
#     freq_slider.reset()
#     amp_slider.reset()
# reset_button.on_clicked(reset_button_on_clicked)



# # Add a set of radio buttons for changing color
# color_radios_ax = fig.add_axes([0.025, 0.5, 0.15, 0.15], facecolor=axis_color)
# color_radios = RadioButtons(color_radios_ax, ('red', 'blue', 'green'), active=0)
# def color_radios_on_clicked(label):
#     line.set_color(label)
#     fig.canvas.draw_idle()
# color_radios.on_clicked(color_radios_on_clicked)

plt.show()