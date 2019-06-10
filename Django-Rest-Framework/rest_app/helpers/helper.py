import pandas as pd
import os
from django.conf import settings
import datetime
from shutil import copy


def copy_file(src, dest):
	copy(src, dest)

def create_dir(dir_path):
	if not os.path.exists(dir_path):
		os.mkdir(dir_path)



def check_input_file_exists(project_id, file_location):
	# project_dir = os.path.join(settings.PROJECT_DIR,str(project_id))
	# project_file_location = os.path.join(project_dir, settings.PROJECT_INPUT_FOLDER,file_location)
	
	# file_format = file_location.split('.')[-1]
	project_file_location = os.path.join(settings.PROJECT_INPUT_FOLDER, file_location)

	if os.path.exists(project_file_location):
		return True
	return False



def get_unique_products_and_total_count(file_name):
	"""
	Return Total row count and Unique product count for a given file
	"""
	# project_dir = os.path.join(settings.PROJECT_DIR,file_name)
	# project_file_location = os.path.join(project_dir, settings.PROJECT_INPUT_FOLDER,file_location)

	project_file_location = os.path.join(settings.PROJECT_INPUT_FOLDER, file_name)

	df = pd.read_csv(project_file_location, sep='\t', encoding='ISO-8859-1', dtype=object)
	column_list = df.columns.tolist()
	total_count = len(df)
	total_unique_products = len(df['s_item_name'].unique().tolist())

	# adding system index to file
	if 'sys_index' in df.columns.tolist():
		del df['sys_index']
	df['sys_index'] = range(1, total_count+1)

	df = df[['sys_index']+column_list]
	df.to_csv(project_file_location, index=False,sep='\t', encoding='ISO-8859-1')

	return total_count, total_unique_products


def get_from_date_to_date_format(from_date, to_date):
	from_date_list = from_date.split('/')
	to_date_list = to_date.split('/')
	from_date = '{}-{}-{}'.format(from_date_list[2],from_date_list[0],from_date_list[1])
	to_date = '{}-{}-{} {}-{}-{}'.format(to_date_list[2],to_date_list[0],to_date_list[1],23,59,59)

	format_str = '%Y-%m-%d' # The date format
	format_to_date_str = '%Y-%m-%d %H-%M-%S' # The date format
	from_date = datetime.datetime.strptime(from_date, format_str)
	to_date = datetime.datetime.strptime(to_date, format_to_date_str)
	return from_date, to_date

def get_total_project_count(project):
	return len(project)

def get_project_phase_completion(project_phase):
	project_phase = int(project_phase)
	total_phases = len(list(settings.PROJECT_PROCESS_STATUS_DICT.keys()))
	percentage_completed = '{0:.2f}%'.format((project_phase/total_phases)*100)
	return percentage_completed


def terminate_async_task(task_id):
	from celery.task.control import revoke
	revoke(task_id, terminate=True)



def get_project_match_notmatch_count(project_id):
	"""
	Return Total count of matched and non-matched combination for project
	"""
	project_dir = os.path.join(settings.PROJECT_DIR,str(project_id))
	project_file_location = os.path.join(project_dir,settings.PROJECT_STEP_FOLDER,settings.PROJECT_STEP_FOLDER_7,settings.PROJECT_STEP_FILE_7.format(project_id))

	df = pd.read_csv(project_file_location, sep='\t', encoding='ISO-8859-1')
	total_matched_count = len(df[df['Result']=='Match'])
	total_notmatched_count = len(df)-total_matched_count
	return total_matched_count, total_notmatched_count


def get_current_date():
	today = datetime.date.today()
	return today.strftime("%m/%d/%Y")