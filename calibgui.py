# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 11:17:03 2023

@author: cm846
"""
import tkinter as tkr
# from matplotlib import pyplot as plt
import numpy as np

__all__ = ['CalibWindow']

class CalibWindow:
    def __init__(self, win, nwin, b_quit, fig, canvas):
        self.fig = fig
        self.canvas = canvas

        self.lbl_el = tkr.Label(win, text="Element")
        self.lbl_peak = tkr.Label(win, text="Peak (ADU)")
        self.lbl_counts = tkr.Label(win, text="Counts in Peak")
        
        self.lbl_c = tkr.Label(win, text='Carbon')
        self.lbl_cu = tkr.Label(win, text='Copper')
        self.lbl_mg = tkr.Label(win, text='Magnesium')
        self.lbl_al = tkr.Label(win, text='Aluminium')
        self.lbl_si = tkr.Label(win, text='Silicon')
        self.lbl_p = tkr.Label(win, text='Phosphorus')
        
        self.text_c = tkr.Entry(win, bd=3, width = 10)
        self.text_cu = tkr.Entry(win, bd=3, width = 10)
        self.text_mg = tkr.Entry(win, bd=3, width = 10)
        self.text_al = tkr.Entry(win, bd=3, width = 10)
        self.text_si = tkr.Entry(win, bd=3, width = 10)
        self.text_p = tkr.Entry(win, bd=3, width = 10)
        self.cal = [self.text_c, self.text_cu, self.text_mg,
                    self.text_al, self.text_si, self.text_p]
        
        self.text_c2 = tkr.Entry(win, bd=3, width = 10)
        self.text_cu2 = tkr.Entry(win, bd=3, width = 10)
        self.text_mg2 = tkr.Entry(win, bd=3, width = 10)
        self.text_al2 = tkr.Entry(win, bd=3, width = 10)
        self.text_si2 = tkr.Entry(win, bd=3, width = 10)
        self.text_p2 = tkr.Entry(win, bd=3, width = 10)
        self.qe = [self.text_c2, self.text_cu2, self.text_mg2,
                   self.text_al2, self.text_si2, self.text_p2]
        
        self.lbl_el.grid(row=1, column=1, padx=5, pady=5)
        self.lbl_c.grid( row=2, column=1, padx=5, pady=5)
        self.lbl_cu.grid(row=3, column=1, padx=5, pady=5)
        self.lbl_mg.grid(row=4, column=1, padx=5, pady=5)
        self.lbl_al.grid(row=5, column=1, padx=5, pady=5)
        self.lbl_si.grid(row=6, column=1, padx=5, pady=5)
        self.lbl_p.grid( row=7, column=1, padx=5, pady=5)
        
        self.lbl_peak.grid(row=1, column=2, padx=5, pady=5)
        self.text_c.grid( row=2, column=2, padx=5, pady=5)
        self.text_cu.grid(row=3, column=2, padx=5, pady=5)
        self.text_mg.grid(row=4, column=2, padx=5, pady=5)
        self.text_al.grid(row=5, column=2, padx=5, pady=5)
        self.text_si.grid(row=6, column=2, padx=5, pady=5)
        self.text_p.grid( row=7, column=2, padx=5, pady=5)
        
        self.lbl_counts.grid(row=1, column=3, padx=5, pady=5)
        self.text_c2.grid( row=2, column=3, padx=5, pady=5)
        self.text_cu2.grid(row=3, column=3, padx=5, pady=5)
        self.text_mg2.grid(row=4, column=3, padx=5, pady=5)
        self.text_al2.grid(row=5, column=3, padx=5, pady=5)
        self.text_si2.grid(row=6, column=3, padx=5, pady=5)
        self.text_p2.grid( row=7, column=3, padx=5, pady=5)

        self.cal_button = tkr.Button(win, command=self.calibrate)
        self.cal_button.config(text='Calibrate', width = 10)
        self.cal_button.grid(row=8, column=2)

        self.qe_button = tkr.Button(win, command=self.quantum_eff)
        self.qe_button.config(text='QE', width = 10)
        self.qe_button.grid(row=8, column=3)

        self.a = None

        b_quit.grid(row = 12, column = 2, padx=5, pady=5)
        self.default()

    def win_quit(self, win, nwin):
        """
        Closes the GUI window, and reopens the main GUI.

        Parameters
        ----------
        win : Tkinter Frame
            The Tkinter frame in which the GUI is running.
            
        nwin : Tkinter Frame.
            The main Tkinter frame which created this frame.

        Returns
        -------
        None.

        """    
        # nwin.deiconify()
        win.destroy()


    def default(self):
        defs = [132, 510, 670, 819, 945, 1085]
        for nr, i in enumerate(self.cal):
            i.delete(0, tkr.END)
            i.insert(0, defs[nr])
        

    def calibrate(self):
        peaks = []
        evs = [277, 930, 1254, 1487, 1740, 2013]
        labs = ["C", "Cu", "Mg", "Al", "Si", "P"]
        labels = []
        corr_evs = []
        for nr, i in enumerate(self.cal):
            data = str(i.get())
            if data.isdigit():
                peaks.append(int(data))
                corr_evs.append(evs[nr])
                labels.append(labs[nr])
        self.show_pic(peaks,corr_evs,labels)


    def quantum_eff(self):
        if self.a is None:
            print("Calibration required first")
            return

        evs = []
        for nr, i in enumerate(self.cal):
            data = str(i.get())
            if data.isdigit():
                evs.append(int(data)*self.a)
        # evs = [277, 930, 1254, 1487, 1740, 2013]
        
        
        # Number of photons per second from the SDD
        int_time = 120 # s 
        sdd_area = 0.7 # cm2
        data = np.array((43572, 119650, 15378, 20386, 16228, 13305), int) / int_time / sdd_area
        qe = [0.14, 0.7, 0.78, 0.7, 0.75, 0.7]
        photons = np.array([x/y for x,y in zip(data,qe)])
        data = data.astype(int).tolist()
        photons = photons.astype(int).tolist()
        counts = photons
        
        # counts = [5187, 4646, 328, 485, 360, 316]
        labs = ["C", "Cu", "Mg", "Al", "Si", "P"]

        labels = []
        corr_evs = []
        corr_counts = []
        nr_counts = []

        for nr, i in enumerate(self.qe):
            data = str(i.get())
            if data.isdigit():
                nr_counts.append(int(data))
                corr_counts.append(counts[nr])
                corr_evs.append(evs[nr])
                labels.append(labs[nr])
        # print(f'nr_counts: {nr_counts}')
        # print(f'corr_counts: {corr_counts}')
        # print(f'corr_evs: {corr_evs}')
        # print(f'labels: {labels}')
        if labels == []:
            return

        corr_qe = [i / j for i, j in zip(nr_counts, corr_counts)]
        # print(corr_qe)
        self.fig.clear()
        p = self.fig.gca()
        p.plot(corr_evs, corr_qe, 'r*')
        # Label data points
        for i, xy in enumerate(zip(corr_evs, [i for i in corr_qe])):
            p.annotate(labels[i], xy=xy, textcoords='data')

        # x = np.array(peaks)
        # y = np.array(corr_evs)
        # x = x[:, np.newaxis]
        # y = y[:, np.newaxis]
        # a, _, _, _ = np.linalg.lstsq(x, y, rcond=-1)
        
        # x = np.array([i for i in range(0, 3000)])
        # x = x[:, np.newaxis]
        # p.plot(x, a*x) # Line of best fit
        p.set_ylim([0, np.amax(corr_qe)*1.2])
        p.set_xlim([0, np.amax(corr_evs)*1.2])
        # p.legend([f'{np.around(a[0][0], 2)}*x'], loc='upper right')
        self.canvas.draw()


    def show_pic(self, peaks, corr_evs, labels):
        """
        Create new image from data.
        """
        self.fig.clear()
        p = self.fig.gca()
        p.plot(peaks, corr_evs, 'r*')
        # Label data points
        for i, xy in enumerate(zip(peaks, [i-100 for i in corr_evs])):
            p.annotate(labels[i], xy=xy, textcoords='data')

        x = np.array(peaks)
        y = np.array(corr_evs)
        x = x[:, np.newaxis]
        y = y[:, np.newaxis]
        a, _, _, _ = np.linalg.lstsq(x, y, rcond=-1)
        # print(a[0])
        self.a = a[0][0]
        x = np.array([i for i in range(0, 3000)])
        x = x[:, np.newaxis]
        p.plot(x, self.a*x) # Line of best fit
        p.set_ylim([0, np.amax(corr_evs)*1.2])
        p.set_xlim([0, np.amax(peaks)*1.2])
        p.legend([f'{np.around(a[0][0], 2)} eV/ADU'], loc='upper right')
        self.fig.suptitle("Gain Calculation (ADU to eV)")
        self.fig.supxlabel("Measured X-ray peaks (ADU)")
        self.fig.supylabel("Expected X-Ray peaks (eV)")
        self.canvas.draw()


