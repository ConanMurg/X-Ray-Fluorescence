# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 10:11:49 2022
Python Code for Handling Detector Data
University of Leicester
School of Physics and Astronomy

@author: cm846

Requires installation of a few modules:
 - mttkinter
 - glob
 - natsorted
"""
from mttkinter import mtTkinter as tkr
import logging
from tkinter import ttk
from tkinter.filedialog import askopenfilename as askf
from tkinter.filedialog import asksaveasfilename as askfs
from tkinter.filedialog import askdirectory as askd
import os
import csv
import json
import glob
from threading import Thread, Event
from functools import partial
from queue import Queue
from natsort import natsorted
from scipy.stats import norm
import numpy as np
from matplotlib.figure import (Figure, SubplotParams)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.widgets import MultiCursor
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import pathlib
from tifffile import imread
from darkframegui import DFWindow  ######
from hotpixelgui import HPWindow   ######
from paramsgui import ParamsWindow ######
from calibgui import CalibWindow   ######
# from xray_finder import xrf_analysis #####
from xray_5x5_finder import xrf_analysis #####
from scipy.signal import savgol_filter

__all__ = ['Parameters', 'MyWindow', 'Startup']

class Parameters:
    """
    Description:
        Stores parameters from a config file. Uses setters and getters to ensure
        that the config file contains the correct data types and values for
        every variable.

    Params: vals.
        vals = [rows, cols, threshold, sec_threshold, searchgrid, dir_df,
                dir_hp, dir_save]

    E.g.
        rows, cols = int.
        threshold, sec_threshold = int or float.
        searchgrid = list of 4 integers.
        dir_df, dir_hp, dir_save = string

        vals = [2040, 2048, 90, 20, [460, 1555, 0, 935], "C:/Users/cm846/dark.raw",
                "C:/Users/cm846/hp.raw", "C:/Users/cm846/"]
    """
    def __init__(self, vals):
        if not isinstance(vals, list): # Ensure config file contains a list
            raise TypeError

        if len(vals) < 8: # Ensure list has at least 8 parameters
            raise IndexError

        if not all (isinstance(i, (int, float)) for i in vals[0:4]):
            raise TypeError

        if not isinstance(vals[4], list): # Ensure searchgrid is a list
            raise TypeError

        if vals[2] < vals[3]: # Ensure threshold >= sec_threshold
            raise ValueError

        self.rows = vals[0]
        self.cols = vals[1]
        self.threshold = vals[2]
        self.sec_threshold = vals[3]
        self.searchgrid = vals[4]
        self.dir_df = vals[5]
        self.dir_hp = vals[6]
        self.dir_filenames = vals[7]
        self.dark = np.zeros((), int)
        self.hot_pixels = np.zeros((), int)
        self.element = None
        self.pixel_size	= 0.0011 # cm
        self.int_time = 20.54 # 19.94
        self.roi = "All"
        self.LR = "All"
        self.scale = 4
        
    @property
    def rows(self):
        """
        Returns rows
        """
        return self.__rows

    @rows.setter
    def rows(self, var):
        """
        Setter for n. Ensures new value is positive and an integer.
        """
        if var > 0 and isinstance(var, int):
            self.__rows = var

    @property
    def cols(self):
        """
        Returns cols
        """
        return self.__cols

    @cols.setter
    def cols(self, var):
        """
        Setter for m. Ensures new value is positive and an integer.
        """
        if var > 0 and isinstance(var, int):
            self.__cols = var

    @property
    def threshold(self):
        """
        Returns threshold value.
        """
        return self.__threshold

    @threshold.setter
    def threshold(self, value):
        """
        Setter for threshold. Ensures value is numeric and positive.
        """
        if isinstance(value, (int, float)):
            if value > 0:
                self.__threshold = value

    @property
    def sec_threshold(self):
        """
        Returns sec_threshold value.
        """
        return self.__sec_threshold

    @sec_threshold.setter
    def sec_threshold(self, value):
        """
        Setter for sec_threshold. Ensures value is numeric and positive.
        """
        if 0 < value < self.threshold and isinstance(value, int):
            self.__sec_threshold = value

    @property
    def searchgrid(self):
        """
        Returns searchgrid value.
        """
        return self.__searchgrid

    @searchgrid.setter
    def searchgrid(self, search):
        """
        Setter for searchgrid. Ensures value is a list of 4 integers.
        """
        if isinstance(search, list) and len(search) == 4:
            if all(isinstance(x, int) for x in search):
                self.__searchgrid = search

    @property
    def roi(self):
        """
        Returns roi for the dark frame. For instance, if we want to evaluate
        only the bottom quarter or top three quarters of the image.
        """
        return self.__roi

    @roi.setter
    def roi(self, val):
        if val in ["All", "Q1-Q3", "Q1", "Q2", "Q3", "Q4"]:
            self.__roi = val

    @property
    def LR(self):
        """
        Returns LR for the dark frame. For instance, if we want to evaluate
        only the left half or right half of the image.
        """
        return self.__LR
    
    @LR.setter
    def LR(self, val):
        if val in ["All", "Left", "Right", "LL", "ML", "MR", "RR"]:
            self.__LR = val

    @property
    def scale(self):
        """
        Returns scale value.
        """
        return self.__scale

    @scale.setter
    def scale(self, value):
        """
        Setter for scale. Ensures value is numeric and positive.
        """
        if value > 0 and isinstance(value, int):
            self.__scale = value


class MyWindow:
    """
    Description:
        Creates a Tkinter GUI for importing data and creating a
        dark frame image for a CCD detector.

    Params: win.
        The Tkinter window which the following buttons and layout will populate.

    E.g.
        <<< import tkinter as tkr
        <<< window = tkr.Tk()
        <<< mywin = MyWindow(window)
        <<< window.title('Example Code')
        <<< window.geometry("750x750+10+10")
        <<< window.mainloop()

    """
    def __init__(self, win):
        try:
            with open("config", "r", encoding='UTF-8') as config:
                values = json.load(config)

        except FileNotFoundError:
            print("Error with config file - resorting to defaults\n")
            self.update_console("Error with config file - resorting to defaults")
            values = self.defaults()

        try:
            self.params = Parameters(values)

        except IndexError as i_err:
            print("IndexError: Number of Values in Config are wrong. Program aborting.\n")
            win.destroy()
            raise SystemExit(0) from i_err

        except TypeError as t_err:
            print("TypeError: Values in Config are wrong. Program aborting.\n")
            win.destroy()
            raise SystemExit(0) from t_err

        except ValueError as v_err:
            print("Exception: threshold must be larger than sec_threshold. Program aborting.\n")
            win.destroy()
            raise SystemExit(0) from v_err

        else:
            assert values[2] >= values[3], "Thresh >= sec_threshold failed."

        finally:
            self.plot_select = True # Display singlepixel (T) or multipixel (F) graph.
            self.stop_plot = False
            self.queue_time = Queue()
            self.queue_data = Queue()
            self.event = Event()
            self.data_sp = []
            self.data_mp = []
            self.energy_sp = None
            self.energy_mp = None
            self.file_nr = 0
            self.after_id = None
            self.is_tiff_file = False
            # self.calib = 1 # 1.84496667
            self.save_hist_param = False


        # Create buttons
        self.button_create_hp = tkr.Button(win, command = lambda: self.hp_gui(win))
        self.button_create_hp.config(text='Create Hot Pixel Map', width=20)      # Hot Pixel Map
        self.button_create_hp.config(bg='#DBDBDB')
        self.button_create_df = tkr.Button(win, command = lambda: self.df_gui(win))
        self.button_create_df.config(text='Create Dark Frame', width=20)         # Dark Frame
        self.button_create_df.config(bg='#DBDBDB')

        self.button_hist_df = tkr.Button(win, command = self.hist_dark)
        self.button_hist_df.config(text='Histogram Frame', width=20)
        self.button_hist_sub = tkr.Button(win, command = self.image_subtracted)
        self.button_hist_sub.config(text='Dark Subtracted Frame', width=20)

        self.button_hist_save = tkr.Button(win, command = self.change_save)
        self.button_hist_save.config(text='Enable Save Histogram', width=20)

        self.button_load_df = tkr.Button(win, command = self.darkframe)          # Sel Dark Frame
        self.button_load_df.config(text='Select Dark Frame', width = 20)
        self.button_load_hp = tkr.Button(win, command = self.load_hot_pixel_map) # Sel Hot Pixel Map
        self.button_load_hp.config(text='Select Hot Pixel Map', width=20)
        self.button_data = tkr.Button(win, command = self.sample_data)
        self.button_data.config(text='Sample Data (FWHM)', width=20)           # Sample Data File
        self.button_datas = tkr.Button(win,command = lambda: self.check_params(win))
        self.button_datas.config(text='Choose X-Ray Frames', width=20)           # Start analysis
        self.button_quit = tkr.Button(win, command = lambda: self.confirm_exit(win))
        self.button_quit.config(text = 'Quit', width = 20)                       # Quit
        self.button_params = tkr.Button(win, command = lambda: self.params_gui(win, self.params))
        self.button_params.config(text='Update Parameters', width = 20)        # Update Params

        self.button_calibration = tkr.Button(win, command = lambda: self.calib_gui(win))
        self.button_calibration.config(text="Calibration", width=20)
        self.button_calibration.grid(row=14, column = 2, padx=5, pady=5)

        # Create text labels
        string = (f'x({self.params.searchgrid[0]}, {self.params.searchgrid[1]}),'
                  f' y({self.params.searchgrid[2]}, {self.params.searchgrid[3]})')
        lbl1 = tkr.Label(win, text='Threshold (1) (ADU)')
        lbl2 = tkr.Label(win, text='Threshold (2) (ADU)')
        lbl3 = tkr.Label(win, text='Search Grid (Pixels)')
        self.text_searchgrid = tkr.Entry(win, bd=3, width = 20) # Search Grid
        self.text_searchgrid.insert(0, string)
        self.text_searchgrid.config(state='readonly')
        self.text_thresh = tkr.Entry(win, bd=3, width = 20)     # Primary Threshold
        self.text_thresh.insert(0, self.params.threshold)
        self.text_thresh.config(state='readonly')
        self.text_thresh2 = tkr.Entry(win, bd=3, width = 20)    # Secondary Threshold
        self.text_thresh2.insert(0, self.params.sec_threshold)
        self.text_thresh2.config(state='readonly')

        # Place buttons in grid array
        self.button_create_df.grid(row = 1, column = 1,  padx=20, pady=5)   # Create Dark Frame
        self.button_create_hp.grid(row= 1, column = 2, padx=5, pady=5)      # Create Hot Pixel Map
        self.button_load_df.grid(row = 2, column = 1,  padx=20, pady=5)     # Select Dark Frame

        self.button_hist_df.grid(row = 17, column= 2,padx=20, pady=20)
        self.button_hist_sub.grid(row =17, column= 1,padx=20, pady=20)
        self.button_hist_save.grid(row=17, column=3, padx=20, pady=20)

        self.button_load_hp.grid(row = 2, column = 2, padx=20, pady=5)      # Select Hot Pixel Map
        self.button_params.grid(row = 3, column = 1, padx=5, pady=5)        # Update Parameters
        self.button_data.grid(row = 3, column = 2,  padx=5, pady=5)         # Sample Data File
        self.button_datas.grid(row = 7, column = 1,  padx=20, pady=5)       # Start XRF Analysis
        self.button_quit.grid(row = 14, column = 1,  padx=20, pady=5)       # Quit
        lbl1.grid(row = 4, column = 1, padx=5, pady=5)                 # Text labels
        lbl2.grid(row = 5, column = 1, padx=5, pady=5)
        lbl3.grid(row = 6, column = 1, padx=5, pady=5)
        self.text_thresh.grid( row = 4, column = 2, padx=5, pady=5)    # Entry boxes
        self.text_thresh2.grid(row = 5, column = 2, padx=5, pady=5)
        self.text_searchgrid.grid(row = 6, column = 2, padx=5, pady=5)
        self.my_progress = ttk.Progressbar(win, orient=tkr.HORIZONTAL, # Progress Bar
                                           length=380, mode = 'determinate')
        self.my_progress.grid(row=10, column=1, columnspan=2, padx=20, pady=5)

        # Frame for time displays
        self.time_frame = tkr.Frame(win)
        self.time_frame.grid(row=9, column=1, columnspan=2, sticky="nsew", padx=20, pady=5)
        self.elapsedtime = tkr.Text(self.time_frame, width=15, height=1, state='disabled')
        self.elapsedtime.pack(side="left")
        self.remainingtime = tkr.Text(self.time_frame, width =15, height=1, state='disabled')
        self.remainingtime.pack(side="right")

        # Create interactive figure with a toolbar inside Frame
        image_frame = tkr.Frame(win)
        image_frame.grid(row = 1, column = 4, rowspan=15, padx=20, pady=20, sticky="nsew")
        bottom = tkr.Frame(image_frame)
        bottom.pack(side=tkr.BOTTOM, fill=tkr.BOTH, expand=tkr.TRUE)
        plot_params = SubplotParams(left = 0.1, bottom = 0.1, right = 0.95, top = 0.95,
                                    wspace = 0.05, hspace = 0.05)
        self.fig = Figure(figsize = (9, 9), dpi = 72, subplotpars = plot_params)
        self.canvas = FigureCanvasTkAgg(master = image_frame, figure=self.fig)
        self.canvas.draw()

        self.toolbar = NavigationToolbar2Tk(window = image_frame, canvas = self.canvas)
        self.toolbar.update()
        self.toolbar.pack(in_ = bottom, side = tkr.LEFT)
        button_ch = tkr.Button(image_frame, command = self.clear_pic) # Clear Pic
        button_ch.config(text='Clear', width = 5)
        button_ch.pack(in_ = bottom, side = tkr.RIGHT)
        self.button_stop_plot = tkr.Button(win, command = self.stop_plotting)
        self.button_stop_plot.config(text='Lock', width = 5)
        self.button_stop_plot.pack(in_ = bottom, side = tkr.RIGHT, padx=1)

        self.button_compare = tkr.Button(win, command = self.data_comparison)
        self.button_compare.config(text='Expand', width = 5)
        self.button_compare.pack(in_ = bottom, side = tkr.RIGHT, padx=1)

        self.button_sum = tkr.Button(win, command = self.data_sum)
        self.button_sum.config(text='Sum', width = 5)
        self.button_sum.pack(in_ = bottom, side = tkr.RIGHT, padx=1)

        self.canvas.get_tk_widget().pack(side=tkr.BOTTOM, fill=tkr.BOTH, expand=tkr.TRUE)

        def on_key_press(event):
            key_press_handler(event, self.canvas, self.toolbar)
        self.canvas.mpl_connect("key_press_event", on_key_press)

        # Enable Buttons button
        button_enable = tkr.Button(win, command = self.enable_buttons)
        button_enable.config(width = 20, text="Force Enable Buttons")
        button_enable.grid(row = 7, column = 2, padx=5, pady=5)

        # Switch Graph button
        button_calc_stop = tkr.Button(win, command = self.stop_calc)
        button_calc_stop.config(width = 20, text="Stop Calculation")
        button_calc_stop.grid(row = 8, column = 1, padx=5, pady=5)

        # Switch Graph button
        button_switch_hist = tkr.Button(win, command = self.switch_hist)
        button_switch_hist.config(width = 20, text="Switch Histogram")
        button_switch_hist.grid(row = 8, column = 2, padx=5, pady=5)


        button_dev = tkr.Button(win, command = lambda: self.exc_mplan(self.file_nr))
        button_dev.config(width = 20, text="Developer")
        # button_dev.grid(row = 14, column = 2, padx=5, pady=5)

        button_left = tkr.Button(win, command = self.left)
        button_left.config(width = 20, text="Left")
        button_left.grid(row=15, column = 1, padx=5, pady=5)
        button_right = tkr.Button(win, command = self.right)
        button_right.config(width = 20, text="Right")
        button_right.grid(row=15, column = 2, padx=5, pady=5)

        button_load = tkr.Button(win, command= self.load_prev_data)
        button_load.config(width=20, text="Load Data")
        button_load.grid(row=16, column = 1, padx=5, pady=5)

        button_save = tkr.Button(win, command= self.save_data)
        button_save.config(width=20, text="Save Data")
        button_save.grid(row=16, column = 2, padx=5, pady=5)

        # Console Display
        self.console = tkr.Text(win, width = 38, height=3, state='disabled')
        self.console.grid(row=11, column=1, columnspan=2, rowspan=3, padx=20, pady=0, sticky="nsew")

        win.protocol('WM_DELETE_WINDOW', lambda: self.confirm_exit(win)) # GUI exit protocol


    def change_save(self):
        self.save_hist_param = not self.save_hist_param
        print(self.save_hist_param)


    def image_subtracted(self):
        if self.stop_plot:
            return

        try:
            if self.params.dark.shape == ():
                raise ValueError
            dark = self.params.dark
            filename = askf()

            if not filename:
                raise FileNotFoundError
                
            
            path = pathlib.Path(filename)

            if path.suffix == ".raw":
                arr = np.memmap(filename, dtype='>u2').astype(int)
                arr = arr.reshape((self.params.rows, self.params.cols))
                arr = arr.flatten()
            

            arr = np.subtract(arr, dark)
            
            # arr[blank[blank>0].tolist()] == 0
            # arr = arr * 5993/345 / 3.65 * 10

            if not arr.any():
                raise RuntimeWarning

            if path.suffix == ".tiff":
                self.plot_hist(arr, nr_bins= 5993/345 / 3.65 * 10, xmin=np.amin(arr), xmax=4100* 5993/345 / 3.65 * 10, sample=True,
                               string="Histogram of Pixel Values from Dark Subtracted Frames (BSI Non-OBF)") # Create histogram of data [Display on frame]
                if self.plot_select:
                    self.show_pic(arr.reshape(x.shape), [0, 20])


            else: # if .raw
                self.plot_hist(arr, nr_bins=1)
                if self.plot_select:
                    self.show_pic(arr.reshape((self.params.rows, self.params.cols)))

        except FileNotFoundError:
            self.update_console("No File Chosen")

        except ValueError:
            self.update_console("No Dark Frame Imported")

        except RuntimeWarning:
            self.update_console("Selected data file is identical to dark frame")



    def hist_dark(self):
        x = self.params.dark
        x = x.reshape((self.params.rows, self.params.cols))

        try:
            index2 =  ["Left", "Right", "LL", "ML", "MR", "RR", "All"].index(self.params.LR)

        except: pass

        else:
            LRlist1 = [2, 2, 4, 4, 4, 4]
            LRlist2 = [0, 1, 0, 1, 2, 3]
            if index2 != 6: x = np.split(x, LRlist1[index2], axis=1)[LRlist2[index2]]


        try:
            index3 =  ["Q1-Q3", "Q1", "Q2", "Q3", "Q4", "All"].index(self.params.roi)

        except: pass

        else:
            list1 = [0, 0, 1, 2, 3, 4]
            list2 = [3, 1, 2, 3, 4, 5]
            if index3 != 5: x = np.concatenate(np.split(x, 4)[list1[index3]:list2[index3]])
                
        # print(f'rows: {x.shape[0]}, cols: {x.shape[1]}')
        # plt.imshow(x, interpolation = None, cmap='hot', vmin=0, vmax=4095)
        # plt.savefig(f"C:/Users/Conan/OneDrive - University of Leicester/CIS/Non-OBF 15C/CIS_Non_OBF_{self.params.roi}_Image.png",
        #             bbox_inches='tight')


        try:
            self.fig.clear()    # Clear previous figure
            p = self.fig.gca()  # Find the subplot axes
            data = np.array(x).flatten()

            if len(data) == 0:
                raise ValueError

            xmin = np.amin(data)
            xmax = np.amax(data)
            nr_bins = 1
            if self.plot_select:
                n, bins, patches = p.hist(data, bins=np.arange(xmin, xmax+nr_bins, nr_bins), 
                                          facecolor='green', alpha=0.75, density=0)
    
                p.set_xlim(xmin, xmax)
                p.set_ylim(0, 1.01*np.max(n))
                self.fig.supxlabel("Pixel Value (ADU)")
                self.fig.supylabel("Frequency (%)")
                self.fig.suptitle("Histogram of Pixel Values (ADU)")
            
            else:
                data = data * 5993/345 / 3.65 * 10
                nr_bins = 5993/345 / 3.65 * 10
                xmin = np.amin(data)
                xmax = np.amax(data)
                n, bins, patches = p.hist(data, bins=np.arange(xmin, xmax+nr_bins, nr_bins), 
                                          facecolor='green', alpha=0.75, density=0, cumulative=0)
                if xmin < 0.1: xmin = 0.1
                # p.set_xlim(xmin, xmax)
                # p.set_ylim(0.0015, 1.01*np.max(n))
                p.set_xlim(np.amin(bins), np.amax(bins))
                p.set_ylim(0, 1.01*np.amax(n))
                # p.set_yscale('log')
                # p.set_xscale('log')
                self.fig.supxlabel("Pixel Value (ADU)")
                self.fig.supylabel("Cumulative Frequency (%)")
                self.fig.suptitle("Cumulative Histogram of Pixel Values (ADU)")

            
            p.grid(True)        # Overlay grid
            

            # if self.plot_select:
            #     scale_x = 930 / 510 / 3.65 # / 0.0194
            
            # scale_x = 1

            # if scale_x != 1:
            #     self.fig.supxlabel("Dark Current (e-/pixel/s)")
            #     self.fig.supxlabel("Pixel Value (KeV)")

            # ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(np.around(x*scale_x, 3)))
            # ax2 = self.fig.gca()
            # ax2.xaxis.set_major_formatter(ticks_x)

            self.canvas.draw()  # Update the canvas
            # self.fig.savefig("TESTINGSAVEFUNCTON")
            
            if self.save_hist_param is True:
                print("Attempting Save")
                c=[bins, n]
                save_hist_data = askfs(filetypes=[("txt", ".txt")], defaultextension=".txt")
                if save_hist_data == '':
                    return
                else:
                    with open(save_hist_data, "w") as file:
                        for x in zip(*c):
                            file.write("{0}\t{1}\n".format(*x))
            

        except TypeError:
            self.update_console("plot_hist function failed.")

        except ValueError:
            pass



    def data_sum(self):
        """
        Find the number of counts within the range shown on image pane.

        Returns
        -------
        None.

        """
        if not self.event.is_set():
            return

        p = self.fig.gca()
        xmin, xmax = p.get_xlim()
        xmin = np.around(xmin, 0)
        xmax = np.around(xmax, 0)
        if self.plot_select:
            e = np.array(self.energy_sp)
        else:
            e = np.array(self.energy_mp)
        e = e[e > xmin]
        e = e[e < xmax]
        self.update_console(f'Number of events in window: {len(e)}.')
        self.update_console(f' - Range: {xmin} - {xmax} ADU')
        self.update_console(f'Number of Files: {len(self.data_sp)}')

        pixel_size = self.params.pixel_size
        int_time = self.params.int_time
        pixel_area	= pixel_size * pixel_size # cm^2
        x1, x2, y1, y2 = self.params.searchgrid
        ROI = (x2-x1)*(y2-y1) # Pixels
        roi_area = ROI*pixel_area # cm^2
        self.update_console(f'ROI: {roi_area}')
        t = len(e) / (int_time * len(self.data_sp) / 1000) / roi_area
        self.update_console(f'Counts /s /cm: {t}')


    def save_data(self):
        """
        Saves the data into a csv.

        Returns
        -------
        None.

        """
        if len(self.data_mp) == 0 or len(self.data_sp) == 0:
            self.update_console("Collect some data first!")
            return

        initdir = os.path.dirname(os.path.realpath(__file__))
        try:
            f = askfs(filetypes=[("csv", ".csv")], defaultextension=".csv",
                                         initialdir=initdir)
            with open(f, "w", newline="", encoding='UTF-8') as f:
                writer = csv.writer(f)
                writer.writerows(self.parameters)
                writer.writerows(self.data_mp)
                writer.writerows(self.data_sp)

        except Exception as err:
            logging.exception(err)
            self.update_console("Failed to save data")
            print("Failed to save data")


    def load_prev_data(self):
        """
        Loads in a csv file containing all the data from previous analysis

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        initdir = os.path.dirname(os.path.realpath(__file__))
        try:
            filename = askf(initialdir=initdir, defaultextension='.npy',
                            filetypes=[('csv','*.csv'), ('All files','*.*')])
            with open(filename, encoding='UTF-8') as file:
                reader = csv.reader(file)
                states = [[item for item in row if item != ''] for row in reader]

            if len(states[0]) != 5:
                print("Here")
                print(states)
                raise ValueError

            params = [json.loads(item) for item in states[0]]
            dir_dark, dir_hp, dir_filenames = states[1:4]
            parameters = [params, dir_dark, dir_hp, dir_filenames]

            hot_pixels = np.load(dir_hp[0]).tolist()
            rows, cols, searchgrid = params[0:3]

            # EDITS REQUIRED
            if os.path.splitext(os.path.basename(dir_dark[0]))[1] == '.tiff':
                filenames = natsorted(glob.glob(os.path.join(dir_filenames[0], '*.tiff')))
                dark = imread(dir_dark[0])
                dark = dark[::self.params.scale, ::self.params.scale]
                self.is_tiff_file = True

            else:
                filenames = natsorted(glob.glob(os.path.join(dir_filenames[0], '*.raw')))
                dark = np.fromfile(dir_dark[0], dtype='>u2')

            states[4:] = [[json.loads(item) for item in row] for row in states[4:]]

            data_mp = states[4:int(len(states)/2+2)]
            data_sp = states[int(len(states)/2+2):int(len(states))]

            energy_mp = []
            for i in data_mp:
                for k in i:
                    energy_mp.append(sum(k[1]))

            energy_sp = []
            for i in data_sp:
                for k in i:
                    energy_sp.append(k[1])

            parameter = [rows, cols, searchgrid] + [hot_pixels]

        except Exception as err:
            print("Fail")
            logging.exception(err)
            data_sp = []
            data_mp = []
            energy_sp = None
            energy_mp = None
            filenames = None
            params = None
            self.update_console("Failed to load previous data!")

        else:
            self.params.dark = dark
            self.params.dir_df = dir_dark[0]
            # os.path.dirname(os.path.abspath(dir_dark[0])) # CHANGE TO JUST DIRECTORY

            self.params.hot_pixels = hot_pixels
            self.params.dir_hp = dir_hp[0]

            self.file_view = partial(self.data_viewer, files=filenames,
                                     params=[rows,cols,searchgrid,hot_pixels])
            self.params.dir_filenames = dir_filenames[0]
            self.params.element = os.path.basename(os.path.dirname(filenames[0]))

            self.params.threshold = params[3]
            self.params.sec_threshold = params[4]
            self.params.searchgrid = searchgrid

            self.parameters = parameters

            self.data_sp = data_sp
            self.data_mp = data_mp
            self.energy_sp = energy_sp
            self.energy_mp = energy_mp
            self.update_params()

            self.event.set()
            self.file_view = partial(self.data_viewer, files=filenames, params=parameter)
            self.switch_hist()
            # self.show_pic(self.params.dark.reshape(rows, cols))
            # x = np.zeros((rows*cols), dtype=np.int32)
            # x[self.params.hot_pixels] = 1
            # x = np.reshape(x, (rows, cols))
            # self.show_pic(x, v=1)
            self.file_nr = 0
            print("Done")


    def stop_plotting(self):
        """
        Locks the display

        Returns
        -------
        None.

        """
        self.stop_plot = not self.stop_plot # Switch from locked/unlocked to unlocked/locked

        if self.stop_plot:
            self.button_stop_plot.config(text='Unlock')
            self.update_console("Image is pinned to the display")
        else:
            self.button_stop_plot.config(text='Lock')
            self.update_console("Display is now unlocked")


    def data_comparison(self):
        """
        Brings up the quad-view of data comparison

        Returns
        -------
        None.

        """
        if self.energy_sp is None or len(self.energy_sp) == 0:
            return
        try:
            self.file_view(self.data_sp, self.data_mp, self.file_nr, expand=True)

        except Exception as err:
            logging.exception(err)
            self.update_console("Error with data comparison function")
            print("Error")


    def left(self):
        """
        Cycle to the previous file in quad-view.

        Returns
        -------
        None.

        """
        if self.stop_plot:
            return

        if self.event.is_set(): # If calculation has finished running
            if self.file_nr <= 0:
                self.file_nr = len(self.data_sp)

            self.file_nr -= 1
            self.exc_mplan(self.file_nr)


    def right(self):
        """
        Cycle to the next file in quad-view.

        Returns
        -------
        None.

        """
        if self.stop_plot:
            return

        if self.event.is_set(): # If calculation has finished running
            if self.file_nr >= len(self.data_sp)-1:
                self.file_nr = -1
            self.file_nr += 1
            self.exc_mplan(self.file_nr)


    def exc_mplan(self, file_nr=0):
        """
        Bring up the quad-view

        Parameters
        ----------
        file_nr : TYPE, optional
            DESCRIPTION. The default is 0.

        Returns
        -------
        None.

        """
        if self.stop_plot:
            return

        if self.event.is_set(): # If calculation has finished running
            self.update_console(f'File: {file_nr+1} / {len(self.data_sp)}')
            self.file_view(self.data_sp, self.data_mp, file_nr)


    def switch_hist(self):
        """
        Change the graph from single to multi pixel or vice versa

        Returns
        -------
        None.

        """
        if self.stop_plot:
            return

        self.plot_select = not self.plot_select

        if self.event.is_set(): # If calculation has finished running
            if self.energy_mp is None or self.energy_sp is None:
                self.update_console("No data collected yet - try choosing x-ray frames")
                return

            if self.plot_select:
                if len(self.energy_sp) != 0:
                    string = (f'Histogram of Single Pixel Energy: {self.params.element}')
                        
                    # self.plot_hist(self.energy_sp, nr_bins=1, xmin=0, xmax=2000, sample=False,
                    #                 string="Histogram of Single Pixel Energies (BSI Non-OBF)",
                    #                 save=self.save_hist_param)
                    self.plot_line(self.energy_sp, nr_bins=1, string="Histogram of Single Pixel Values")
            else:
                if len(self.energy_mp) != 0:
                    string = (f'Histogram of Multi Pixel Energy: {self.params.element}')
                    self.plot_line(self.energy_mp, nr_bins=1, string=string)

                # ll = self.energy_sp + self.energy_mp
                # self.plot_line(ll, nr_bins=1, string="Histogram of Pixel Energies")
            # self.plot_hist(ll, nr_bins=1, xmin=0, xmax=2000, sample=False,
            #                 string="Histogram of Pixel Energies (BSI Non-OBF)",
            #                 save=self.save_hist_param)


    def stop_calc(self):
        """
        Stops the calculation running in another thread.

        Returns
        -------
        None.

        """
        try:
            if not self.event.is_set():
                self.event.set()
                self.worker.join()

        except AttributeError: # Will occur if threading event has not run
            pass


    def confirm_exit(self, win):
        """
        Saves parameters into config file for next run of software.

        """
        try:
            self.event.set()
            self.worker.join()

        except AttributeError: # Will occur if threading event has not run
            pass

        try:
            self.update_console("Saving parameters")
            values = []
            for _ in self.params.__dict__.values():
                values += [_]

            with open("config", "w", encoding='UTF-8') as config:
                json.dump(values[0:8], config)

        except Exception as err:
            logging.exception(err)
            self.update_console("Failed to save parameters")
            print("Failed to save parameters")

        else:
            self.update_console("Parameters successfully saved")

        try:
            self.update_console("Quitting")
            for after_id in win.tk.eval('after info').split(): # Ensures after callback cancelled
                win.after_cancel(after_id)

            # win.quit()
            win.destroy()
            raise SystemExit(0)


        except Exception as exc:
            self.update_console("Error Quitting Program")
            logging.exception(exc)
            raise SystemExit(0) from exc


    def update_console(self, text):
        """
        Print text to the console on the GUI.

        Parameters
        ----------
        text : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.console["state"] = 'normal'    # Elapsed Time
        self.console.insert(tkr.END, '\n' + text)
        self.console.see(tkr.END)
        self.console["state"] = 'disabled'

    def update_params(self):
        """
        Update all the parameters from the textboxes in the GUI.

        Returns
        -------
        None.

        """
        # self.update_console("Updated!")
        self.text_thresh.config(state='normal')
        self.text_thresh2.config(state='normal')
        self.text_searchgrid.config(state='normal')
        self.text_thresh.delete(0, tkr.END)
        self.text_thresh2.delete(0, tkr.END)
        self.text_searchgrid.delete(0, tkr.END)
        string = (f'x({self.params.searchgrid[0]}, {self.params.searchgrid[1]}),'
                  f' y({self.params.searchgrid[2]}, {self.params.searchgrid[3]})')
        self.text_thresh.insert(0, self.params.threshold)
        self.text_thresh2.insert(0, self.params.sec_threshold)
        self.text_searchgrid.insert(0, string)

        self.text_thresh.config(state='readonly')
        self.text_thresh2.config(state='readonly')
        self.text_searchgrid.config(state='readonly')


    def defaults(self):
        """
        Returns default values for config file.
        """
        values = [2040,  2048,  90,  20,  [460,  1555,  10,  935]]
        values.append("C:/Users/cm846/OneDrive - University of Leicester/"
                      "Python/Dark Frames")
        values.append("C:/Users/cm846/OneDrive - University of Leicester/"
                      "Python/Dark Frames/Mg_Frames")
        values.append("C:/Users/cm846/OneDrive - University of Leicester/")
        return values


    def disable_toolbar(self):
        """
        Disables the toolbar under the image pane on the GUI

        Returns
        -------
        None.

        """
        toolitems = list(map(list, zip(*self.toolbar.toolitems)))[0] # Find button names on toolbar
        toolitems = [_ for _ in toolitems if _ is not None] # Remove any Nonetypes

        for i in toolitems:
            self.toolbar._buttons[i]["state"] = tkr.DISABLED


    def disable_buttons(self):
        """
        Disables the buttons on the GUI.

        Returns
        -------
        None.

        """
        buttons = [self.button_load_df, self.button_load_hp, self.button_data,
                   self.button_datas, self.button_quit, self.button_params]

        for i in buttons:
            i["state"] = tkr.DISABLED

        self.disable_toolbar()


    def enable_toolbar(self):
        """
        Enable the toolbar under the image pane on the GUI

        Returns
        -------
        None.

        """
        toolitems = list(map(list, zip(*self.toolbar.toolitems)))[0] # Find button names on toolbar
        toolitems = [_ for _ in toolitems if _ is not None] # Remove any Nonetypes

        for i in toolitems:
            self.toolbar._buttons[i]["state"] = tkr.NORMAL


    def enable_buttons(self):
        """
        Enables the buttons on the GUI.

        Returns
        -------
        None.

        """
        buttons = [self.button_load_df, self.button_load_hp, self.button_data,
                   self.button_datas, self.button_quit, self.button_params]

        for i in buttons:
            i["state"] = tkr.NORMAL

        self.enable_toolbar()


    def check_params(self, win):
        """
        Checks that dark frame has been imported and that there are files in
        the selected directory before beginning x-ray analysis.

        """
        initdir="C:/Users/cm846/OneDrive - University of Leicester/Python/Dark Frames/Mg_Frames"
        if self.params.dir_filenames:
            initdir = self.params.dir_filenames

        try:
            if self.params.dark.shape == (): # Error if Dark Frame not selected
                raise NameError

            directory = askd(initialdir = initdir)

            if not directory: # Return error message if no directory is selected
                raise ValueError

            if self.is_tiff_file:
                filenames = natsorted(glob.glob(os.path.join(directory, '*.tiff')))

            else:
                filenames = natsorted(glob.glob(os.path.join(directory, '*.raw')))

            if len(filenames) == 0: # Return error message if no files are found in directory
                raise ValueError

            self.params.dir_filenames = directory

        except NameError:
            self.update_console("Dark Frame Not Selected")

        except ValueError:
            self.update_console("Error Importing .raw Files")

        else:
            self.update_console("\n" + "Starting Calculation" + "\n")
            self.disable_buttons()
            self.event.clear()

            rows = self.params.rows # Make a subset
            cols = self.params.cols
            searchgrid = self.params.searchgrid
            threshold = self.params.threshold
            sec_threshold = self.params.sec_threshold
            dark = self.params.dark         # Import Dark Frame
            hot_pixels = self.params.hot_pixels    # Define the hot pixels
            self.params.element = os.path.basename(os.path.dirname(filenames[0]))

            params = [rows, cols, searchgrid, threshold, sec_threshold]
            self.parameters = [params, [self.params.dir_df], [self.params.dir_hp],
                               [self.params.dir_filenames]]
            parameters = [rows, cols, searchgrid, threshold, sec_threshold, dark, hot_pixels]
            self.file_view = partial(self.data_viewer, files=filenames, params=[rows,cols,searchgrid,hot_pixels])
            self.worker=Thread(target=xrf_analysis, args=(filenames, self.queue_time, 
                                                          self.queue_data, self.event, 
                                                          parameters, self.is_tiff_file,
                                                          self.params.roi, self.params.LR,
                                                          self.params.scale))
            self.worker.start()
            self.after_id = None
            self.time_frame.after(1, self.update_time_display)


    def update_time_display(self):
        """
        Updates Tkinter time elapsed, time remaining, and progress bar as the
        x-ray finder calculation runs in another thread.

        Returns
        -------
        None.

        """
        stop = 0
        if not self.queue_time.empty():
            elaps, remain, percent, energy_sp, energy_mp, stop = self.queue_time.get() # Get values from Queue()

            self.elapsedtime["state"] = 'normal'    # Elapsed Time
            self.elapsedtime.delete('1.0',   tkr.END)
            self.elapsedtime.insert('1.0',   elaps)
            self.elapsedtime["state"] = 'disabled'

            self.remainingtime["state"] = 'normal'  # Remaining Time
            self.remainingtime.delete('1.0', tkr.END)
            self.remainingtime.insert('1.0', remain)
            self.remainingtime["state"] = 'disabled'

            self.my_progress['value'] = percent     # Percentage Bar
            if not self.stop_plot:
                self.disable_toolbar()

                if self.plot_select:
                    string = (f'Histogram of Single Pixel Energy: {self.params.element}')
                    self.plot_hist(energy_sp, nr_bins=20, string=string)

                else:
                    string = (f'Histogram of Multi Pixel Energy: {self.params.element}')
                    self.plot_hist(energy_mp, nr_bins=20, string=string)
            else:
                self.enable_toolbar()

            if stop:
                self.event.set()
                self.time_frame.after_cancel(self.after_id)
                self.enable_buttons()
                self.energy_sp = energy_sp
                self.energy_mp = energy_mp

                if not self.queue_time.empty():
                    str1, str2, str3 = self.queue_time.get()
                    for i in [str1, str2, str3]:
                        self.update_console(i)

                data_sp, data_mp = [], []

                while not self.queue_data.empty():
                    data = self.queue_data.get()
                    data_sp += data[0]
                    data_mp += data[1]

                self.data_sp = [[[int(i) for i in y] for y in lst] for lst in data_sp]
                self.data_mp = [[[[int(l) for l in i] for i in y] for y in lst] for lst in data_mp]

                if not self.stop_plot:
                    if self.plot_select:
                        if len(energy_sp) != 0:
                            string = ('Histogram of Single Pixel Energy')
                            self.plot_line(energy_sp, nr_bins=1, string=string)

                        elif len(energy_mp) != 0:
                            self.update_console("No Single Pixel Data")
                            string = ('Histogram of Multi Pixel Energy')
                            self.plot_line(energy_mp, nr_bins=1, string=string)

                        else:
                            self.update_console("No Single or Multi Pixel Data")

                    else:
                        if len(energy_mp) != 0:
                            string = ('Histogram of Multi Pixel Energy')
                            self.plot_line(energy_mp, nr_bins=1, string=string)

                        elif len(energy_sp) != 0:
                            self.update_console("No Multi Pixel Data")
                            string = ('Histogram of Single Pixel Energy')
                            self.plot_line(energy_sp, nr_bins=1, string=string)

                        else:
                            self.update_console("No Single or Multi Pixel Data")

        if not stop:
            self.after_id = self.time_frame.after(500, self.update_time_display)


    def load_hot_pixel_map(self):
        """
        Import hot pixel map.

        """
        initdir="C:/Users/cm846/OneDrive - University of Leicester/Python/"
        if self.params.dir_hp:
            initdir = os.path.dirname(os.path.abspath(self.params.dir_hp))
        try:
            filename = askf(initialdir=initdir, defaultextension='.npy',
                                          filetypes=[('Numpy file','*.npy'), ('All files','*.*')])
            if not filename:
                raise FileNotFoundError

        except FileNotFoundError:
            self.update_console("No File Chosen")
            return

        try:
            self.params.hot_pixels = np.load(filename).tolist()
            self.params.dir_hp = filename

        except ValueError:
            self.update_console("Error selecting hot pixel")

        else:
            try:
                self.update_console(f"Imported Hot Pixel Map. Nr: {len(self.params.hot_pixels)}")
                rows = self.params.rows
                cols = self.params.cols
                x = np.zeros((rows*cols), dtype=np.int32)
                x[self.params.hot_pixels] = 1
                x = np.reshape(x, (rows, cols))
                self.show_pic(x, v=[0,1])

            except IndexError:
                self.update_console("Hot Pixel List has out of bound coordinates")


    def show_pic(self, data: np.array, v: bool=None):
        """
        Create new image from data.
        """
        if self.stop_plot:
            return

        if v is None:
            v = [0, np.mean(data) + 20*np.std(data)]

        self.fig.clear()
        p = self.fig.gca()
        p.imshow(data, interpolation = 'none', cmap='hot', vmin=v[0],
                 vmax=v[1])
        # self.fig.supxlabel("IMAGE")
        self.canvas.draw()


    def clear_pic(self):
        """
        Update frame to show blank picture.
        """
        if self.stop_plot:
            return

        self.fig.clear()    # Clear the figure
        self.canvas.draw()  # Update the canvas


    def show_hist(self, arr: np.array, nr_bins: int=50, lims=None):
        """
        Histogram with an automatic fitted Gaussian.
        """
        try:
            self.fig.clear()    # Clear previous figure
            p = self.fig.gca()  # Find the subplot axes
            if lims is not None:
                xlims = lims
                p.set_xlim(xlims)
                arr[arr>xlims[1]] = 0
                arr[arr<xlims[0]] = 0

            data = np.array(arr).flatten()
            mean, sigma = norm.fit(data)
            bins = p.hist(data, bins=nr_bins, density=1, facecolor='green', alpha=0.75)[1]
            bin_counts = norm.pdf(bins, mean, sigma)

            p.plot(bins, bin_counts, 'r--', linewidth=2) # Gaussian Best Fit Line
            p.grid(True)        # Overlay grid
            self.fig.supxlabel("Pixel Energy (ADU)")
            self.fig.supylabel("Normalized Frequency (Percentage %)")
            string = (f'Histogram of Pixel Energy: \u03BC = {np.round(mean, 2)},'
                      f' \u03C3 = {np.round(sigma, 2)}')
            self.fig.suptitle(string)

            self.canvas.draw()  # Update the canvas

        except TypeError:
            self.update_console("TypeError: show_hist function failed")

        except ValueError:
            self.update_console("ValueError: show_hist function failed")


    def plot_line(self, arr, nr_bins, string):
        """
        Plot a line graph

        Parameters
        ----------
        arr : TYPE
            DESCRIPTION.
        nr_bins : TYPE
            DESCRIPTION.
        string : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.fig.clear()    # Clear previous figure
        p = self.fig.gca()  # Find the subplot axes
        data = np.array(arr).flatten()
        nr_events = len(data)
        # data = data[data > 3*self.params.sec_threshold]
        y = np.histogram(data, bins=np.arange(0, np.max(data)+nr_bins, nr_bins))[0]
        c=[np.arange(0, np.max(data)+nr_bins, nr_bins), y]
        p.plot(y, marker='o', markersize=2)

        xlims = [0, 750]
        p.set_xlim(xlims)
        data = p.get_lines()[0].get_xydata()

        # cut out data in xlims window
        data = data[np.logical_and(data[:, 0] >= xlims[0], data[:, 0] <= xlims[1])]

        # rescale y
        p.set_ylim(np.min(data[:, 1]), 1.01*np.max(data[:, 1]))

        p.grid(True)        # Overlay grid
        self.fig.supxlabel("Pixel Value (ADU)")
        self.fig.supylabel("Frequency (Counts)")

        if string is None:
            string = ('Line Graph of X-Ray Energy')

        self.fig.suptitle(string)

        ymax = np.amax(data[:, 1])
        data = np.array(data[:, 1])
        xmax = data.argmax() + xlims[0]

        p.text(0, -0.1, f'Coords: [x: {xmax}, y: {ymax}]',
                 ha='center', va='center', transform = p.transAxes)

        self.fig.legend([f'{nr_events} Total Events'], loc='upper right')

        # scale_x = 1.84496667 / 1000
        scale_x = 1
        # scale_x = 5993/345/1000 # EDITS REQUIRED

        if scale_x != 1:
            self.fig.supxlabel("X-Ray Energy (KeV)")

        ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(np.around(x*scale_x, 3)))
        ax2 = self.fig.gca()
        ax2.xaxis.set_major_formatter(ticks_x)

        p.plot(xmax, ymax, 'r*')
        self.canvas.draw()  # Update the canvas
        if self.save_hist_param is True:
            save_hist_data = askfs(filetypes=[("txt", ".txt")], defaultextension=".txt")
            if save_hist_data == '':
                return
            else:
                with open(save_hist_data, "w") as file:
                    for x in zip(*c):
                        file.write("{0}\t{1}\n".format(*x))
        


    def plot_hist(self, arr, nr_bins=1, string=None, xmin=None, xmax=None, sample=False, save=False, log=False):
        """
        Create histogram of imported data

        Params
        ------------

        df_data: numpy array
            The data for which we wish to create a histogram.

        bins: int
            The number of bins we want in our histogram.

        string: string
            The title of the histogram to display on the plot.

        xmin, xmax, ymax: int
            The values for the range we want to plot on our histogram for the
            x-axis and y-axis
        """
        try:
            self.fig.clear()    # Clear previous figure
            p = self.fig.gca()  # Find the subplot axes
            data = np.array(arr).flatten()
            # print(np.mean(data))
            # print(np.amax(data))
            # print(f'Ratio: {np.amax(data) / np.mean(data)}')
            if sample is False:
                pass
                # data = data[data > 60]
                # xlims = [100, 2000]

            if len(data) == 0:
                raise ValueError

            if xmin is None:
                xmin = 0

            if xmax is None:
                xmax = np.amax(data)

            if sample is True:
                # xmin = np.amin(data)
                # xmax = np.amax(data)
                # xlims = [-100, 100]
                xlims = [xmin, xmax]
                # xlims = [400, 4095]

            n, bins, patches = p.hist(data, bins=np.arange(xmin, xmax+nr_bins, nr_bins), facecolor='green', alpha=0.75, density=0)
            # xlims[0]= 100

            if np.amin(data) < 1:
                xm = 1

            else: 
                xm = np.amin(data)
            

            if log is True:
                p.set_xlim(xm, np.amax(data))
                # print(np.amin(data))
                # rescale y
                p.set_ylim(0.1, 10*np.max(n))
                
                p.set_yscale('log')
                p.set_xscale('log')
            else:
                p.set_xlim(0, 500)
                if xmin == xmax:
                    xmax = xmin + 1
                p.set_xlim(xmin, xmax)
                p.set_ylim(0, 1.01*np.max(n))
            
            
            p.grid(True)        # Overlay grid
            if sample:
                self.fig.supxlabel("Pixel Value (ADU)")
                self.fig.supylabel("Frequency (%)")
            else:
                self.fig.supxlabel("Pixel Energy (ADU)")
                self.fig.supylabel("Frequency (Counts)")

            if string is None:
                string = ('Histogram of X-Ray Energy')

            self.fig.suptitle(string)

            if sample is False:
                self.fig.legend([f'{len(data)}'], loc='upper right')
            
            if self.plot_select:
                scale_x = 1 # 5900/345 # 1
            else:
                scale_x = 5993/345/1000 # EDITS REQUIRED # eV
                # scale_x = scale_x / 3.65 # Mean Energy (convert eV to number of electrons
                # scale_x = scale_x / 0.1 # Divide by exposure time to convert from /0.1s to /s

                # scale_x = 930 / 510 / 3.65 # / 0.0194
            
            scale_x = 1

            if scale_x != 1:
                self.fig.supxlabel("Dark Current (e-/pixel/s)")
                self.fig.supxlabel("Pixel Value (KeV)")

            ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(np.around(x*scale_x, 3)))
            ax2 = self.fig.gca()
            ax2.xaxis.set_major_formatter(ticks_x)

            self.canvas.draw()  # Update the canvas
            
            if save is True:
                # self.fig.savefig("TESTINGSAVEFUNCTON")
                c=[bins, n]
                save_hist_data = askfs(filetypes=[("txt", ".txt")], defaultextension=".txt")
                if save_hist_data == '':
                    return
                else:
                    with open(save_hist_data, "w") as file:
                        for x in zip(*c):
                            file.write("{0}\t{1}\n".format(*x))
            

        except TypeError:
            self.update_console("plot_hist function failed.")

        except ValueError:
            pass


    def new_and_histogram(self, arr, nr_bins=1, string=None, xmin=None, xmax=None):
        """
        Create histogram of imported data
    
        Params
        ------------
    
        df_data: numpy array
            The data for which we wish to create a histogram.
    
        bins: int
            The number of bins we want in our histogram.
    
        string: string
            The title of the histogram to display on the plot.
    
        xmin, xmax, ymax: int
            The values for the range we want to plot on our histogram for the
            x-axis and y-axis
        """
        try:
            self.fig.clear()    # Clear previous figure
            p = self.fig.gca()  # Find the subplot axes
            data = np.array(arr).flatten() 
    
            if len(data) == 0:
                raise ValueError
    
            if xmin is None:
                xmin = 0
    
            if xmax is None:
                xmax = np.amax(data)
    
            n, bins, patches = p.hist(data, bins=np.arange(xmin, xmax+nr_bins, nr_bins), facecolor='green', alpha=0.75, cumulative=True, density=True)
    
            p.set_xlim(1, np.amax(bins))
            p.set_ylim(0.5,     np.max(n))
            
            
            p.grid(True)        # Overlay grid
            self.fig.supxlabel("Pixel Energy (ADU)")
            self.fig.supylabel("Frequency (Counts)")
    
            if string is None:
                string = ('Histogram of X-Ray Energy')
    
            self.fig.suptitle(string)
            
            if self.plot_select:
                scale_x = 1 # 5900/345 # 1
            else:
                scale_x = 1# 930 / 510 / 3.65 # / 0.0194
            
    
            if scale_x != 1:
                # self.fig.supxlabel("Dark Current (e-/pixel/s)")
                self.fig.supxlabel("Pixel Value (KeV)")
    
            ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(np.around(x*scale_x, 3)))
            ax2 = self.fig.gca()
            ax2.xaxis.set_major_formatter(ticks_x)
            p.set_yscale('log')
            p.set_xscale('log')
    
            self.canvas.draw()  # Update the canvas
            
            if self.save_hist_param is True:
                # self.fig.savefig("TESTINGSAVEFUNCTON")
                # print("Attempting Save")
                c=[bins, n]
                save_hist_data = askfs(filetypes=[("txt", ".txt")], defaultextension=".txt")
                if save_hist_data == '':
                    return
                else:
                    with open(save_hist_data, "w") as file:
                        for x in zip(*c):
                            file.write("{0}\t{1}\n".format(*x))
            
    
        except TypeError:
            self.update_console("plot_hist function failed.")
    
        except ValueError:
            pass




    def darkframe(self):
        """
        Import dark frame
        """
        initdir=("C:/Users/cm846/OneDrive - University of Leicester/"
                 "Python/Dark Frames/")
        if self.params.dir_df:
            initdir = os.path.dirname(os.path.abspath(self.params.dir_df))

        try:
            filename = askf(initialdir=initdir, 
                            filetypes=[('All files','*.*'), ('Tiff file','*.tiff'), ('Raw file','*.raw')])
            if not filename:
                if self.params.dark.size != 1:
                    dark = self.params.dark.reshape((self.params.rows, self.params.cols))
                    if pathlib.Path(os.path.basename(self.params.dir_df)).suffix == ".tiff":
                        lims=[0, 4095]
    
                    else: 
                        lims=None
    
                    self.show_pic(dark, v=lims)

                raise FileNotFoundError
            
            path = pathlib.Path(filename)

            if path.suffix == ".raw":
                self.is_tiff_file = False
                # self.params.rows = 2040 # m
                # self.params.cols = 2048 # n
                self.params.rows = 4112 # m
                self.params.cols = 4154 # n
                dark = np.memmap(filename, dtype='>u2').astype(int)
                x = dark.reshape((self.params.rows, self.params.cols))
                # print(x.shape)
                # print(self.params.rows)
                # print(self.params.cols)
                lims=None

            elif path.suffix == ".tiff":
                self.is_tiff_file = True
                lims=[0, 4095]
                x = imread(filename)
                x = x[::self.params.scale, ::self.params.scale]
                

                self.params.rows = x.shape[0]
                self.params.cols = x.shape[1]
                dark = x.reshape(x.size).astype(int)
                print(f'Dark Frame Max Value: {np.amax(dark)}')
                print(f'Min Value: {np.amin(dark)}')
                try:
                    index2 =  ["Left", "Right", "LL", "ML", "MR", "RR", "All"].index(self.params.LR)

                except: pass

                else:
                    LRlist1 = [2, 2, 4, 4, 4, 4]
                    LRlist2 = [0, 1, 0, 1, 2, 3]
                    if index2 != 6: x = np.split(x, LRlist1[index2], axis=1)[LRlist2[index2]]
                    if index2 == 3: x = x[:, 28:108] # Reduce Europa Region


                try:
                    index3 =  ["Q1-Q3", "Q1", "Q2", "Q3", "Q4", "All"].index(self.params.roi)

                except: pass

                else:
                    list1 = [0, 0, 1, 2, 3, 4]
                    list2 = [3, 1, 2, 3, 4, 5]
                    if index3 != 5: x = np.concatenate(np.split(x, 4)[list1[index3]:list2[index3]])
                
                # Ratio of Bloom to Average Region
                dim = int(2048 / int(self.params.scale))
                v1 = np.mean(dark.reshape((dim, dim))[256:268, 0:11])
                v2 = np.mean(dark.reshape((dim, dim))[256:268, 500:511])
                self.update_console(f'Ratio of Bloom to Avg: {np.around(v2/v1, 3)}')
                    
                
            else: 
                raise ValueError

            self.params.dark = dark
            self.params.dir_df = filename
            self.show_pic(x, v=lims)
            self.update_console(f'Mean: {np.around(np.mean(self.params.dark), 1)}. '
                                f'Std: {np.around(np.std(self.params.dark), 1)}.')
            
        except FileNotFoundError:
            self.update_console("No File Chosen")


    def sample_data(self):
        """
        Import sample X-Ray Frame
        """
        if self.stop_plot:
            return

        try:
            if self.params.dark.shape == ():
                raise ValueError
            dark = self.params.dark
            filename = askf()

            if not filename:
                raise FileNotFoundError
                
            
            path = pathlib.Path(filename)
                
            if path.suffix == ".raw":
                arr = np.memmap(filename, dtype='>u2').astype(int)
                arr = arr.flatten()
                print(f'Dark dims {dark.shape}')
                blank = np.zeros(arr.size, int)
                blank[self.params.hot_pixels] = 1
                blank = blank.astype(int)
                # arr = arr.reshape((self.params.rows, self.params.cols))

            elif path.suffix == ".tiff":
                x = imread(filename)
                scale = self.params.scale
                x = x[::scale, ::scale]
                self.update_console(f'File: {os.path.basename(filename)}')
                blank = np.zeros(x.size, int)
                blank[self.params.hot_pixels] = 1
                blank = blank.reshape(x.shape)
                dark = self.params.dark.reshape((self.params.rows, self.params.cols))

                # Left / Right Split
                try:
                    index2 =  ["Left", "Right", "LL", "ML", "MR", "RR", "All"].index(self.params.LR)

                except: pass

                else:
                    LRlist1 = [2, 2, 4, 4, 4, 4]
                    LRlist2 = [0, 1, 0, 1, 2, 3]
                    if index2 != 6:
                        x = np.split(x, LRlist1[index2], axis=1)[LRlist2[index2]]
                        blank = np.split(blank, LRlist1[index2], axis=1)[LRlist2[index2]]
                        dark = np.split(dark, LRlist1[index2], axis=1)[LRlist2[index2]]


                # Quarter Split
                try:
                    index3 =  ["Q1-Q3", "Q1", "Q2", "Q3", "Q4", "All"].index(self.params.roi)

                except: pass

                else:
                    list1 = [0, 0, 1, 2, 3, 4]
                    list2 = [3, 1, 2, 3, 4, 5]
                    if index3 != 5:
                        x = np.concatenate(np.split(x, 4)[list1[index3]:list2[index3]])
                        blank = np.concatenate(np.split(blank, 4)[list1[index3]:list2[index3]])
                        dark = np.concatenate(np.split(dark, 4)[list1[index3]:list2[index3]])

                # Change arrays into correct format (1D)
                dark = dark.flatten()
                arr = x.reshape(x.size).astype(int)
                blank = blank.reshape(x.size).astype(int)

            else: 
                raise ValueError

            arr = np.subtract(arr, dark)
            arr[blank[blank>0].tolist()] == 0

            if not arr.any():
                raise RuntimeWarning


            # Create histogram of data [Display on frame]
            xmi = np.amin(arr)
            xma = np.amax(arr)
            if self.plot_select:
                self.plot_hist(arr, nr_bins=1, xmin=xmi, xmax=xma, sample=True,
                               string="Histogram of Pixel Values from Dark Subtracted Frames (BSI Non-OBF)",
                               save=self.save_hist_param)
            else:
                self.new_and_histogram(arr, nr_bins=1, xmin=xmi, xmax=xma, string="New and Improved")
            

        except FileNotFoundError:
            self.update_console("No File Chosen")

        except ValueError:
            self.update_console("No Dark Frame Imported")

        except RuntimeWarning:
            self.update_console("Selected data file is identical to dark frame")


    def data_viewer(self, data_sp, data_mp, nr, files, params, expand=False):
        """
        Show images of data for each frame

        """
        self.fig.clear()
        rows, cols, searchgrid, hotpixels = params
        x_1, x_2, y_1, y_2 = searchgrid
        arr = np.zeros((rows*cols), int)
        for coords, vals in data_sp[nr]: # Single pixels
            arr[coords] = vals

        for coords, vals in data_mp[nr]: # Multi pixels
            arr[coords] = vals
            
        self.update_console(f'SP: {len(data_sp[nr])}. MP: {len(data_mp[nr])}')
        arr = arr.reshape((rows, cols))
        arr = arr[y_1:y_2+1, x_1:x_2+1]
        
        
        if self.is_tiff_file:
            x = imread(files[nr])
            scale = self.params.scale
            x = x[::scale, ::scale]
            data = x.reshape(x.size).astype(int)
            x = x.astype(int)
            
        else:
            data = np.memmap(files[nr], '>u2').astype(int)
            x = data.reshape((self.params.rows, self.params.cols))
            data = data.reshape(data.size)



        
        dark = self.params.dark.reshape(x.shape)
        x = np.subtract(x, dark)
        
        # new = x
        # test = np.zeros((512, 512))
        
        # for i in range(new.shape[0]):
        #     t = t_spare = new[i, :]
            
        #     yhat2 = savgol_filter(t, 64, 1)
        #     yhat2 = yhat2.astype(int)

        #     flat = np.subtract(t, yhat2)

        #     f1 = flat < -5*np.std(flat)
        #     f2 = flat > 5*np.std(flat)

        #     t_spare[f1] = flat[f1]
        #     t_spare[f2] = flat[f2]

        #     yhat3 = savgol_filter(t_spare, 64, 1)
        #     yhat3 = yhat3.astype(int)

        #     new_flat = np.subtract(t, yhat3)
        #     new_flat = new_flat.reshape((1, -1))

        #     test[i,:] = new_flat
            
        # test = test.astype(int)
        # data2 = test.flatten()
        
        if self.is_tiff_file:
            for i in range(x.shape[0]):
                    diff = x[i, 256:512]
                    heights, bins= np.histogram(diff, bins = np.arange(np.amin(diff), np.amax(diff)+1, 1))
                    heights = heights.astype(int)
                    bins = np.delete(bins, len(bins)-1)
                    y_values, temp_l, temp_r = [], [], []
                    y_values = heights.tolist()
                    peak_height = max(y_values)
                    mean = bins[y_values.index(peak_height)]
                    x[i,256:512] = x[i,256:512] - mean
                    
            for i in range(x.shape[0]):
                    diff = x[i, 0:256]
                    heights, bins= np.histogram(diff, bins = np.arange(np.amin(diff), np.amax(diff)+1, 1))
                    heights = heights.astype(int)
                    bins = np.delete(bins, len(bins)-1)
                    y_values, temp_l, temp_r = [], [], []
                    y_values = heights.tolist()
                    peak_height = max(y_values)
                    mean = bins[y_values.index(peak_height)]
                    x[i,0:256] = x[i,0:256] - mean
            
            
        
        data2 = x.flatten()
                
            
        # data2 = np.subtract(data, self.params.dark)
        
        

        data = data.reshape((rows, cols))[y_1:y_2+1, x_1:x_2+1]
        data2 = data2.reshape((rows, cols))[y_1:y_2+1, x_1:x_2+1]

        ax1 = self.fig.add_subplot(221)
        ax2 = self.fig.add_subplot(222, sharex=ax1, sharey=ax1)
        ax3 = self.fig.add_subplot(223, sharex=ax1, sharey=ax1)
        ax4 = self.fig.add_subplot(224, sharex=ax1, sharey=ax1)
        
        if self.is_tiff_file:
            maxs = [4095, 90, 45]
        else:
            maxs = [450, 90, 45]

        ax1.imshow(data, interpolation = 'none', cmap='hot', vmin=0, vmax=maxs[0])
        ax2.imshow(data2, interpolation = 'none', cmap='hot', vmin=0, vmax=maxs[1])
        ax3.imshow(arr, interpolation = None, cmap='hot', vmin=0, vmax=maxs[2])


        arr = np.zeros((rows*cols), int)
        for coords, vals in data_sp[nr]: # Single pixels
            arr[coords] = 2

        for coords, vals in data_mp[nr]: # Multi pixels
            arr[coords] = 2

        arr[hotpixels] = 1
        arr = arr.reshape((rows, cols))
        arr = arr[y_1:y_2+1, x_1:x_2+1]
        v = np.mean(arr) + 20*np.std(arr)
        ax4.imshow(arr, interpolation = 'none', cmap='hot', vmin=0, vmax=v)

        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_yticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.setp(ax4.get_yticklabels(), visible=False)
        plt.multi = MultiCursor(self.canvas, (ax1, ax2, ax3, ax4), color='w',
                                lw=0.5, horizOn=True, vertOn=True)
        self.canvas.draw()

        if expand is True:
            plt.close()
            rows, cols, searchgrid, hotpixels = params
            x_1, x_2, y_1, y_2 = searchgrid
            arr = np.zeros((rows*cols), int)
            for coords, vals in data_sp[nr]: # Single pixels
                arr[coords] = vals

            for coords, vals in data_mp[nr]: # Multi pixels
                arr[coords] = vals
            arr = arr.reshape((rows, cols))
            arr = arr[y_1:y_2+1, x_1:x_2+1]

            
            if self.is_tiff_file:
                x = imread(files[nr])
                scale = self.params.scale
                x = x[::scale, ::scale]
                data = x.reshape(x.size).astype(int)

            else: # Raw Files
                data = np.memmap(files[nr], '>u2').astype(int)

            data2 = np.subtract(data, self.params.dark)

            data = data.reshape((rows, cols))[y_1:y_2+1, x_1:x_2+1]
            data2 = data2.reshape((rows, cols))[y_1:y_2+1, x_1:x_2+1]

            ext_fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharex=True, sharey=True)
            ax1.imshow(data2, interpolation = None, cmap='hot', vmin=0, vmax=90)
            ax2.imshow(arr, interpolation = None, cmap='hot', vmin=0, vmax=25)

            arr = np.zeros((rows*cols), int)

            for coords, vals in data_sp[nr]: # Single pixels
                arr[coords] = 2

            for coords, vals in data_mp[nr]: # Multi pixels
                arr[coords] = 2

            arr[hotpixels] = 1
            arr = arr.reshape((rows, cols))
            arr = arr[y_1:y_2+1, x_1:x_2+1]
            v = np.mean(arr) + 20*np.std(arr)
            ax3.imshow(arr, interpolation = None, cmap='hot', vmin=0, vmax=v)
            plt.setp(ax2.get_yticklabels(), visible=False)
            plt.setp(ax3.get_yticklabels(), visible=False)
            plt.multi2 = MultiCursor(ax1.figure.canvas , (ax1, ax2, ax3), color='w',
                                    lw=0.5, horizOn=True, vertOn=True)
            manager = plt.get_current_fig_manager()
            manager.window.showMaximized() # manager.full_screen_toggle()
            ax1.set_aspect(aspect=1, share=True)
            plt.subplots_adjust(left=0.025, bottom=0.01, right=0.99, top=0.99, wspace=0.01, hspace=0.01)
            plt.show()


    def df_gui(self, win):
        """
        Opens a new Tkinter GUI to create a dark frame
        """
        win.withdraw()
        self.df_window = tkr.Toplevel() # Create New Tkinter Interface Frame (TopLevel())
        def confirm_exit():
            win.deiconify()
            self.df_window.destroy()
            
        button_quit = tkr.Button(self.df_window, text='Quit', width=50, command=confirm_exit)
        self.df_win = DFWindow(self.df_window, win, button_quit)  # Use GUI Settings from darkframegui.py
        self.df_window.title('Dark Frame Creator')  # Select GUI name
        self.df_window.geometry("550x550+10+10") # Choose window geometry settings
        self.df_window.protocol('WM_DELETE_WINDOW', confirm_exit)


    def hp_gui(self, win):
        """
        Opens a new Tkinter GUI to create a hot pixel map

        """
        win.withdraw()
        self.hp_window = tkr.Toplevel() # Create New Tkinter Interface Frame (TopLevel())
        self.hp_win = HPWindow(self.hp_window, win)  # Use GUI Settings from darkframegui.py
        self.hp_window.title('Hot Pixel Map Creator')  # Select GUI name
        self.hp_window.geometry("420x300+10+10") # Choose window geometry settings

        def confirm_exit():
            win.deiconify()
            self.hp_window.destroy()

        self.hp_window.protocol('WM_DELETE_WINDOW', confirm_exit)


    def params_gui(self, win, params):
        """
        Opens a new Tkinter GUI to create a hot pixel map

        """
        # win.withdraw()
        self.params_window = tkr.Toplevel() # Create New Tkinter Interface Frame (TopLevel())
        def confirm_exit():
            self.params_window.destroy()
            self.update_params()

        button_quit = tkr.Button(self.params_window, text='Quit', width=20, command=confirm_exit)
        self.params_win = ParamsWindow(self.params_window, win, params, button_quit)  # GUI from paramsgui.py
        self.params_window.title('Parameter Editor')  # Select GUI name
        self.params_window.geometry("550x550+10+10") # Choose window geometry settings
        self.params_window.protocol('WM_DELETE_WINDOW', confirm_exit)


    def calib_gui(self, win):
        """
        Opens a new Tkinter GUI to create a calibration curve from the data
        """
        self.calib_window = tkr.Toplevel() # Create New Tkinter Interface Frame (TopLevel())
        def confirm_exit():
            self.calib_window.destroy()

        button_quit = tkr.Button(self.calib_window, text='Quit', width=20, command=confirm_exit)
        self.calib_win = CalibWindow(self.calib_window, win, button_quit, self.fig, self.canvas)  # GUI from calibgui.py
        self.calib_window.title('Parameter Editor')  # Select GUI name
        self.calib_window.geometry("550x550+10+10") # Choose window geometry settings
        self.calib_window.protocol('WM_DELETE_WINDOW', confirm_exit)


class Startup:
    """
    Creates Main GUI window
    """
    def __init__(self):
        self.window = tkr.Tk() # Create Tkinter Frame
        self.mywin = MyWindow(self.window) # Use MyWindow GUI Settings from GUI.py
        self.window.title('X-Ray Fluorescence Detector Software') # Select GUI name
        self.window.iconbitmap('UoL.ico')
        self.window.geometry("1550x1000+10+10") # Choose Window Geometry
        self.window.mainloop()


if __name__ == '__main__':
    start = Startup()
    
    x = start.mywin.data_sp
    y = start.mywin.data_mp
    yy = start.mywin.energy_mp
    xx = start.mywin.energy_sp
