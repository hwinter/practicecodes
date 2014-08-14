import sunpy
import sunpy.map
import glob
from datetime import datetime
#
#Name:dih_sunfirst
#
#Purpose:finds time of first AIA image in directory
#
#Inputs: directory with aia fits files (dirname)
#
#Outputs: first timestring
#
#Written:6/25/14 Dan Herman	daniel.herman@cfa.harvard.edu
#
def dih_sunfirst(dirname):
	filelist = glob.glob(dirname+"/*.fits")
	my_map = sunpy.map.Map(filelist[0])
	return [my_map.date,my_map.center,my_map.measurement]
#
#
#
#
def dih_suncenter(dirname):
	filelist = glob.glob(dirname+"/*.fits")
	my_map = sunpy.map.Map(filelist[0])
	return my_map.center