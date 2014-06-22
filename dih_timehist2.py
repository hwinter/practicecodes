#Name: dih_timehist2.py
#
#Purpose: creates histogram of times (indices) of peak events
#
#
import sys
import numpy as np
import matplotlib
matplotlib.use('ps')
import matplotlib.pyplot as plt 
import pylab as P
import glob
import matplotlib.cm as cm
import matplotlib.mlab as mlab
from scipy import signal
import dih_tableread as d
import dih_timelistmaker as tlm
from scipy.stats import norm

def dih_basictimehist(dirname,histname):
    indata = tlm.dih_timelistmaker(dirname)
    y, binedges = np.histogram(indata,bins=10)
    bincenters = .5*(binedges[1:]+binedges[:-1])
    width = 3
    list1 = [i for i, j in enumerate(y) if j != 0.0]
    list2 = [0]*len(y)
    for num in list1:
        list2[num] = .5
    plt.bar(bincenters,y,width=width, color ='r',yerr=list2)
    plt.xlabel("Time of Peak")
    plt.ylabel("# of peaks")
    plt.title("Time Distribution of Peaks")
    (mu,sigma) = norm.fit(indata)
    plotline = mlab.normpdf(bincenters,mu,sigma)
    plt.plot(bincenters,plotline,'b--')
    plt.savefig(histname)
    return list1
