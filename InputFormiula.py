# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 14:17:08 2024

@author: cm846
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
t = np.arange(-2.0, 2.0, 0.001)
s = t ** 2
initial_text = "t ** 2"
l, = plt.plot(t, s, lw=2)
lo, = plt.plot(t,s, lw=2)


def submit(text):
    ydata = eval(text)
    l.set_ydata(ydata)
    ax.set_ylim(np.min(ydata), np.max(ydata))
    plt.draw()

def submit2(text):
    ydata = eval(text)
    lo.set_ydata(ydata)
    ax.set_ylim(np.min(ydata), np.max(ydata))
    plt.draw()

axbox = plt.axes([0.1, 0.05, 0.8, 0.075])
text_box = TextBox(axbox, 'Evaluate', initial=initial_text)
text_box.on_submit(submit)

axbox = plt.axes([0.1, 0, 0.8, 0.075])
text_box2 = TextBox(axbox, 'Evaluate', initial=initial_text)
text_box2.on_submit(submit2)

plt.show()