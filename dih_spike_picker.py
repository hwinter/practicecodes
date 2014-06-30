import sys
import numpy as np
import matplotlib
matplotlib.use('ps')
import matplotlib.pyplot as plt 
import pylab
import glob
import matplotlib.cm as cm
from scipy import signal

def dih_spike_picker(inarray):
    crest = max(inarray)
    cave = min(inarray)
    diff = crest - cave
    crestlist = [i for i, j in enumerate(inarray) if j == crest]
    for num in crestlist:
        crestarray = inarray[num-2:num+2]
        subdiff = max(crestarray) - min(crestarray)
        if subdiff > .75*diff:
            inarray[num-2:num+2] = min(crestarray)
        else:
            print 'Not a false spike'
    return inarray

                