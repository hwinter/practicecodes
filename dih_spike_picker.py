import sys
import numpy as np
import matplotlib
matplotlib.use('ps')
import matplotlib.pyplot as plt 
import pylab
import glob
import matplotlib.cm as cm
from scipy import signal
#
#
#Name: dih_spike_picker
#
#Purpose: finds spikes of data that are not flares and flattens them
#
#Inputs: array of lightcurve flux data (inarray)
#
#Outputs: new array of flux data with spikes removed
#
#Example: ynew = dih_spike_picker(y)
#
#Written: 6.30.14 Dan Herman daniel.herman@cfa.harvard.edu
#
#

def dih_spike_picker(inarray):
    crest = max(inarray)
    cave = min(inarray)
    diff = crest - cave
    crestlist = [i for i, j in enumerate(inarray) if j == crest]
    print crestlist
    for num in crestlist:
    	print num
        if num < len(inarray)-3 and num > 2:
        	crestarray = inarray[num-2:num+3]
        	numlist = range(num-2,num+3)
        elif num >= len(inarray)-3:
        	crestarray = inarray[len(inarray)-3:len(inarray)]
        	numlist = range(len(inarray)-3,len(inarray))
        elif num <= 2:
        	crestarray = inarray[0:3]
        	numlist = range(0,3)
        else:
        	print "bad index"	
        subdiff = max(crestarray) - min(crestarray)
        if subdiff > .5*diff:
            for member in numlist:
            	inarray[member] = min(crestarray)
            dih_spike_picker(inarray)
        else:
            print 'Not a false spike'
    return inarray

                