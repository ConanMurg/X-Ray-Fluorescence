# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 11:17:03 2023

@author: cm846
"""
import tkinter as tkr

__all__ = ['ParamsWindow']

class ParamsWindow:
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
    def __init__(self, win, nwin, params, b_quit):
        self.params = params
        self.lblthresh = tkr.Label(win, text='Primary Threshold (\u03c3)')
        self.lblthresh2 = tkr.Label(win, text='Secondary Threshold (\u03c3)')
        self.lblsearch = tkr.Label(win, text='Search Grid')
        self.lblx1 = tkr.Label(win, text='x_1 Coordinate')
        self.lblx2 = tkr.Label(win, text='x_2 Coordinate')
        self.lbly1 = tkr.Label(win, text='y_1 Coordinate')
        self.lbly2 = tkr.Label(win, text='y_2 Coordinate')
        self.lblpixsize = tkr.Label(win, text="Pixel Size (cm)")
        self.lblinttime = tkr.Label(win, text="Integration Time (ms)")

        # Entry boxes
        # self.text_sigma = tkr.Entry(  win, bd=3, width = 20) # Sigma
        # self.text_offset = tkr.Entry( win, bd=3, width = 20) # Offset
        self.text_thresh = tkr.Entry( win, bd=3, width = 20) # Primary Threshold
        self.text_thresh2 = tkr.Entry(win, bd=3, width = 20) # Secondary Threshold
        self.text_x1 = tkr.Entry(win, bd=3, width = 20) # Sigma
        self.text_x2 = tkr.Entry(win, bd=3, width = 20) # Offset
        self.text_y1 = tkr.Entry(win, bd=3, width = 20) # Primary Threshold
        self.text_y2 = tkr.Entry(win, bd=3, width = 20) # Secondary Threshold
        self.text_pixelsize = tkr.Entry(win, bd=3, width=20) # Pixel Size
        self.text_inttime = tkr.Entry(win, bd=3, width=20) # Integration Time

        self.lbl_scale = tkr.Label(win, text='Tiff Scale Factor')
        self.tiff_scale = tkr.Entry(win, bd=3, width=20)

        # Dropdown Box Quarters
        self.options = ["All", "Q1-Q3", "Q1", "Q2", "Q3", "Q4"] 
        # To add another option, must also update self.params.roi @setter property
        self.clicked = tkr.StringVar()
        self.clicked.set( "All" ) # Default value is Raw
        self.drop = tkr.OptionMenu(win, self.clicked , *self.options)
        
        # Dropdown Box LR
        self.optionsLR = ["All", "Left", "Right", "LL", "ML", "MR", "RR"] 
        self.clickedLR = tkr.StringVar()
        self.clickedLR.set( "All" ) # Default value is Raw
        self.dropLR = tkr.OptionMenu(win, self.clickedLR , *self.optionsLR)
        

        # Buttons
        self.f1 = tkr.Frame(win)
        self.button_search_on  = tkr.Button(self.f1, text='On', width = 9, command = self.sg_on)
        self.button_search_off = tkr.Button(self.f1, text='Off', width = 9, command = self.sg_off)
        self.button_search_on.pack(side="left")
        self.button_search_off.pack(side="right")
        self.button_defaults = tkr.Button(win, text='Restore Default Values', width = 20, command = lambda: self.defaults(win))
        self.button_params = tkr.Button(win, text='Update Parameters', width = 20, command = lambda: self.update_params(win))
       
        
        self.lblthresh.grid(row = 1, column = 1, padx=5, pady=5)
        self.lblthresh2.grid(row = 2, column = 1, padx=5, pady=5)
        self.lblsearch.grid(row = 3, column = 1, padx=5, pady=5)
        self.lblx1.grid(row = 4, column = 1, padx=5, pady=5)
        self.lblx2.grid(row = 5, column = 1, padx=5, pady=5)
        self.lbly1.grid(row = 6, column = 1, padx=5, pady=5)
        self.lbly2.grid(row = 7, column = 1, padx=5, pady=5)
        self.lblpixsize.grid(row=8, column = 1, padx=5, pady=5)
        self.lblinttime.grid(row=9, column = 1, padx=5, pady=5)
        
        self.text_thresh.grid(row = 1, column = 2, padx=5, pady=5)
        self.text_thresh2.grid(row = 2, column = 2, padx=5, pady=5)
        self.f1.grid(row=3, column=2, sticky="nsew", padx=5, pady=5)
        self.text_x1.grid(row = 4, column = 2, padx=5, pady=5)
        self.text_x2.grid(row = 5, column = 2, padx=5, pady=5)
        self.text_y1.grid(row = 6, column = 2, padx=5, pady=5)
        self.text_y2.grid(row = 7, column = 2, padx=5, pady=5)
        self.text_pixelsize.grid(row = 8, column = 2, padx=5, pady=5)
        self.text_inttime.grid(row = 9, column = 2, padx=5, pady=5)
        
        self.lbl_scale.grid(row=10, column=1, padx=5,pady=5)
        self.tiff_scale.grid(row=10, column=2, padx=5,pady=5)
        
        self.button_params.grid(row = 11, column = 1, padx=5, pady=5)
        self.button_defaults.grid(row = 12, column = 1, padx=5, pady=5)
        self.drop.grid(row=11, column=2, padx=5, pady=5)
        self.dropLR.grid(row=11, column=3, padx=5, pady=5)
        b_quit.grid(row = 14, column = 2, padx=5, pady=5)

        self.sg_on()
        self.update_display()

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


    def sg_on(self):
        """
        Turns on search grid. Enables 'off' button and disables 'on' button.

        Returns
        -------
        None.

        """
        self.button_search_on["state"] = "disabled"
        self.button_search_off["state"] = "normal"


    def sg_off(self):
        """
        Turns off search grid. Enables 'on' button and disables 'off' button.

        Returns
        -------
        None.

        """
        self.button_search_on["state"] = "normal"
        self.button_search_off["state"] = "disabled"


    def defaults(self, win):
        self.params.threshold = 90
        self.params.sec_threshold = 20
        self.params.searchgrid = [460,  1555,  10,  935]
        self.update_display()


    def update_display(self):
        self.text_thresh.delete(0, tkr.END)
        self.text_thresh2.delete(0, tkr.END)
        self.text_x1.delete(0, tkr.END)
        self.text_x2.delete(0, tkr.END)
        self.text_y1.delete(0, tkr.END)
        self.text_y2.delete(0, tkr.END)
        self.text_pixelsize.delete(0, tkr.END)
        self.text_inttime.delete(0, tkr.END)
        self.tiff_scale.delete(0, tkr.END)
        self.text_thresh.insert(0, self.params.threshold)
        self.text_thresh2.insert(0, self.params.sec_threshold)
        self.text_x1.insert(0, self.params.searchgrid[0])
        self.text_x2.insert(0, self.params.searchgrid[1])
        self.text_y1.insert(0, self.params.searchgrid[2])
        self.text_y2.insert(0, self.params.searchgrid[3])
        self.text_pixelsize.insert(0, self.params.pixel_size)
        self.text_inttime.insert(0, self.params.int_time)
        self.tiff_scale.insert(0, self.params.scale)
        self.clicked.set(self.params.roi)
        self.clickedLR.set(self.params.LR)


    def update_params(self, win):
        """
        Stuff

        Parameters
        ----------
        win : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        txt_thresh = str(self.text_thresh.get())
        if txt_thresh.isdigit():
            self.params.threshold = int(txt_thresh)

        txt_thresh2 = str(self.text_thresh2.get())
        if txt_thresh2.isdigit():
            self.params.sec_threshold = int(txt_thresh2)
        
        x1 = str(self.text_x1.get())
        x2 = str(self.text_x2.get())
        y1 = str(self.text_y1.get())
        y2 = str(self.text_y2.get())
        if x1.isdigit() and x2.isdigit() and y1.isdigit() and y2.isdigit():
            self.params.searchgrid = [int(x1), int(x2), int(y1), int(y2)]
        
        txt_pixel_size = str(self.text_pixelsize.get())
        if txt_pixel_size.replace(".", "").isnumeric():
            self.params.pixel_size = float(txt_pixel_size)

        txt_inttime = str(self.text_inttime.get())
        if txt_inttime.replace(".", "").isnumeric():
            self.params.int_time = float(txt_inttime)
        
        tiff_factor = str(self.tiff_scale.get())
        if tiff_factor.replace(".", "").isnumeric():
            self.params.scale = int(tiff_factor)
            
        self.params.roi = self.clicked.get()
        self.params.LR = self.clickedLR.get()
        self.update_display()

