from django.conf import settings
import threading
import pandas as pd
from .models import ProjectComparator, ProjectUrl, ProjectXpath
import os
import time

class ProjectComparatorORM():

	def __init__(self,request,post_details,project,import_file_names):
		# threading.Thread.__init__(self)
		self.request = request
		self.post_details = post_details
		self.project = project
		self.import_file_names = import_file_names


	def insert_details_into_database(self):
		# print self.post_details
		# url_file = self.post_details['url_file'].name
		# xpath_file = self.post_details['xpath_file'].name
		# platform_import_file = self.post_details['platform_import_file'].name
		
		url_file = self.import_file_names[2]
		xpath_file = self.import_file_names[0]
		platform_import_file = self.import_file_names[1]
		run_priority = self.post_details['run_priority']

		if 'errcount' in self.request.POST and self.request.POST['errcount']:
			error_count = self.request.POST['errcount']
		else:
			error_count = 0
		current_timestamp = time.strftime("%Y%m%d-%H%M%S")
		project_scrapper_output_file = str(self.project)+'_'+'scrapped' +'_'+str(current_timestamp)+'.csv'
		project_report_file = str(self.project)+'_'+'report' +'_'+str(current_timestamp)+'.csv'
		new_project_comparison = ProjectComparator(project=self.project, user=self.request.user, project_url_file=url_file, project_xpath_file=xpath_file, project_platform_import_file=platform_import_file, run_priority=run_priority, project_status=ProjectComparator.RUN, error_count=error_count,project_scrapper_output_file=project_scrapper_output_file,project_report_file=project_report_file)
		new_project_comparison.save() # Calls signal from here
		self.process_id = new_project_comparison.id
		
	def get_project_comparator_id(self):
		return self.process_id




class ProjectUrlORM(threading.Thread):

	def __init__(self,url_file_name,project):
		threading.Thread.__init__(self)
		self.url_df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,url_file_name))
		self.project = project

	def run(self):
		self.url_df.apply(self.parse_url_file, axis=1)

	def parse_url_file(self,row):
		primary_id = row[row.index.tolist()[0]]
		row_url = row[row.index.tolist()[1]]
		new_project_url = ProjectUrl(project=self.project, primary_identifier=primary_id,url=row_url)
		new_project_url.save()



class ProjectXpathORM(threading.Thread):

	def __init__(self,xpath_file_name,project):
		threading.Thread.__init__(self)
		self.xpath_df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,xpath_file_name))
		self.project = project
		self.xpath_file_name = xpath_file_name

	def run(self):
		self.xpath_df.apply(self.parse_xpath_file, axis=1)
		

	def parse_xpath_file(self,row):
		field_name = row[row.index.tolist()[0]]
		xpath = row[row.index.tolist()[1]]
		new_project_url = ProjectXpath(project=self.project, field_name=field_name,xpath=xpath)
		new_project_url.save()

