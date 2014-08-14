#Name: dih_smooth
#
#Purpose: create kaiser smoothed version of input x with kaiser filter beta
#
#Inputs: array x and index beta
#
#Outputs: smoothed array
#
#Example: y = dih_smooth(y,16)
#
#Written: 6/23/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#

import sys
import numpy as np
import matplotlib
matplotlib.use('ps')
import matplotlib.pyplot as plt 
import pylab
import glob
import matplotlib.cm as cm
from scipy import signal
from dih_tableread import dih_filegrab
from dih_tableread import dih_tablereader
from dih_boxcar import dih_boxcar

def dih_smooth(x,beta):
    """ kaiser window smoothing """
    window_len=11
    # extending the data at beginning and at the end
    # to apply the window at the borders
    s = np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    w = np.kaiser(window_len,beta)#creates kaiser window
    y = np.convolve(w/w.sum(),s,mode='valid')#convolve normalized window with data
    return y[5:len(y)-5]
#
#
#

#Name:dih_plotter2
#
#Purpose:attempt at using kaiser smoothed data to find peaks and plot them
#
#Inputs: directory string, savename string, number of files to read from directory
#
#Keywords: kaiser = true -gives kaiser smoothing, boxcar = true -gives boxcar smoothing
#both = true -gives both kaiser then boxcar
#
#Outputs: plot of smoothed data from dirname, returns raw data
#
#Example: gah = dih_plotter2('../data','savename.ps',10)
#
#Written:6/23/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_plotter2(dirname,savename,numplot,kaiser,boxcar,both):
    inlist = dih_tablereader(dirname)
    plotlist = inlist[0:numplot]
    colors = iter(cm.rainbow(np.linspace(0,1,len(plotlist)))) #creates color table
    for memberlist in plotlist:
        x = memberlist[0] #x coordinate data
        y = memberlist[1] #y coordinate data
        if kaiser == 1:
        	ysmooth = dih_smooth(y,14)#kaiser smoothing
        if boxcar == 1:
        	ysmooth = dih_boxcar(y)#boxcar smoothing
        if both == 1:
        	ysmooth = dih_boxcar(dih_smooth(y,14))
        peaklist =signal.find_peaks_cwt(ysmooth, np.arange(4,30))#continuous wavelet transformation
        plt.plot(x,ysmooth,color = next(colors))
        for num in peaklist:
            plt.plot(x[num],ysmooth[num],'gD')#places markers on peaks
        peak = max(ysmooth)
        peaklist2 = [i for i, j in enumerate(ysmooth) if j == peak]#places markers on absolute peaks
        for num in peaklist2:
            plt.plot(x[num],ysmooth[num],'rD')

#finish up plot characteristics
    plt.title('Super Most Awesome Graph!')
    plt.ylabel('Flux')
    plt.xlabel('Time')       
    pylab.ylim([-5,5])
    pylab.xlim([0,6.3])
    plt.savefig(savename)#saves postscript file
    return plotlist
