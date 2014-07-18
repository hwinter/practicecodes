import csv
import numpy as np
import ast
from itertools import islice
from datetime import datetime
from datetime import timedelta
#Name: dih_goes_csv_reader
#
#Purpose: reads csv containing data on all flares and produces a list of events
#
#Inputs:file contains csv data from Hinode Flare Catalogue
#
#Outputs:csv data in list of lists form
#
#Example: goes_events = dih_goes_csv_reader('/home/dherman/Documents/flare.csv')
#
#Written: 7/16/14 Dan Herman	daniel.herman@cfa.harvard.edu
#




def dih_goes_csv_reader(filename):
	event_list = []
	with open(filename, 'rb') as csvfile:
		goesreader = csv.reader(csvfile)
		for row in islice(goesreader,1,None):
			event_string = '["' + '","'.join(row) + 'N/A' + '"]'
			event_sublist = ast.literal_eval(event_string)
			event_list.append(event_sublist)
	return event_list
#
#
#Name: dih_goes_csv_compare
#
#Purpose: takes time range outputs peaks of GOES events that fall within that time range
#
#Inputs: start time (time1), end time (time2), file containing data (filename)
#
#Outputs: list of events in time range
#
#Example: related_events = dih_goes_csv_compare(datetime(2007, 12, 6, 15, 29, 43, 79060),datetime(2007, 12, 7, 15, 29, 43, 79060),'/home/dherman/Documents/flare.csv')
#
#Written: 7/16/14 Dan Herman daniel.herman@cfa.harvard.edu
#

def dih_goes_csv_compare(time1,time2,filename):
	event_list = dih_goes_csv_reader(filename)
	time_interval = time1 - time2
	if time_interval.total_seconds() >= 0:
		print 'Bad Times!'
		return 11
	goes_peak_list = []
	for idx,event in enumerate(event_list):
		peaktime = datetime.strptime(event[3], '%Y/%m/%d %H:%M')
		if peaktime > time1 and peaktime < time2:
			goes_peak_list.append(event)
	return goes_peak_list
#
#
#
#Name: dih_goes_csv_checker
#
#Needs Documentation!

def dih_goes_csv_checker(filename,csvfilename):
	file = open(filename,'r')
	AIA_events = file.readlines()
	GOES_events = []
	for idx,member in enumerate(AIA_events):
		member = ast.literal_eval(member)
		peaklist = []
		for guy in member[4]:
			timeval = datetime.strptime(member,'%Y/%m/%d %H:%M:%S.%f')
			peaklist.append(timeval)
		for peak in peaklist:
			time1 = peak - timedelta(seconds = 300)
			time2 = peak + timedelta(seconds = 300)
			subeventlist = dih_goes_csv_compare(time1,time2,csvfilename)
			if len(subeventlist) > 0:
				subeventlist.append('GOES event present')
				print "Found Goes Event(s) near AIA Event"
			else:
				subeventlist.append('GOES event absent')
				print "No Goes Event near AIA Event"
			GOES_events.append([member,subeventlist])
			savefile = open('/data/george/dherman/metadata/all_GOES_events.txt','a')
			simplejson.dump([member,subeventlist],savefile)
			savefile.close()
	return GOES_events