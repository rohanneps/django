from datetime import datetime, timedelta

DATE_TIME_DELIM = '__'


def get_current_time():
	now = datetime.now()
	return now.strftime("%d_%m_%Y__%H")
	# return '26_12_2019__12'


def get_current_date():
	"""
	The date format used here is DD_MM_YYYY_HH
	"""
	# now = datetime.now()
	# return now.strftime("%d_%m_%Y__")
	# return '24_01_2020__08'
	return get_current_time()


def get_current_est_time(date_time_stamp):
	""" 
	GMT to EST
	"""
	date_time_list = date_time_stamp.split(DATE_TIME_DELIM)
	if len(date_time_list)==1:
		# No hour delim here
		return date_time_list
	else:
		date_time_obj = datetime.strptime(date_time_stamp, '%d_%m_%Y__%H')
		est_date_time_obj = date_time_obj - timedelta(hours=5)
		return est_date_time_obj.strftime("%d_%m_%Y__%H")


def convert_s3_to_email_format(date_time_stamp):
	""" 
	Convert s3 EST format to email format
	"""
	date_time_list = date_time_stamp.split(DATE_TIME_DELIM)
	if len(date_time_list)==1:
		# No hour delim here
		return datetime.strptime(date_time_stamp, "%d_%m_%Y").strftime("%m:%d:%Y")
	else:
		return datetime.strptime(date_time_stamp, "%d_%m_%Y__%H").strftime("%m-%d-%Y_%H")

