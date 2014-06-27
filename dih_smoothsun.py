#Name: dih_smoothsun
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
from dih_lightcurvedata import dih_lightcurvedata
import dih_sunplot as times
import dih_suncurve as values
import dih_sundate as date
import dih_sunchannel as channel
from scipy.signal import argrelextrema
import dih_dir_finder as finder

#see dih_smoothie for documentation for dih_smooth module
def dih_smooth(x,beta):
    """ kaiser window smoothing """
    window_len=7
    # extending the data at beginning and at the end
    # to apply the window at the borders
    s = np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    w = np.kaiser(window_len,beta)#creates kaiser window
    y = np.convolve(w/w.sum(),s,mode='valid')#convolve normalized window with data
    return y[3:len(y)-3]
#
#
#
#Name:dih_plotter3
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
def dih_plotter3(dirname,savename,kaiser,boxcar,both):
    fitslist = finder.dih_dir_finder(dirname)
    for idx,dirpath in enumerate(fitslist):
    	print "processing"+str(idx)
    	inlist = zip(*dih_lightcurvedata(dirpath))
    	plotlist = [list(row) for row in inlist]
    	colors = iter(cm.rainbow(np.linspace(0,1,len(plotlist)))) #creates color table
    	x = plotlist[0] #x coordinate data
    	y = plotlist[1] #y coordinate data
    	if kaiser == 1:
    		ysmooth = dih_smooth(y,14)#kaiser smoothing
    	if boxcar == 1:
    		ysmooth = dih_boxcar(y)#boxcar smoothing
    	if both == 1:
    		ysmooth = dih_boxcar(dih_smooth(y,14))
    	#peaklist =signal.find_peaks_cwt(ysmooth, np.arange(1,10))#continuous wavelet transformation
    	peaklist = argrelextrema(ysmooth, np.greater)
    	plt.plot(x,ysmooth,color = next(colors))
    	#for num in peaklist[0]:
    		#plt.plot(x[num],ysmooth[num],'gD')#places markers on peaks
    	peak = max(ysmooth)
    	peaklist2 = [i for i, j in enumerate(ysmooth) if j == peak]#places markers on absolute peaks
    	for num in peaklist2:
    		plt.plot(x[num],ysmooth[num],'rD')

#finish up plot characteristics
    	plt.plot(x,y,'b',linewidth = 2.0)
    	plt.title('Lightcurve at'+' '+date.dih_sunfirst(dirpath)+ ' '+ str(channel.dih_sunchannel(dirpath))+'$\AA$',y=1.07)
    	plt.xlabel('Seconds Since'+' '+date.dih_sunfirst(dirpath))
    	plt.ylabel('Arbitrary Flux Units')
    	plt.savefig(savename+str(idx)+'.ps')#saves postscript file
    return fitslist
