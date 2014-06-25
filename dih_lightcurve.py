import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import dih_sunplot as times
import dih_suncurve as values
import dih_sundate as date
#
#Name:dih_lightcurve
#
#Purpose:Plots a lightcurve given AIA files in a directory
#
#Inputs:directory (dirname) with files, savename for plot
#
#Outputs:plot saved as savename
#
#Written:6/25/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_lightcurve(dirname,savename):
	x = times.dih_sunplot_times(dirname)
	y = values.dih_suncurve(dirname)
	plt.plot(x,y,'b',linewidth = 2.0)
	plt.title('Lightcurve at'+' '+date.dih_sunfirst(dirname),y=1.08)
	plt.xlabel('Seconds Since'+' '+date.dih_sunfirst(dirname))
	plt.ylabel('Arbitrary Flux Units')
	plt.savefig(savename)
	return y