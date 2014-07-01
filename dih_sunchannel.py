import sunpy
import sunpy.map
import glob
from datetime import datetime
#
#Name:dih_sunchannel
#
#Purpose:finds channel of first AIA image in directory
#
#Inputs: directory with aia fits files (dirname)
#
#Outputs: channel
#
#Written:6/25/14 Dan Herman	daniel.herman@cfa.harvard.edu
#
def dih_sunchannel(dirname):
	filelist = glob.glob(dirname+"/*.fits")
	my_map = sunpy.map.Map(filelist[0])
	return my_map.measurement