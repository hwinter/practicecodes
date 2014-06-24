import sys
import numpy as np
import matplotlib
matplotlib.use('ps')
import matplotlib.pyplot as plt 
import pylab
import glob
import matplotlib.cm as cm
from scipy.signal import boxcar
from dih_tableread import dih_filegrab
from dih_tableread import dih_tablereader
from scipy import signal
#
#Name: dih_boxcar
#
#Purpose: convolves boxcar window with vector x to produce smoother plot
#
#Inputs: input 1d array
#
#Outputs:Smoothed array of length = original length minus 2 (for useful case of width 3)
#
#Example: xsmooth = dih_boxcar(x)
#
#Written:6/23/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_boxcar(x):
	width = 3
	s = np.r_[x[width-1:0:-1],x,x[-1:-width:-1]]
	out = np.convolve(inarray, np.ones((width,))/width,mode='valid')
	return out[1:len(out)-1]
	
#Name: dih_plotter3
#
#Purpose: use dih_boxcar to provide smoothing....see dih_plotter2 in dih_smoothie for more
# documentation
#
#Written:6/23/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_plotter3(dirname,savename,numplot):
    inlist = dih_tablereader(dirname)
    plotlist = inlist[0:numplot]
    colors = iter(cm.rainbow(np.linspace(0,1,len(plotlist)))) #creates color table
    for memberlist in plotlist:
        x = memberlist[0] #x coordinate data
        y = memberlist[1] #y coordinate data
        ysmooth = dih_boxcar(y)
        xshort = x[0:len(ysmooth)]
        peaklist =signal.find_peaks_cwt(ysmooth, np.arange(1,30))#continuous wavelet transformation
        plt.plot(xshort,ysmooth,color = next(colors))
        for num in peaklist:
            plt.plot(xshort[num],ysmooth[num],'gD')#places markers on peaks
        peak = max(ysmooth)
        peaklist2 = [i for i, j in enumerate(ysmooth) if j == peak]
        for num in peaklist2:
            plt.plot(xshort[num],ysmooth[num],'rD')

#finish up plot characteristics
    plt.title('Super Most Awesome Graph!')
    plt.ylabel('Flux')
    plt.xlabel('Time')       
    pylab.ylim([-5,5])
    pylab.xlim([0,6.3])
    plt.savefig(savename)#saves postscript file
    return plotlist