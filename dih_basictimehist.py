#Name: dih_basictimehist.py
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
from scipy import signal
import dih_tableread as d
import dih_timelistmaker as tlm

def dih_basictimehist(dirname,histname):
	indata = tlm.dih_timelistmaker(dirname)
	P.figure
	n, bins, patches = P.hist(indata,12,normed = 1, histtype = "stepfilled")
	plt.xlabel("Time of Peak")
	plt.ylabel("Fraction of total peaks")
	plt.title("Time Distribution of Peaks")
	plt.savefig(histname)
	return indata