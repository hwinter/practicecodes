import numpy as np
import os
from datetime import datetime
from datetime import timedelta
#
#
#
#
#Name: dih_event_range
#
#Purpose: given list of metadata for events starting at the same time, return cut off after which peaks should no longer be examined for relative channel separation
#
#Inputs: list of metadata for related events
#
#Outputs: Minimum length of lightcurve in seconds
#
#Example: min_seconds = dih_event_range(list_of_metadata)
#
#Written: 7/21/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_event_range(in_list):
	event_range_list = []
	for thing in in_list:
		begin = datetime.strptime(thing[0],'%Y-%m-%dT%H:%M:%S.%f')
		end = datetime.strptime(thing[-1],'%Y-%m-%dT%H:%M:%S.%f')
		range = end - begin
		event_range_list.append(range.total_seconds())
	min_range = min(event_range_list)
	return min_range
	
