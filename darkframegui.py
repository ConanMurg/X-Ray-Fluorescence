# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 10:11:49 2022
Python Code for Handling Detector Data
University of Leicester
School of Physics and Astronomy

@author: Conan
"""
import os
import glob
import numpy as np
import tkinter as tkr
from tkinter.filedialog import asksaveasfilename as askfs
from tkinter.filedialog import askdirectory as askd
from tifffile import imread, imsave
from natsort import natsorted

__all__ = ['DFWindow']

class DFWindow:
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
    def __init__(self, win, nwin, b_quit):
        # Create variables to determine if data has been imported and averaged yet
        self.data = 0
        self.is_tiff_file = False
        # Create labels and textboxes for users to select and see their inputs
        self.lbl1 = tkr.Label(win, text='File Folder')
        self.lbl2 = tkr.Label(win, text='Pixels (x)')
        self.lbl3 = tkr.Label(win, text='Pixels (y)')
        self.text_1 = tkr.Text(win, bd=3, width = 35, height = 3)
        self.text_2 = tkr.Entry(win, bd=3, width = 20)
        self.text_3 = tkr.Entry(win, bd=3, width = 20)
        self.button_1 = tkr.Button(win, text='Choose Folder', command = self.sel_dir, width=20)
        self.button_2 = tkr.Button(win, text='Create Dark Frame', command = self.start_import, width=20)
        self.button_3 = tkr.Button(win, text='Save Dark Frame', command = self.saving_df, width=20)

        # Set default x, y values for number of pixels
        self.defnum1 = 2040
        self.defnum2 = 2048
        self.num1 = self.defnum1
        self.num2 = self.defnum2

        # Set default input and output directories
        self.defaultdir = 'C:/Users/Conan/OneDrive - University of Leicester/Python/Dark Frames/'
        self.defaultoutdir = 'C:/Users/Conan/OneDrive - University of Leicester/Python/Dark Frames/'
        self.directory = self.defaultdir
        self.dir = self.defaultdir
        self.filetype = 0
        self.df_data = 0

        # Create read only textbox to display number of files.
        self.count = tkr.Entry(win, bd=3, width = 35)
        self.count.config(state='readonly')

        # Create dropdown box for filetype
        self.options = ["Tiff", "Raw"]
        self.clicked = tkr.StringVar()
        self.clicked.set( "Raw" ) # Default value is Raw
        self.drop = tkr.OptionMenu(win , self.clicked , *self.options)

        # Create label for dropdown box
        self.label = tkr.Label(win, text = "Filetype")
        
        # Select label and textbox locations in GUI
        self.lbl1.grid(row = 1, column = 1,  padx=20, pady=5, sticky='w')
        self.text_1.grid(row = 1, column = 2,  padx=20, pady=5, sticky='w')
        self.button_1.grid(row = 2, column = 1,  padx=20, pady=5, sticky='w')
        self.count.grid(row = 2, column = 2,  padx=20, pady=5, sticky='w')
        self.lbl2.grid(row = 3, column = 1,  padx=20, pady=5, sticky='w')
        self.text_2.grid(row = 3, column = 2,  padx=20, pady=5, sticky='w')
        self.lbl3.grid(row = 4, column = 1,  padx=20, pady=5, sticky='w')
        self.text_3.grid(row = 4, column = 2,  padx=20, pady=5, sticky='w')
        self.label.grid(row = 5, column = 1,  padx=20, pady=5, sticky='w')
        self.drop.grid(row = 5, column = 2,  padx=20, pady=5, sticky='w')
        self.button_2.grid(row = 6, column = 1,  padx=20, pady=5, sticky='w')
        self.button_3.grid(row = 7, column = 1,  padx=20, pady=5, sticky='w')
        b_quit.grid(row = 8, column = 1, columnspan=2, padx=5, pady=5, sticky='w')


    def sel_dir(self):
        """
        Function which opens file explorer to select directory
        and display the selected directory into textbox.
        """
        self.text_1.delete('1.0', tkr.END)
        self.directory = askd()
        self.text_1.insert(tkr.END, self.directory)


    def chk_dir(self):
        """ 
        Function which checks the directory selected by the user. If
        no directory has been selected, the default directory is
        chosen.
        """
        if self.text_1.get("1.0",'end-1c') == '':
            self.text_1.insert(tkr.END, self.defaultdir)
        self.dir = self.text_1.get("1.0",'end-1c')
        return self.dir


    def chk_num1(self):
        """
        Function which checks the x-value for number of pixels in the detector
        data, selected by the user's input. If no value has been selected,
        the default value (2040) is chosen.
        """
        if self.text_2.get() == '':
            self.text_2.insert(tkr.END, self.defnum1)
        return int(self.text_2.get())


    def chk_num2(self):
        """
        Function which checks the y-value for number of pixels in the detector
        data, selected by the user's input. If no value has been selected,
        the default value (2048) is chosen.
        """
        if self.text_3.get() == '':
            self.text_3.insert(tkr.END, self.defnum2)
        return int(self.text_3.get())


    def start_import(self):
        """
        Imports data from the user's chosen directory .
            (function: chk_dir())
        Data dimensions are specified by num1 and num2 provided from user.
            (functions: chk_num1() and chk_num2())
        Imports data of type 'Raw' or 'Tiff' as selected by user.
            (function: chk_type())
        If no data is imported from directory, error line printed into console
        and textbox.
            (function: nr_of_files())
        Average each pixel from array of imported data.
        """
        directory = self.directory
        self.num1 = self.chk_num1()
        self.num2 = self.chk_num2()
        try:
            count = 0
            if self.clicked.get() == 'Tiff':
                filenames = natsorted(glob.glob(os.path.join(directory, '*.tiff')))
    
                if len(filenames) == 0: # Return error message
                    raise ValueError

                x = imread(filenames[0])
                self.shape = x.shape
                sum_init = x.reshape(x.size).astype(int)
                placeholder = np.zeros((2, len(sum_init)), dtype = np.uint32)

                for f in filenames:
                    x = imread(f)
                    data = x.reshape(x.size).astype(int)
                    placeholder[1] = data
                    placeholder[0] =  np.einsum('...ij->...j', placeholder) 
                    count += 1

                data  = placeholder[0] / count
                self.df_data = np.around(data).astype(int)
                self.data = 1

            else:
                filenames = natsorted(glob.glob(os.path.join(directory, '*.raw')))
    
                if len(filenames) == 0: # Return error message
                    raise ValueError

                sum_init = np.fromfile(filenames[0], dtype='>u2')
                placeholder = np.zeros((2, len(sum_init)), dtype = np.uint32)
                
                for f in filenames:
                    data = np.fromfile(f, dtype='>u2')
                    placeholder[1] = data
                    placeholder[0] =  np.einsum('...ij->...j', placeholder) 
                    count += 1
                    
                data  = placeholder[0] / count

                self.df_data = np.around(data).astype(int)
                self.data = 1

            self.count.config(state='normal')
            self.count.delete(0, tkr.END)
            self.count.insert(tkr.END, count)
            self.count.config(state='readonly')
        
        except Exception:
            self.data = 0
            self.count.config(state='normal')
            self.count.delete(0, tkr.END)
            self.count.insert(tkr.END, "Error importing files")
            self.count.config(state='readonly')


    def saving_df(self):
        """
        Save dark frame to file.
        """
        if not self.data:
            return

        if self.clicked.get() == 'Tiff':
            initdir = ""
            f = askfs(filetypes=[("tiff file", ".tiff")],
                      defaultextension=".tiff", initialdir=initdir)

            if f is None:
                print("File Name Required to Save Dark Frame")
                return
        
            data = self.df_data.reshape(self.shape).astype(np.uint16)
            imsave(f, data)
    
        else:
            initdir = ""
            f = askfs(filetypes=[("raw file", ".raw")],
                      defaultextension=".raw", initialdir=initdir)

            if f is None:
                print("File Name Required to Save Dark Frame")
                return

            self.df_data = self.df_data.astype(np.uint16)
            self.df_data = self.df_data.byteswap(True)
            self.df_data.astype('uint16').tofile(f)
