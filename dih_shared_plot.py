import matplotlib.pyplot as plt
import numpy as np
import simplejson
import ast
from datetime import datetime
from datetime import timedelta	
import dih_tableread as grab
import matplotlib.cm as cm
#
#Name: dih_shared_groups
#
#Purpose: places all metadata from events in a text file into groups based on common start time
#
#Inputs: text file containing meta data in the form of lists
#
#Outputs: list of list of times that start within 2 minutes of each other
#
#Example: shared_times = dih_shared_group('meta.txt')
#
#Written:7/16/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#

def dih_shared_groups(metadatafile):
	working_file = open(metadatafile,'r')
	working_lines = working_file.readlines()
	events = []
	#Turn strings into lists
	for idx,member in enumerate(working_lines):
		member = ast.literal_eval(member)
		events.append(member)
	shared_times = []
	#Compare times to see which ones are within 2 minutes of each other
	for idx,member in enumerate(events):
		print type(member)
		#consider increasing shared time limit
		subshared_events = [j for j, j in enumerate(events) if abs((datetime.strptime(j[0],'%Y-%m-%dT%H:%M:%S.%f')-datetime.strptime(member[0],'%Y-%m-%dT%H:%M:%S.%f')).total_seconds()) < 120]
		subshared_times = []
		for member in subshared_events:
			subshared_times.append(member[0])
		shared_times.append(tuple(set(tuple(subshared_times))))
	shared_times = list(set(shared_times))
	return shared_times
	
	
		
#def dih_shared_groups_plot(metadatafile,savename):
	#shared_times = dih_shared_groups(metadatafile)
	#for idx,member in enumerate(shared_times):
		#for guy in member:
			#columns = grab.dih_filegrab('/data/george/dherman/rawdata/' + guy + '*.txt'
			#colors = iter(cm.rainbow(np.linspace(0,1,len(member))))
			#print columns
		#print 'here'
	#return shared_times
					
	