import sunpy
import sunpy.map
import glob
from sunpy.image.coalignment import mapcube_coalign_by_match_template
from datetime import datetime
import numpy as np
#
#Name:dih_sunplot_data
#
#Purpose:creates (time,flux) = (x,y) data, and also gives data,channel and center of first fits file in a given directory
#
#Inputs: directory with aia fits files (dirname)
#
#Outputs: list of times since first AIA image in directory
#
#Written: 7/8/14 Dan Herman	daniel.herman@cfa.harvard.edu
#
def dih_sunplot_data(dirname):
	filelist = glob.glob(dirname+"/*.fits")#get files
	maplist = []
	curvelist = []
	for member in filelist:#make list of sunpy maps
		my_map = sunpy.map.Map(member)
		maplist.append(my_map)
		sigma = np.sum(my_map)
		curvelist.append(sigma)
	difflist = []
	for map in maplist:#populate difflist with time differences to first map
		string1 = maplist[0].date
		string2 = map.date
		d1 = datetime.strptime(string1, '%Y-%m-%dT%H:%M:%S.%f')
		d2 = datetime.strptime(string2, '%Y-%m-%dT%H:%M:%S.%f')
		deltatime = d2-d1
		diff = deltatime.total_seconds()
		difflist.append(diff)
	my_first_map = maplist[0]
	datalist = [curvelist,difflist,my_first_map.date,my_first_map.measurement,my_first_map.center]
	return datalist

