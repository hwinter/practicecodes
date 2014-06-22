#Name: dih_timelistmaker.py
#
#Purpose: makes list of times (indices) of peak event
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

def dih_timelistmaker(dirname):
	indata = d.dih_tablereader(dirname)
	timelist =[]
	endlist =[]
	for memberlist in indata:
		y = memberlist[1]
		peak = max(y)
		peaklist = [i for i, j in enumerate(y) if j==peak]
		timelist.append(peaklist)
	for member in timelist:
		for item in member:
			endlist.append(item)
	
	
	
	
	return endlist
		