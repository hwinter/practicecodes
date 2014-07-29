from datetime import datetime
from datetime import timedelta

#
#Name: dih_ev_peak_compare
#
#Purpose: compares a list of time strings and compares them to a peak time from an event file and finds the closest peak
#
#


def dih_ev_peak_compare(peaklist,ev_peak_time):
	peaklist = list(set(peaklist))
	peaklist_datetimes = []
	time_differences = []
	ev_peak_time = datetime.strptime(ev_peak_time,'%Y-%m-%dT%H:%M:%S')
	for member in peaklist:
		member_dt = datetime.strptime(member,'%Y/%m/%d %H:%M:%S.%f')
		peaklist_datetimes.append(member_dt)
		delt = member_dt - ev_peak_time
		delt_num = abs(delt.total_seconds())
		time_differences.append(delt_num)
	min_list = [i for i, j in enumerate(time_differences) if j == min(time_differences)]
	return peaklist_datetimes[min_list[0]]