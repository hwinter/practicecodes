import sunpy
import sunpy.map
import glob
from sunpy.image.coalignment import mapcube_coalign_by_match_template
from datetime import datetime
#
#Name:dih_sunplot_times
#
#Purpose:creates 1d vector of time since first AIA image in a directory
#
#Inputs: directory with aia fits files (dirname)
#
#Outputs: list of times since first AIA image in directory
#
#Written:6/25/14 Dan Herman	daniel.herman@cfa.harvard.edu
#
def dih_sunplot_times(dirname):
	filelist = glob.glob(dirname+"/*.fits")
	maplist = []
	for member in filelist:
		my_map = sunpy.map.Map(member)
		maplist.append(my_map)
	difflist = []
	maplist1 = maplist[1:len(maplist)]
	for map in maplist:
		string1 = maplist[0].date
		string2 = map.date
		d1 = datetime.strptime(string1, '%Y-%m-%dT%H:%M:%S.%f')
		d2 = datetime.strptime(string2, '%Y-%m-%dT%H:%M:%S.%f')
		deltatime = d2-d1
		diff = deltatime.total_seconds()
		difflist.append(diff)
	return difflist
		


