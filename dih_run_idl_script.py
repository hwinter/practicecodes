import pidly
from dih_tableread import dih_filegrab2
import ast
#
#
#
#
#
#
#

def dih_run_idl_goes_script(start_time,end_time,save_name):
	idl = pidly.IDL('/proj/DataCenter/ssw/gen/setup/ssw_idl')
	idl.pro('dih_get_goes',start_time,end_time,save_name)
	print 'here'
	#txt_file = open(save_name,'r')
	#txt_lines = txt_file.readlines()
	#txt_header = ast.literal_eval(txt_lines[0])
	columns = dih_filegrab2(save_name)
	return zip(*columns)