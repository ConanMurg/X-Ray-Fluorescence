# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 11:17:03 2023

@author: cm846
"""
# import tkinter as tkr
from mttkinter import mtTkinter as tkr
from tkinter import ttk
from tkinter.filedialog import askopenfilename as askf
from tkinter.filedialog import asksaveasfilename as askfs
from tkinter.filedialog import askdirectory as askd
import os
import glob
import time
import datetime
import pathlib
import numpy as np
from natsort import natsorted
from tifffile import imread
from threading import Thread

__all__ = ['HPWindow']

class HPWindow:
    """
    Description:
        Creates a Tkinter GUI for importing data and identifying
        hot pixels on a CCD detector.

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
    def __init__(self, win, nwin):
        self.thresh1 = 5000
        self.thresh2 = 15
        self.chk = False
        self.is_tiff_file = False

        # Create Buttons
        avg_df_button = tkr.Button(win, command = self.dark_frame) # Import averaged dark frame
        avg_df_button.config(text='Averaged Dark Frame', width = 20)
        data_button = tkr.Button(win, command = lambda: self.check_params(win))
        data_button.config(text='Other Dark Frames', width = 20) # Select dark frame directory
        save = tkr.Button(win, command = self.save_hotpixels) # Save button
        save.config(text='Save', width = 20)
        button_quit = tkr.Button(win, command = lambda: self.win_quit(win, nwin)) # Quit button
        button_quit.config(text='Quit', width = 20)
        lbl1 = tkr.Label(win, text='Threshold 1 (DF): ')
        lbl2 = tkr.Label(win, text='Threshold 2 (DSDF): ')
        countlbl = tkr.Label(win, text='Hotpixels found') # Hotpixel count display
        self.text_1 = tkr.Entry(win, bd=3, width = 20)
        self.text_2 = tkr.Entry(win, bd=3, width = 20)
        self.text = tkr.Entry(win, bd=3, width = 20, state='readonly') # Hotpixel count display

        # Position Buttons in grid
        avg_df_button.grid(row = 3, column = 1, padx=20, pady=10)
        data_button.grid(row = 3, column = 2, padx=20, pady=10)
        save.grid(row = 7, column = 1, padx=20, pady=30)
        button_quit.grid(row = 7, column = 2, padx=20, pady=30)
        lbl1.grid(row = 1, column = 1, padx=20, pady=10)
        lbl2.grid(row = 2, column = 1, padx=20, pady=10)
        countlbl.grid(row = 5, column = 1, padx=20, pady=10)
        self.text_1.grid(row = 1, column = 2, padx=20, pady=10)
        self.text_2.grid(row = 2, column = 2, padx=20, pady=10)
        self.text.grid(row = 5, column = 2, padx=20, pady=10)
        self.my_progress = ttk.Progressbar(win, orient=tkr.HORIZONTAL, length=330,
                                           mode = 'determinate')
        self.my_progress.grid(row= 6, column = 1, columnspan = 2, padx=5, pady=5)
        self.text_1.insert(0, self.thresh1)
        self.text_2.insert(0, self.thresh2)


    @property
    def thresh1(self):
        """
        Returns thresh1 value.
        """
        return self.__thresh1

    @thresh1.setter
    def thresh1(self, var):
        """
        Setter for thresh1. Ensures value is numeric and positive.
        """
        if isinstance(var, (int, float)) and var > 0:
            self.__thresh1 = var

    @property
    def thresh2(self):
        """
        Returns thresh2 value.
        """
        return self.__thresh2

    @thresh2.setter
    def thresh2(self, var):
        """
        Setter for thresh2. Ensures value is numeric and positive.
        """
        if isinstance(var, (int, float)) and var > 0:
            self.__thresh2 = var


    def win_quit(self, win, nwin):
        """
        Closes the GUI window, and reopens the main GUI.

        Parameters
        ----------
        win : Tkinter Frame
            The Tkinter frame in which the GUI is running.

        nwin : Tkinter Frame.
            The main Tkinter frame which created this frame..

        """
        nwin.deiconify()
        win.destroy()


    def counter(self, nr_hot_pixels):
        """
        Displays the number of hot pixels counted on the Tkinter interface.
        """
        self.text.config(state='normal')
        self.text.delete(0, tkr.END)
        self.text.insert(0, nr_hot_pixels)
        self.text.config(state='readonly')


    def dark_frame(self):
        """
        Import the dark frame.

        Returns
        -------
        int
            Error code.

        """
        initdir = "C:/Users/cm846/OneDrive - University of Leicester/Python/Theseus_QE/Theseus_QE/Theseus_QE/Non-OBF 30C"
        try:
            filename = askf(initialdir = initdir, defaultextension='.tiff',
                            filetypes=[('Tiff file','*.tiff'), ('Raw file','*.raw'),
                                       ('All files','*.*')])
            if not filename:
                raise ValueError

            path = pathlib.Path(filename)

            if path.suffix == ".raw":
                self.darkframe = np.fromfile(filename, dtype='>u2').astype(np.int32)

            else:
                self.is_tiff_file = True
                x = imread(filename)
                x = x[::4, ::4]
                # x = np.split(x, 4, axis=1)[3]
                # x = np.split(x, 4)[2]
                
                # all_rows = [76, 80, 37, 13, 29, 56, 41, 66, 105, 84, 31, 362, 322]
                # for i in all_rows:
                #     x[i][0:219] = 0
                #     x[i][256:474] = 0
                # plt.imshow(x)
                self.darkframe = x.reshape(x.size).astype(int)
            
            self.dark = 1
            print("Imported Dark Frame")

        except ValueError:
            print("No File Chosen")


    def check_params(self, win):
        """
        Checks that all the necessary parameters are correct before beginning
        hot pixel identification map.

        Parameters
        ----------
        win : Tkinter Frame
            The Tkinter frame in which the GUI is running.

        Returns
        -------
        int
            Error code.

        """
        try:
            if not self.dark: # Return error message if Dark Frame has not been selected
                print("Dark Frame Not Selected")
                raise FileNotFoundError

            initdir="C:/Users/cm846/OneDrive - University of Leicester/Python/Theseus_QE/Theseus_QE/Theseus_QE/Non-OBF 30C"
            directory = askd(initialdir = initdir)

            if not directory: # Return error message if no directory is selected
                print("No Directory Selected")
                raise FileNotFoundError
            
            if self.is_tiff_file:
                filenames = natsorted(glob.glob(os.path.join(directory, '*.tiff')))

            else:
                filenames = natsorted(glob.glob(os.path.join(directory, '*.raw')))

            if len(filenames) == 0: # Return error message if no files are found in directory
                raise ValueError

            txt_1 = str(self.text_1.get())
            if txt_1.isdigit():
                self.thresh1 = int(txt_1)

            txt_2 = str(self.text_2.get())
            if txt_2.isdigit():
                self.thresh2 = int(txt_2)

            self.text_1.delete(0, tkr.END)
            self.text_2.delete(0, tkr.END)
            self.text_1.insert(tkr.END, self.thresh1)
            self.text_2.insert(tkr.END, self.thresh2)
            worker = Thread(target = self.hot_pixel_finder,
                            args=(win, filenames, self.is_tiff_file))
            worker.start()
            # self.hot_pixel_finder(win, filenames)

        except ValueError:
            print("Error Importing .raw Files")
            print("ValueError")

        except FileNotFoundError:
            print("FileNotFoundError")


    def hot_pixel_finder(self, win, filenames, is_tiff_file):
        """
        Identifies any hot pixels in a set of dark frames. Requires an
        averaged Dark Frame.
            1. Identify any pixels above a threshold in the Averaged Dark Frame.
            2. Identify any pixels above a threshold in each dark frame after
                averaged Dark Frame is subtracted.

        Saves the hot pixel map to a npy file

        Parameters
        ----------
        win : Tkinter Frame.
            The Tkinter frame in which the GUI is running.

        filenames : list.
            Natsorted (alphabetic) ordered list.

        Returns
        -------
        Saves the hot pixel map to a npy file.

        """
        try:
            if not self.dark:
                raise FileNotFoundError

            start = time.time()
            hot_pix = []
            hot_pix = np.nonzero(self.darkframe > self.thresh1)[0].tolist()
            filecount = 1
            prev = time.time()

            for f in filenames:
                if time.time() - prev > 1: # Update progress bar every second
                    prev = time.time()
                    self.my_progress['value'] = filecount/len(filenames) * 100
                    win.update_idletasks()

                if is_tiff_file:
                    x = imread(f)
                    x = x[::4, ::4]
                    
                    # x = np.split(x, 4, axis=1)[0]
                    # x = np.split(x, 4)[2]
                    
                    # if self.params.LR == "LL":
                    #     x = np.split(x, 4, axis=1)[0]
               
                    # if self.params.LR == "ML":
                    #     x = np.split(x, 4, axis=1)[1]
                    #     x = x[:, 28:108] # REDUCE EUROPA REGION
                        
                    # if self.params.LR == "MR":
                    #     x = np.split(x, 4, axis=1)[2]
               
                    # if self.params.LR == "RR":
                    #     x = np.split(x, 4, axis=1)[3]

                    # if self.params.roi == "Q1-Q3":
                    #     x = np.concatenate(np.split(x, 4)[0:3])

                    # if self.params.roi == "Q1":
                    #     x = np.split(x, 4)[0]

                    # if self.params.roi == "Q2":
                    #     x = np.split(x, 4)[1]

                    # if self.params.roi == "Q3":
                    #     x = np.split(x, 4)[2]

                    # if self.params.roi == "Q4":
                    #     x = np.split(x, 4)[3]
                        
                    
                    
                    # all_rows = [76, 80, 37, 13, 29, 56, 41, 66, 105, 84, 31, 362, 322]
                    # for i in all_rows:
                    #     x[i][0:219] = 0
                    #     x[i][256:474] = 0
                    # del_rows = [[76], [80], [], [37], [13], [29], [], [], [56],
                    #             [41, 66, 105], [], [], [84], [31, 362], [], [],
                    #             [322], []]
                    # t = int(os.path.splitext(os.path.basename(f))[0])-1
                    # if del_rows[t] != []:
                    #     for i in del_rows[t]:
                    #         x[i][0:219] = self.ddf[i][0:219]
                    #         x[i][256:474] = self.ddf[i][256:474]
                    arr = x.reshape(x.size).astype(int)

                else:
                    arr = np.fromfile(f, dtype='>u2').astype(np.int32) # Import file

                dsdf = np.subtract(arr, self.darkframe)
                
                dsdf = dsdf.reshape(x.shape)
                
                  
                for i in range(dsdf.shape[0]):
                        diff = dsdf[i, 256:512]
                        heights, bins= np.histogram(diff, bins = np.arange(np.amin(diff), np.amax(diff)+1, 1))
                        heights = heights.astype(int)
                        bins = np.delete(bins, len(bins)-1)
                        y_values = []
                        y_values = heights.tolist()
                        peak_height = max(y_values)
                        mean = bins[y_values.index(peak_height)]
                        dsdf[i,256:512] = dsdf[i,256:512] - mean
                        
                for i in range(dsdf.shape[0]):
                        diff = dsdf[i, 0:256]
                        heights, bins= np.histogram(diff, bins = np.arange(np.amin(diff), np.amax(diff)+1, 1))
                        heights = heights.astype(int)
                        bins = np.delete(bins, len(bins)-1)
                        y_values = []
                        y_values = heights.tolist()
                        peak_height = max(y_values)
                        mean = bins[y_values.index(peak_height)]
                        dsdf[i,0:256] = dsdf[i,0:256] - mean
                
                dsdf = dsdf.flatten()
                # print(np.mean(dsdf))
                # print(len(np.nonzero(dsdf >= self.thresh2)[0]))
                hot_pix += np.nonzero(dsdf >= self.thresh2)[0].tolist()
                filecount += 1

        except FileNotFoundError:
            print("Dark Frame not imported.")

        else:
            hot_pix = list(set(hot_pix)) # Only keeps unique values)
            self.counter(len(hot_pix))
            self.hotpixels = hot_pix
            self.chk = True

            self.my_progress['value'] = 100
            win.update_idletasks()
            print("Time Taken: ", str(datetime.timedelta(seconds=int(time.time() - start))))
            
            # hps = np.loadtxt("G400_TVISA_HotPixelList_V1.txt", usecols=(1), dtype =int).tolist()
            # intersect = set(hot_pix).intersection(hps)
            # print(f'Mel: {len(hps)}. Mine: {len(hot_pix)}. Intersect: {len(intersect)}')
            return hot_pix


    def save_hotpixels(self):
        """
        Saves the hotpixels into the specified npy file.

        """
        initdir = os.path.dirname(os.path.realpath(__file__))
        f = askfs(filetypes=[("npy", ".npy")], defaultextension=".npy",
                                     initialdir=initdir)
        # save_dir = "C:/Users/cm846/OneDrive - University of Leicester/Python/Dark Frames/hotpixellist.npy"
        if self.chk:
            np.save(f, self.hotpixels)