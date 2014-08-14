#Name: dih_basichist.py
#
#
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
from scipy import signal
import dih_tableread as d
import matplotlib.mlab as mlab
from scipy.stats import norm

def dih_basichist(dirname,histname):
	indata = d.dih_tablereader(dirname)
	peaklist = []
	for memberlist in indata:
		y = memberlist[1]
		peak = max(y)
		peaklist.append(peak)
	P.figure()
	n, bins, patches = P.hist(peaklist,12, histtype = "stepfilled")
	(mu,sigma) = norm.fit(peaklist)
	plotline = mlab.normpdf(bins,mu,sigma)
	plt.plot(bins, plotline)
	plt.xlabel('Max value of Random Data')
	plt.ylabel('Fraction of Counts')
	plt.title('Practice with Histograms')
	plt.savefig(histname)
	return peaklist
	