# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 15:10:01 2023

@author: cm846
"""
import logging
import time
import datetime
from functools import lru_cache
import numpy as np
from tifffile import imread
from scipy.signal import savgol_filter


@lru_cache(maxsize=100000)
def grid_search_3x3(i: int, n: int=2048, m: int=2040, search: bool=None) -> tuple:
    """
    Creates coordinates for a 3x3 grid around coordinate 'i' for an array of
    length 'n' and width 'm'. Includes boundaries so that if coordinate is on
    a border, negative coordinates or 'out-of-bounds' values are not included.

    Params
    ------------
    i: int.
        The coordinate around which the 3x3 grid search coordinates are found.

    n: int, optional.
        The length of the array. Default value is 2048.

    m: int, optional.
        The width of the array. Default value is 2040.

    search: list, optional.
        search = [x_1, x_2, y_1, y_2].
        The values x_1, x_2, y_1, and y_2 represents the edges of the searchgrid, in
        pixel coordinates.
        Default values are x_1 = 0,  x_2 = 2047,  y_1 = 0, y_2 = 2039.

    """
    if search is None:
        search = [0,n-1,0,m-1]

    try: # Find the row and column respectively of the input coordinate.
        row = i // n
        col = i %  n
        x_1, x_2, y_1, y_2 = search # Search Grid corners (in 2D pixel coordinate values)

        # Search Grid Boundary Error Handling
        if i < 0 or i >= n*m: # Input coordinate is negative or larger than n*m
            raise ValueError

        if x_1 < 0 or x_1 >= x_2 or x_2 + 1 > n: #Search grid error on x_1 and x_2 values
            raise ValueError

        if y_1 < 0 or y_1 >= y_2 or y_2 + 1 > m: # Search grid error on y_1 and y_2 values
            raise ValueError

        if row < y_1 or row > y_2: # Input row is out of bound
            raise ValueError

        if col < x_1 or col > x_2: # Input column is out of bounds
            raise ValueError

    except TypeError:
        return ()

    except ValueError:
        return ()

    try: # Convert 2D Search Grid corners into 1D pixel coordinate values.
        coords = [x_1 + y_1*n,  x_2 + y_1*n,  x_1 + y_2*n,  x_2 + y_2*n]
        topleft, topright, bottomleft, bottomright = coords

        # if i == topleft:                                    # Topleft.
        #     return (i, i+1, i+n, i+n+1)

        # if i == topright:                                   # Topright.
        #     return (i, i-1, i+n-1, i+n)

        # if i == bottomleft:                                 # Bottomleft.
        #     return (i, i-n, i-n+1, i+1)

        # if i == bottomright:                                # Bottomright.
        #     return (i, i-n-1, i-n, i-1)

        # if topleft <= i <= topright:                # Along first row.
        #     return (i, i-1, i+1, i+n-1, i+n, i+n+1)

        # if bottomleft <= i <= bottomright:          # Along last row.
        #     return (i, i-n-1, i-n, i-n+1, i-1, i+1)

        # if not (i-topleft) % n:                           #Leftmost column.
        #     return (i, i-n, i-n+1, i+1, i+n, i+n+1)

        # if not (i-topright) % n:                          # Rightmost column.
        #     return (i, i-n-1, i-n, i-1, i+n-1, i+n)

        return (i, # Center of 3x3
                i-n-1, i-n, i-n+1,
                i-1, i+1,
                i+n-1, i+n, i+n+1) # 3x3

        # return (i, # Center of 5x5
        #         i-2*n-2, i-2*n-1, i-2*n, i-2*n+1, i-2*n+2,
        #         i-1*n-2, i-1*n-1, i-1*n, i-1*n+1, i-1*n+2,
        #         i-2, i-1, i+1, i+2,
        #         i+1*n-2, i+1*n-1, i+1*n, i+1*n+1, i+1*n+2,
        #         i+2*n-2, i+2*n-1, i+2*n, i+2*n+1, i+2*n+2)

        # return (i, # Center of 7x7
        #         i-3*n-3, i-3*n-2, i-3*n-1, i-3*n, i-3*n+1, i-3*n+2, i-3*n+3,
        #         i-2*n-3, i-2*n-2, i-2*n-1, i-2*n, i-2*n+1, i-2*n+2, i-2*n+3,
        #         i-1*n-3, i-1*n-2, i-1*n-1, i-1*n, i-1*n+1, i-1*n+2, i-1*n+3,
        #         i-3, i-2, i-1, i+1, i+2, i+3,
        #         i+1*n-3, i+1*n-2, i+1*n-1, i+1*n, i+1*n+1, i+1*n+2, i+1*n+3,
        #         i+2*n-3, i+2*n-2, i+2*n-1, i+2*n, i+2*n+1, i+2*n+2, i+2*n+3,
        #         i+3*n-3, i+3*n-2, i+3*n-1, i+3*n, i+3*n+1, i+3*n+2, i+3*n+3)
    
    

    except TypeError:
        print("Error")
        return ()

    except ValueError:
        print("Error")
        return ()


def xrf_analysis(filenames, queue_time, queue_data, event, parameters, is_tiff_file, roi, LR, scale):
    """
    Imports raw files from a directory, subtracts a dark frame and offset
    from each frame. Identifies all pixels above a threshold value, then
    identifies if they are single pixel or multipixel events. Stores all
    single pixel events (coordinate, value, and file) into an HDF5 file
    and all multipixel events (coordinate, values, event number, and file)
    into another HDF5 file.


    Parameters
    ----------
    win : tkinter frame.
        The Tkinter frame which the GUI is running in.

    Returns
    -------
    error
        int. Returns 1 if an error has occured, 0 otherwise.

    """
    try:
        early, percent, stop = 0, 0.00, 0
        zero = str(datetime.timedelta(seconds=0))
        elaps = zero
        queue_time.put([elaps, zero, percent, 0, 0, stop])
        energy_sp, energy_mp = [], []

        rows, cols, searchgrid, threshold, sec_threshold, dark, hot_pixels = parameters
        x_1, x_2, y_1, y_2 = searchgrid
        sg = [x_1, x_2, y_1, y_2]

        searchgrid = (sg[0], sg[1], sg[2], sg[3])
        x_1, x_2, y_1, y_2 = searchgrid

        # Array of 1D coordinate positions inside searchgrid
        pl_arr = np.zeros((rows*cols), dtype = int)
        test = np.reshape(np.arange(0, rows*cols),(rows,cols))
            
        x = np.arange(0, 512)
        y = np.arange(0, 512)
        arr = np.zeros((y.size, x.size))
        
        cx = 165. # X Centre # 384 is centre of OBF, 128 is centre of non OBF
        cy = 320. # Y Centre  #320 for Q3, 192 for Q2
        r = 58. # 155 pixels radius
        
        mask = ((x[np.newaxis,:]-cx)/1)**2 + ((y[:,np.newaxis]-cy)/1)**2 < r**2
        
        # subset = test[y_1:y_2+1, x_1:x_2+1].reshape(-1)
        subset = test[mask].reshape(-1)
        prev = total = time.time()
        
        for file_count, file in enumerate(filenames):
            if time.time() - prev > 1: # Update progress bar every second
                prev = time.time()
                time_c = time.time() - total
                elaps = str(datetime.timedelta(seconds = int(time_c)))
                time_r = time_c * len(filenames) / (file_count+1) - time_c
                remain = str(datetime.timedelta(seconds=  int(time_r)))
                percent = np.around((file_count+1) / len(filenames) * 100, 2)
                queue_time.put([elaps, remain, percent, energy_sp, energy_mp, 0])

            sp, mp = [], []

            # Import data, subtract dark frame, and set hot_pixels to 0
            if is_tiff_file:
                x = imread(file)
                x = x[::scale, ::scale]
                arr = x.astype(int)
                
                dark = dark.reshape(x.shape)
                arr = np.subtract(arr, dark)
                
                for i in range(arr.shape[0]):
                        diff = arr[i, 256:512]
                        heights, bins= np.histogram(diff, bins = np.arange(np.amin(diff), np.amax(diff)+1, 1))
                        heights = heights.astype(int)
                        bins = np.delete(bins, len(bins)-1)
                        y_values, temp_l, temp_r = [], [], []
                        y_values = heights.tolist()
                        peak_height = max(y_values)
                        mean = bins[y_values.index(peak_height)]
                        arr[i,256:512] = arr[i,256:512] - mean
                        
                for i in range(arr.shape[0]):
                        diff = arr[i, 0:256]
                        heights, bins= np.histogram(diff, bins = np.arange(np.amin(diff), np.amax(diff)+1, 1))
                        heights = heights.astype(int)
                        bins = np.delete(bins, len(bins)-1)
                        y_values, temp_l, temp_r = [], [], []
                        y_values = heights.tolist()
                        peak_height = max(y_values)
                        mean = bins[y_values.index(peak_height)]
                        arr[i,0:256] = arr[i,0:256] - mean
                
                dark = dark.flatten()
                arr =  arr.flatten()
                
            else: # Raw File
                arr = np.memmap(file, dtype='>u2', mode='r').astype(int) # Import Raw File
                arr = arr.reshape((rows, cols))
                arr = arr.flatten()
                dark = dark.flatten()
                arr = np.subtract(arr, dark)

            pl_arr[subset] = arr[subset]
            
            # print(np.mean(pl_arr))

            pl_arr[hot_pixels] = -10001 # Set to arbitrarily low value

            searched = [] # List of searched coords
            mp_count = 0  # Multi pixel event counter

            coords_above_threshold = np.nonzero(pl_arr > sec_threshold)[0]

            for i in coords_above_threshold:
                if event.is_set():
                    early = 1
                    print("Calculation stopped early\n")
                    break

                if i in searched: # If it's already been stored, skip this loop
                    continue

                coords = np.array(grid_search_3x3(i, n=cols, m=rows, search = searchgrid))
                if arr[i] != np.amax(arr[coords]):
                    continue

                    
                if not coords.size: # Skip loop if no coords return (out of bounds)
                    continue

                # singlepix = np.all(arr[coords[1:]] < sec_threshold)
                singlepix = True
                near_hotpixel = not np.all(arr[coords[1:]] > -10000)
                
                # Single pixel and above threshold
                if arr[i] >= threshold and singlepix:
                    if near_hotpixel:
                        continue
                    # if not np.all(arr[coords[1:]] > -10000): # Near a hotpixel

                    # # Near multiple hotpixels
                    #     if np.count_nonzero(arr[coords] == -10001) > 1:
                    #         continue

                        # first_coord = coords[0]
                        # r, c = np.unravel_index(coords, shape=(rows, cols))
                        # row_diffs = np.abs(r - first_coord // cols)
                        # col_diffs = np.abs(c - first_coord % cols)
                        # diagonal_mask = np.logical_and(row_diffs == col_diffs, row_diffs > 0)
                        # crnr = [coords[i] for i in np.where(diagonal_mask)[0]]
                        # c = [i for i in coords if i not in crnr]

                        # if not np.all(arr[c] > -10000): # Hotpixel nearest neighbour
                        #     continue

                    searched.append(i)  # Add coord to list of searched coordinates.
                    energy_sp.append(np.sum(arr[coords]))
                    sp += [[i, np.sum(arr[coords])]]
                    
                    # energy_sp.append(arr[i])
                    # sp += [[i, arr[i]]]

                # Multipixel
                if not singlepix:
                    continue
                    rm = 0
                    # continue
                    # near_hotpixel = np.all(arr[coords[1:]] > -10000)
                    near_hotpixel = np.all(arr[coords[1:]] > -10000)
                    if -10001 in arr[coords]:
                        rm = 1
                        continue

                    mp_coords = coords[arr[coords] >= sec_threshold].tolist() # search initial cell
                    mp_searched = [i]
                    
                    
                    while not set(mp_searched) == set(mp_coords):
                        nw_i = next((it for it in mp_coords if it not in mp_searched), None)

                        if nw_i is None:
                            break

                        if len(mp_searched) > 20:
                            break

                        mp_searched.append(nw_i)

                        c = np.array(grid_search_3x3(nw_i, n=cols, m=rows, search = searchgrid))
                        if -10001 in arr[c]:
                            rm = 1
                            break

                        if c.size == 0:
                            break

                        cell_coords = c[arr[c] >= sec_threshold]

                        l = [item for item in cell_coords if item not in mp_coords]

                        if l != []:
                            [mp_coords.append(j) for j in l]


                    ncoords = np.array(mp_coords)
                    values = arr[ncoords.tolist()]
                    
                    if rm == 1:
                        continue

                    if np.sum(values) < threshold:
                        continue

                    if np.count_nonzero(arr[coords] == -10001) > 1: # If near multiple hot pixels
                        continue

                    mp_count += 1       # Store the multipixel event number
                    searched += [item for item in ncoords if item in coords_above_threshold]
                    energy_mp += [np.sum(values)]
                    mp += [[ncoords.tolist(), values.tolist()]]

            queue_data.put([[sp], [mp]])

            if early:
                break

    except FileNotFoundError("File in filenames not found"):
        queue_time.put([elaps, zero, 0, energy_sp, energy_mp, 1])
        queue_time.put([f'Files: {file_count} / {len(filenames)} --> Percentage: {percent}%'])

    except RuntimeError("Unspecified run-time error"):
        queue_time.put([elaps, zero, 0, energy_sp, energy_mp, 1])
        queue_time.put([f'Files: {file_count} / {len(filenames)} --> Percentage: {percent}%'])

    except TypeError("Type Error"):
        queue_time.put([elaps, zero, 0, energy_sp, energy_mp, 1])
        queue_time.put([f'Files: {file_count} / {len(filenames)} --> Percentage: {percent}%'])

    except Exception("General Exception") as err:
        logging.exception(err)
        queue_time.put([elaps, zero, 0, energy_sp, energy_mp, 1])
        queue_time.put([f'Files: {file_count} / {len(filenames)} --> Percentage: {percent}%'])

    else:
        # print(graded)
        time_c = time.time() - total
        elaps = str(datetime.timedelta(seconds = int(time_c)))
        if file_count == 0:
            time_r = 0
        else:
            time_r = time_c * len(filenames) / (file_count) - time_c
        remain = str(datetime.timedelta(seconds=  int(time_r)))
        percent = np.around((file_count) / len(filenames) * 100, 2)
        try:
            if early:
                queue_time.put([elaps, zero, percent, energy_sp, energy_mp, 1]) # Set stop to 1
                queue_time.put([f'Files: {file_count} / {len(filenames)} --> Percentage: {percent}%',
                                f' - Single Pixels: {len(energy_sp)}.',
                                f' - Multi Pixels: {len(energy_mp)}.'])

            if not early:
                # print(f"Number of skips {l}")
                queue_time.put([elaps, zero, 100, energy_sp, energy_mp, 1]) # Set stop to 1, and progressbar to 100
                queue_time.put([f'Calculation Results --> {file_count+1} / {len(filenames)} Files.',
                                f' - Single Pixels: {len(energy_sp)}.',
                                f' - Multi Pixels: {len(energy_mp)}.'])
        except Exception as err:
            logging.exception(err)
            print("Unspecified Error")

