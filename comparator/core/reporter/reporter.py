from core.scrapper.scrapper import Scrapper
from core.comparator.comparator import Comparator
import pandas as pd
from selenium import webdriver
import os
import csv
import collections

class Reporter(Scrapper,Comparator):

	def __init__(self,process_id,url_to_scrape_file,field_to_xpath_file,platform_import_file,output_file,comparision_report_file,logger,output_dir,comp_type,max_error_threshold):
		self.process_id = process_id
		self.url_to_scrape_file_df = pd.read_csv(url_to_scrape_file,dtype=object)
		self.field_identifier_file_df = pd.read_csv(field_to_xpath_file,dtype=object)
		self.platform_import_file = pd.read_csv(platform_import_file,dtype=object)
		self.platform_import_file.fillna(value='', inplace=True)
		# Scrapper file name
		self.output_file = output_file
		self.file_xpath_col_list = self.field_identifier_file_df.columns.tolist()

		# get dictionary from field and xpath
		#Unordered Dictionary
		# self.field_identifier_dict = self.field_identifier_file_df.set_index(self.file_xpath_col_list[0])[self.file_xpath_col_list[1]].to_dict()
		#Ordered Dictionary
		self.field_identifier_dict = collections.OrderedDict(zip(list(self.field_identifier_file_df[self.file_xpath_col_list[0]]),list(self.field_identifier_file_df[self.file_xpath_col_list[1]])))


		self.scrapped_data_file = pd.DataFrame(columns = [self.url_to_scrape_file_df.columns.tolist()[0]]+list(self.field_identifier_dict.keys()))
		#Extracting only Field names and not tags
		self.scrapped_data_file = pd.DataFrame(columns = [self.url_to_scrape_file_df.columns.tolist()[0]]+map(lambda x:x.split('|')[0],self.field_identifier_dict.keys()))
		self.logger = logger
		self.output_dir = output_dir
		self.comp_type = comp_type

		self.report_csv = pd.DataFrame(columns = self.platform_import_file.columns.tolist())
		self.comparision_report_file = comparision_report_file
		self.page_not_found_list = []
		self.invalid_url_list = []
		self.connection_issue_list = []

		self.total_error_count = 0
		self.max_error_threshold = max_error_threshold
		# self.driver = webdriver.Firefox()
		self.driver = webdriver.PhantomJS()

	def start_task(self):
		self.logger.info('ComparisonId = {} : Starting Immediate Reporter task'.format(self.process_id))
		try:
			self.url_to_scrape_file_df.fillna('',inplace=True)
			self.url_to_scrape_file_df.apply(self.start_immediate_reporter,axis =1)
		except Exception:
			# Incase immediate comparison is halted somewhere, the details upto that point is published.
			self.stop_task()


	def stop_task(self):
		try:
			self.driver.quit()
		except Exception as driverClosed:
			pass

		self.scrapped_data_file.to_csv(os.path.join(self.output_dir,self.output_file),index=False,quoting=csv.QUOTE_ALL)
		self.logger.info('ComparisonId = {} : Scrapping task completed'.format(self.process_id))
		self.logger.info('ComparisonId = {} : Comparision task completed'.format(self.process_id))
		report_file_name = os.path.join(self.output_dir,self.comparision_report_file)
		self.report_csv.to_csv(report_file_name,index=False,quoting=csv.QUOTE_ALL)
		self.logger.debug('ComparisonId = {} : Report generated to file {}'.format(self.process_id,report_file_name))
		self.logger.info('ComparisonId = {} : Total errors in file = {}'.format(self.process_id,self.total_error_count))


	def start_immediate_reporter(self,row):
		#Checking to see if the error count has reached maxed threshold
		if(self.total_error_count < self.max_error_threshold):
			get_scrapped_row = self.scrape_url(row)
			self.scrapped_data_file = self.scrapped_data_file.append(pd.Series(get_scrapped_row,index = self.scrapped_data_file.columns.tolist()),ignore_index=True)
			primary_id_column = str(row.index.tolist()[0])
			primary_id = row[primary_id_column]
			try:
				platform_row = self.platform_import_file[self.platform_import_file[self.platform_import_file.columns.tolist()[0]] == primary_id].iloc[0]
				get_comparison_row = self.compare_data(platform_row)
			except Exception:
				missing_report = self.get_missing_row_details(get_scrapped_row)
				get_comparison_row = missing_report
				self.total_error_count +=1
			get_comparison_row_series = pd.Series(get_comparison_row,index = self.platform_import_file.columns.tolist())
			self.report_csv = self.report_csv.append(get_comparison_row_series,ignore_index=True)
			# get_comparison_row_series.apply(self.get_total_error_count)
		else:
			return


	def get_missing_row_details(self,row):
		row_report = []
		primary_id = row[0]
		self.logger.info('ComparisonId = {} : missing row in platform file --> [{}]'.format(self.process_id,primary_id))
		row_report.append(primary_id)

		for row_column_id in range(1,len(row)):
			row_column_value = row[row_column_id]
			row_report.append(str(row_column_value)+', Product not present in provided url')
		return row_report
