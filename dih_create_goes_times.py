from datetime import datetime
from datetime import timedelta
#
#
#Needs Docs!
#
#Name: dih_create_goes_times
#
#Purpose: takes times created by IDL goes finder and puts them in '%d-%m-%Y %H:%M:%S.%f' format
#
#Inputs: list of GOES times
#
#Outputs: list of AIA suitable times
#
#Examples gah = dih_create_goes_times(['01-May-2012 00:00:00.00'])
#
#Written: 8/1/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
#
def dih_create_goes_times(time_list):
	month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	new_time_list = []
	time_diff_list = []
	for member in time_list:
		index_list = [i for i, j in enumerate(month_list) if j == member[3:6]]
		new_member = member[0:3] + str(index_list[0]+1) + '-20' + member[7:22]
		new_time_list.append(new_member)
	#for member in new_time_list:
		#first_time = datetime.strptime(new_time_list[0],'%d-%m-%Y %H:%M:%S.%f')
		#now_time = datetime.strptime(member,'%d-%m-%Y %H:%M:%S.%f')
		#diff = now_time-first_time
		#diff_num = diff.total_seconds()
		#time_diff_list.append(diff_num)
	return new_time_list