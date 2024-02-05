# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 10:44:25 2023

@author: cm846
"""
import numpy as np
from numpy import sqrt, log
from matplotlib import pyplot as plt

def sigma2Gamma(sigma):
    '''Function to convert standard deviation (sigma) to FWHM (Gamma)'''
    return sigma * sqrt(2 * log(2)) * 2 / sqrt(2)

Gamma = sigma2Gamma(10)
print(Gamma)
# prints 16.651092223153956, which is what you saw in your graph

def Gamma2sigma(Gamma):
    '''Function to convert FWHM (Gamma) to standard deviation (sigma)'''
    return Gamma * sqrt(2) / ( sqrt(2 * log(2)) * 2 )

sigma = Gamma2sigma(10)
print(sigma)

height = 6000
width = 7
mean = 0
x1 = np.arange(-20, 50, 0.1)
y1 = height * np.exp( - ((x1-mean)/Gamma2sigma(width))**2 )
# plt.plot(x1,y1)

height = 46
width = 6
mean = 14
x2 = np.arange(-20, 50, 0.1)
y2 = height * np.exp( - ((x2-mean)/Gamma2sigma(width))**2 )
# plt.plot(x2,y2)

comb = y1 + y2

# plt.figure()
# plt.plot(x1, y1, linestyle="dotted")
# plt.plot(x2, y2, linestyle="dotted")
# plt.plot(x2, comb)
# plt.plot(x, y)
# plt.xlim(2, 25)
# plt.ylim(0, 100)

# QE = 0.5
# P = 100 # Signal Photon
# B = 5 # Background
# Read = 5
# Gain = 1.86
# noise = (QE*(P+B)+(Read/Gain)**2)**0.5
# SNR = QE * P / noise

# print(f'Noise: {noise}')
# print(f'SNR: {SNR}')




# raise SystemExit(0)
# Figure
plt.figure()
plt.title("FWHM (X-ray Resolution) against Energy")
plt.xlabel("Energy (eV)")
plt.ylabel("X-Ray Resolution - FWHM (eV)")
plt.xscale('log')
# plt.yscale('log')
plt.xlim([100, 10000])
plt.ylim([1,300])

# Energy Values
E = np.arange(0, 10000, 10)

# Fano 
F = 0.115
Si = 3.65

def ADU_to_e(ADU):
    e = ADU * 5993/345 * 1 / Si
    return e

# Fano
FWHM = 2.355 * (F*E*Si)**0.5

# Photo Response Non Uniformity (1% deviation)
PRNU = 0.009 * E * 2.355 # Convert to FWHM
# PRNU = 0*E

# Dark Current
D_c = 8 # ADU
D_c = np.array([D_c * 6.8] * len(E))
# D_c = np.array([200 * 3.65/10] *len(E))

# Read - (2.5e- rms deviation)
Read = np.array([12 * Si * 2.355] * len(E))
# Read = np.array([103] * len(E)) # 52 electrons FWHM = 188 eV FWHM = 11 ADU

# Total
Total = np.sqrt(  np.square(FWHM) + np.square(D_c) + np.square(Read) + np.square(PRNU) )

# Plot Lines
plt.plot(E,Total, label="Total") # Total
plt.plot(E, FWHM, label="Fano", ls='--') # Fano
plt.plot(E, D_c, label="Dark Current", ls=':') # D_c
plt.plot(E, Read, label="Read", ls='-.') # Read
# plt.plot(E, PRNU, label="PRNU", ls='-')

# Add energy range of interest
plt.axvline(x = 277, color = 'black', lw=1, ls=':')
plt.axvline(x = 525, color = 'black', lw=1, ls=':')

plt.axvline(x = 928, color = 'black', lw=1, ls=':')
plt.axvline(x = 1040, color = 'black', lw=1, ls=':')
plt.axvline(x = 1255, color = 'black', lw=1, ls=':')

plt.axvline(x = 1486, color = 'black', lw=1, ls=':')
plt.axvline(x = 1740, color = 'black', lw=1, ls=':')

plt.axvline(x = 2010, color = 'black', lw=1, ls=':')
plt.axvline(x = 2622, color = 'black', lw=1, ls=':')
plt.axvline(x = 4953, color = 'black', lw=1, ls=':')

plt.axvline(x = 6405, color = 'black', lw=1, ls=':')
# plt.axvline(x = 7059, color = 'black', lw=1, ls=':')

# plt.axvline(x = 7480, color = 'black', lw=1, ls=':')
# Add a legend
plt.legend()


# en = [277, 525, 928, 1040, 1254, 1486, 1740, 2010, 2622,    4953, 6405] #, 7480]
# val = [122, 122, 122 ,122, 139 ,139, 139, 139,  139,  174, 174] #, 243]

en = [392, 525, 1486, 1740, 3692, 4512, 5415, 6405]
val = [122, 122, 136, 143, 170, 184, 204,218 ]
plt.plot(en,val, marker="o")
