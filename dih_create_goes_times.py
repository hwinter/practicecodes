from datetime import datetime
from datetime import timedelta
#
#
#
#
#
def dih_create_goes_times(time_list):
	month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	new_time_list = []
	time_diff_list = []
	for member in time_list:
		index_list = [i for i, j in enumerate(month_list) if j == member[3:6]]
		new_member = member[0:3]+str(index_list[0]+1)+member[6:22]
		new_time_list.append(new_member)
	for member in new_time_list:
		first_time = datetime.strptime(new_time_list[0],'%d-%m-%Y %H:%M:%S.%f)
		now_time = datetime.strptime(member,'%d-%m-%Y %H:%M:%S.%f)
		diff = now_time-first_time
		diff_num = diff.total_seconds()
		time_diff_list.append(diff_num)
	return new_time_list