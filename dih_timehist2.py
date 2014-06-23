#Name: dih_timehist2.py
#
#Purpose: creates histogram of times (indices) of peak events
#
#Inputs: directory of input files (dirname) and save name for hist plot (histname)
#
#Outputs: chisquared value for fit of gaussian to event times as well as the corresponding 
# plot
#
#Example: chi = dih.dih_timehist2('../data','hist.ps')
#
#Written:6/22/14 Dan Herman daniel.herman@cfa.harvard.edu
import sys
import numpy as np
import matplotlib
matplotlib.use('ps')
import matplotlib.pyplot as plt 
import pylab as P
import glob
import scipy as sp
import matplotlib.cm as cm
import matplotlib.mlab as mlab
from scipy import signal
import dih_tableread as d
import dih_timelistmaker as tlm
from scipy.stats import norm
from scipy.optimize import curve_fit

# define gaussian test function
def gauss(x,*p):
	A,mu,sigma = p
	return A*np.exp(-(x-mu)**2/(2.*sigma**2))








def dih_timehist2(dirname,histname):
    indata = tlm.dih_timelistmaker(dirname)
    y, binedges = np.histogram(indata,bins=10)#create hist data
    bincenters = .5*(binedges[1:]+binedges[:-1])#create bin centers
    width = 3
    list1 = [i for i, j in enumerate(y) if j != 0.0]#find indices of non zero bin values
    list2 = [0]*len(y)
    for num in list1:#populate error list
        list2[num] = 2.0
    plt.bar(bincenters,y,width=width, color ='r',yerr=list2)#create bar plot with errors
    plt.xlabel("Time of Peak")
    plt.ylabel("# of peaks")
    plt.title("Time Distribution of Peaks")
    (mu,sigma) = norm.fit(indata)#gaussian fitting raw data
    plotline = mlab.normpdf(bincenters,mu,sigma)#creates the gaussian
    #alternative method for fitting
    #p0 = [1.,0.,1.]
    #coeff,var_matrix = curve_fit(gauss,bincenters,y,p0=p0)
    #hist_fit = gauss(bincenters, *coeff)
    #plt.plot(bincenters,hist_fit)
    plt.plot(bincenters,plotline)
    plt.savefig(histname)
    #create chi squared value
    residuals = plotline - y
    weighted = sp.sqrt(residuals**2/2.0**2)
    return sum(weighted)
