#!/usr/bin/env python

import commpy as com
import scipy.signal as sig
import matplotlib.pyplot as plt

class Filters:

    def __init__(self, F_SAMPLE, F_SYM, DEC_RATE):
        print("BUILDING FILTERS")
        self.fs = F_SAMPLE
        self.fsym = F_SYM
        self.dec = DEC_RATE
        self.fpilot = int(19e3)          # pilot tone, 19kHz from Fc
        self.rrc = self.build_rrc()
        self.bpf = self.build_bpf()
        self.ipf = self.build_ipf()
        self.clk = self.build_clk()
        self.lpf = self.build_lpf()

    def build_rrc(self):
        """Cosine Filter"""
        N = int(121)
        T = 1/self.fsym/2
        alfa = 1 #put 8 samples per sym period. i.e. 16+1 in the main lobe
        __,rrc = com.filters.rrcosfilter(N, alfa, T, self.fs/self.dec)
        return rrc

    def build_bpf(self):
        """Bandpass Filter, at 57kHz"""
        cutoff = 3.0e3          # one-sided cutoff freq, slightly larger than 2.4kHz
        w = [(self.fpilot*3 - cutoff) / self.fs*2, (self.fpilot*3 + cutoff) / self.fs*2]
        b, a = sig.butter(N=12, Wn=w, btype='bandpass', analog=False)
        #f,h = sig.freqz(b,a)
        #plt.plot(f*self.fs/2/3.14,abs(h))
        #plt.show()
        return b, a

    def build_ipf(self):
        """Infinite (impulse response) Peak Filter at 19kHz"""
        w = self.fpilot / float(self.fs / 2.0)
        q = w / 16.0 * self.fs        # Q = f/bw, BW = 16 Hz
        b, a = sig.iirpeak(w, q)
        return b, a

    def build_clk(self):
        """Infinite (impulse response) Peak Filter at Symbol Rate 1187.5Hz"""
        w = self.fsym / float(self.fs / self.dec / 2.0)
        q = w / 4.0 * self.fs * self.dec         # Q = f/bw, BW = 4 Hz
        b, a = sig.iirpeak(w, q)
        return b, a

    def build_lpf(self):
        w = self.fsym * 2 / self.fs * self.dec * 2
        b, a = sig.butter(N=9, Wn=w, btype='lowpass', analog=False)
        #f,h = sig.freqz(b,a)
        #plt.plot(f*self.fs/self.dec/2/3.14,abs(h))
        #plt.show()
        return b, a
