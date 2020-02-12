import os
from datetime import datetime, timedelta
from shutil import copy
import re
import math

DATE_TIME_DELIM = '__'

def copy_file(src, dest):
	copy(src, dest)


def create_dir(dir_path):
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)


def get_current_time():
	now = datetime.now()
	return now.strftime("%d_%m_%Y__%H")
	# return '26_12_2019__12'


def get_current_date():
	"""
	The date format used here is DD_MM_YYYY_HH
	"""
	# return '12_02_2020__09'
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

def get_cleaned_name(value):
	return re.sub('[^A-Za-z0-9_]', ' ', value)


def get_region_name(region):
	if region == 'us-east-1':
		return 'US EAST(N. Virginia)'
	elif region == 'us-east-2':
		return 'US EAST(Ohio)'
	elif region == 'us-west-1':
		return 'US WEST(N. California)'
	else:
		return 'US WEST(Oregon)'


def get_store(row):
	url = row['PLA URL']
	store_name = row['PLA Store']
	if store_name!='':
		return store_name
	elif url=='':
		return url
	elif '/aclk' in url:
		return ''
	else:
		return url.split('/')[2]

def get_store_url(row):
	url = row['PLA URL']
	domain_url = row['PLA Domain']

	if domain_url!='':
		if 'google.com' in domain_url:
			return ''
		else:
			return domain_url
	elif url=='':
		return url
		
	elif '/aclk' in url:
		return ''
	else:
		return url.split('/')[2]

def get_file_size(file_path):
	"""
	Return files size from the file_path
	"""
	file_size_in_bytes = os.stat(file_path).st_size

	if file_size_in_bytes == 0:
		return "0B"

	size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
	i = int(math.floor(math.log(file_size_in_bytes, 1024)))
	p = math.pow(1024, i)
	s = round(file_size_in_bytes / p, 2)
	return "%s %s" % (s, size_name[i])