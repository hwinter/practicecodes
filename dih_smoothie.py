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
    w = np.kaiser(window_len,beta)
    y = np.convolve(w/w.sum(),s,mode='valid')
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
#Outputs: plot of smoothed data from dirname, returns raw data
#
#Example: gah = dih_plotter2('../data','savename.ps',10)
#
#Written:6/23/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_plotter2(dirname,savename,numplot):
    inlist = dih_tablereader(dirname)
    plotlist = inlist[0:numplot]
    colors = iter(cm.rainbow(np.linspace(0,1,len(plotlist)))) #creates color table
    for memberlist in plotlist:
        x = memberlist[0] #x coordinate data
        y = memberlist[1] #y coordinate data
        ysmooth = dih_smooth(y,14)
        ysmoother = dih_boxcar(ysmooth,3)
        xnew = x[0:len(ysmoother)]
        peaklist =signal.find_peaks_cwt(ysmoother, np.arange(3,20))#continuous wavelet transformation
        plt.plot(xnew,ysmoother,color = next(colors))
        for num in peaklist:
            plt.plot(xnew[num],ysmoother[num],'gD')#places markers on peaks
        peak = max(ysmoother)
        peaklist2 = [i for i, j in enumerate(ysmoother) if j == peak]
        for num in peaklist2:
            plt.plot(xnew[num],ysmoother[num],'rD')

#finish up plot characteristics
    plt.title('Super Most Awesome Graph!')
    plt.ylabel('Flux')
    plt.xlabel('Time')       
    pylab.ylim([-5,5])
    pylab.xlim([0,6.3])
    plt.savefig(savename)#saves postscript file
    return plotlist
