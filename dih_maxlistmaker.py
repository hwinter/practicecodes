#Name: dih_maxlistmaker.py
#
#Purpose: makes list of times (indices) of first peak event
#
#Inputs: directory containing data
#
#Outputs: list of times of first peak event
#
#Example: peaks = dih_maxlistmaker('../data')
#
#Written:6/19/14 Dan Herman daniel.herman@cfa.harvard.edu
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

def dih_maxlistmaker(dirname):
	indata = d.dih_tablereader(dirname)
	timelist =[]
	endlist =[]
	for memberlist in indata:
		y = memberlist[1]
		peak = max(y)
		peaklist = [i for i, j in enumerate(y) if j==peak]
		timelist.append(peaklist[0])
	for member in timelist:
		for item in member:
			endlist.append(item)
	
	
	
	
	return endlist