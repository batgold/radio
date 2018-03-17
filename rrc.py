#!/usr/bin/env python

import numpy as np
import matplotlib
import scipy.signal as signal
import matplotlib.pyplot as plt
import commpy

F_SAMPLE = int(228e3)       # 225-300 kHz and 900 - 2032 kHz
F_CENTER = int(88.5e6)     # FM Station
F_PILOT = int(19e3)         # pilot tone, 19kHz from Fc
N_SAMPLES = int(512*512*3)  # must be multiple of 512, should be a multiple of 16384 (URB size)
DEC_RATE = int(12)          # RBDS rate 1187.5 Hz. Thus 228e3/1187.5/24 = 8 sample/sym
F_SYM = 1187.5            # Symbol rate, full bi-phase
SPS = int(F_SAMPLE/DEC_RATE/F_SYM)   # Samples per Symbol

N = int(40)
T = 1/F_SYM/2
alfa = 1 #put 8 samples per sym period. i.e. 16+1 in the main lobe

__,rrc = commpy.filters.rrcosfilter(N,alfa,T,F_SAMPLE/DEC_RATE)

rrc_man = np.array([-0.00281562025759368,-0.00243888516957360,-0.000999844542191435,0.00107593094803098,0.00303973034012925,0.00406700703874643,0.00357325036472412,0.00148757358716287,-0.00162769040855969,-0.00468282782128020,-0.00639101106088724,-0.00573885664637510,-0.00244729848210667,0.00275023551791118,0.00815158917037663,0.0115038199095970,0.0107291667736578,0.00477805894125585,-0.00564522027360720,-0.0177416940767021,-0.0268422464557264,-0.0272355771946698,-0.0134654388344483,0.0181901542149565,0.0684322485815653,0.134211232278632,0.208806091825802,0.282774215523415,0.345612930084173,0.387782741962203,0.402633696835896,0.387782741962203,0.345612930084173,0.282774215523415,0.208806091825802,0.134211232278632,0.0684322485815653,0.0181901542149565,-0.0134654388344483,-0.0272355771946698,-0.0268422464557264,-0.0177416940767021,-0.00564522027360720,0.00477805894125585,0.0107291667736578,0.0115038199095970,0.00815158917037663,0.00275023551791118,-0.00244729848210667,-0.00573885664637510,-0.00639101106088724,-0.00468282782128020,-0.00162769040855969,0.00148757358716287,0.00357325036472412,0.00406700703874643,0.00303973034012925,0.00107593094803098,-0.000999844542191435,-0.00243888516957360,-0.00281562025759368])

f = np.arange(0,2350)
c = np.cos(np.pi*f/F_SYM/4)
cdb = 10*np.log10(c) - 92
plt.figure(1)
plt.plot(rrc_man,'r*')
plt.plot(rrc,'b.')
plt.show()


plt.figure(2)
plt.psd(rrc_man*11,2048,Fs=25e3)
plt.psd(rrc,2048,Fs=F_SAMPLE/DEC_RATE)
plt.plot(f,cdb)
plt.show()
