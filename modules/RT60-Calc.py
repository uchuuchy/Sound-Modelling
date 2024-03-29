# RT60 Calculator - 2019-03-18

import glob # for file access
import math
import matplotlib.pyplot as plt
import numpy as np # for fourier transforms
from scipy import stats # for convolution
import wave # for reading sound files
import xlwt

freqthird = [400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000] # Hz
freqbands = [355, 447, 562, 708, 891, 1122, 1413, 1778, 2239, 2818, 3548, 4467, 5623, 7079, 8913, 11220] # Hz
MAXLEV = 2**15 - 1
DBSCALE = 20
MEDAVGTIME = 0.3 # seconds
RATIOOFMAX = 0.7 # ratio of dB loss before trimming
CONVOLVEN = 2500 # convolve strength - 10000+ is too high!


def calcRT60(filename):
    RT60raw = [0.0] * len(freqthird)
    
    # open wav file
    wr = wave.open(filename, 'r')
    par = list(wr.getparams()) # get the parameters from the input    
    startframe = round(2.1 * par[2]) # time in seconds and sample rate
    endframe   = round(6.1 * par[2])
    endframe2  = round(3.0 * par[2])
    da = np.frombuffer(wr.readframes(-1), dtype=np.int16)
    wr.close() # close wav file

    da = da[startframe:endframe] # trim file to length

    for k in range(len(freqthird)):
        daf = np.fft.rfft(da, n=len(da)) # fourier transform
        lofreq = round((freqbands[k + 0] / (par[2] / 2)) * (len(daf) - 1))
        hifreq = round((freqbands[k + 1] / (par[2] / 2)) * (len(daf) - 1))
        daf[:lofreq] = 0 # apply high pass
        daf[hifreq:] = 0 # apply low pass
        nda = np.fft.irfft(daf, len(da)) # undo fourier transform
        nda = nda[:endframe2] # trim end
        nda = nda.astype(np.int16) # set data type to 16 bit integer
        
        nda = abs(nda) # log can't read negative values
        ndalog = [0.0] * len(nda) # init ndalog as float
        ndapre = [0.0] * len(nda) # ndapre is sound without averaging
        
        # convert to dB
        for i in range(len(nda)):
            if nda[i] != 0: # log can't read negative values
                ndalog[i] = DBSCALE * np.log10(nda[i] / MAXLEV) # MAXLEV is max 16-bit integer value
            else:
                ndalog[i] = DBSCALE * np.log10(1 / MAXLEV)
            ndapre[i] = ndalog[i]
        
        # average dB levels
        ndalog = np.convolve(ndalog, np.ones((CONVOLVEN,))/CONVOLVEN, mode='valid')
        
        ndalog_min, ndalog_max = min(ndalog), max(ndalog)
        ndalog_cut_apx = ndalog_max - (ndalog_max - ndalog_min) * RATIOOFMAX
        ndalog_cut_ind = (np.abs(ndalog - ndalog_cut_apx)).argmin()
        ndalog = ndalog[0:ndalog_cut_ind]
        
        # linear regression
        temp_index = np.arange(0, len(ndalog))
        slope, intercept, r_value, p_value, std_err = stats.linregress(temp_index, ndalog)
        dBlossline = slope * temp_index + intercept
        RT60 = -60.0 / (slope * par[2])
        
        RT60raw[k] = RT60
        print('|', end='')


        # plt.figure(1)
        # plt.subplot(211)
        # plt.suptitle('Linear Regression: ' + str(freqthird[k]) + ' Hz')
        # plt.plot(ndapre[0:ndalog_cut_ind], 'b')
        # plt.plot(dBlossline, 'g-')
        # plt.subplot(212)
        # plt.plot(ndalog, 'b:')
        # plt.plot(dBlossline, 'g-')
        # plt.savefig(f'{filename}.png')
        plt.plot(RT60raw)
        plt.savefig(f'{filename}.png')

    print('')
    return RT60raw

calcRT60("C:\\Users\\Valerio\\PycharmProjects\\Sound-Modelling\\test_sound_files\\clap.wav")