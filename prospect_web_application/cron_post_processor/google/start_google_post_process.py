from core.step1_download_pc_s3_file_class import S3PcDownloaderThread

from core.step2_generateSponsoredReport_pc_class import PcSponsoredResultProcessorThread

from core.step3_download_mobile_s3_file_class import S3MobileDownloaderThread

from core.step4_a_generateSponsoredAds_mobile import main as step4a_main
from core.step4_b_generateRegionSponsoredAdsReport_mobile import main as step4b_main
from core.step4_c_generateSponsoredAdsReport_RegionMerged_mobile import main as step4c_main

from core.step5_a_generateShowcaseAds_mobile import main as step5a_main
from core.step5_b_generateRegionShowcaseAdsReport_mobile import main as step5b_main
from core.step5_c_generateShowcaseAdsReport_RegionMerged_mobile import main as step5c_main

from core.step6_merge_sponsored_showcase_all import main as step6_main

from core.step7_a_aclkRedirect_http_class  import main as step7a_main
from core.step7_b_getAclkRedirectAndRecompute_rem_selenium import main as step7b_main

from GlobalVariables import (
								DESTINATION_ROOT_PATH,
								ADS_COMPUTED_OUTPUT_FILE_PATH,
								ADS_COMPUTED_OUTPUT_FILE,
								BASE_DIR,
								CURRENT_DATE_STAMP,
								LOG_DIR,
								LOG_FILE,
								SERVER,
								OUTPUT_DATE_DIR,
								PLATFORM
							)
import os
import time
from helper import copy_file, get_file_size, create_dir
from db_helper.db_helper import insert_computed_file_to_db
import shutil
from db_helper.db_base import DBConnector
from db_helper.table_classes import ProspectDetails, GoogleRunDetails

class PostProcessor():

	def __init__(self):
		# DB objects
		self.platform = PLATFORM
		db_connector_obj = DBConnector()
		self.engine = db_connector_obj.get_engine()
		Session = db_connector_obj.get_session()
		self.session = Session()

	def setClient(self, client, client_file_name):
		self.client = client
		self.client_file_name = client_file_name

	def setRunDetailsObject(self, run_details_obj):
		self.run_details_obj = run_details_obj

	def getActiveProspectCronJobsToPostProcess(self):
		# return self.session.query(GoogleRunDetails).filter(GoogleRunDetails.prospect.has(ProspectDetails.platform == self.platform))\
		# 		.filter(GoogleRunDetails.post_process_completed == False).all()
		return self.session.query(GoogleRunDetails).filter(GoogleRunDetails.post_process_completed == False).all()


	def CopyFileToDestinationDir(self):
		"""
		Copies computed file to mounted s3 location on ec2
		"""
		src_file_path = os.path.join(BASE_DIR, ADS_COMPUTED_OUTPUT_FILE_PATH.format(self.client))
		client_output_dir = DESTINATION_ROOT_PATH.format(self.client)
		create_dir(client_output_dir)
		dest_file_path = os.path.join(client_output_dir, ADS_COMPUTED_OUTPUT_FILE)
		if os.path.exists(src_file_path):
			copy_file(src_file_path, dest_file_path)
			return dest_file_path
		else:
			return None

	def persistClientDateTimeLogFile(self):
		CRON_LOG_FILE_PATH = os.path.join(BASE_DIR, LOG_DIR, LOG_FILE)
		DATE_TIME_STAMP_LOG_FILE_PATH = os.path.join(BASE_DIR, LOG_DIR, '{}_{}.log'.format(self.client, CURRENT_DATE_STAMP))
		copy_file(CRON_LOG_FILE_PATH, DATE_TIME_STAMP_LOG_FILE_PATH)

	def updateRunDetailsObject(self):
		self.run_details_obj.file_size = self.dest_file_size
		self.run_details_obj.total_pla_records = self.total_sponsored_records
		self.run_details_obj.total_showcase_records = self.total_showcase_records
		self.run_details_obj.post_process_completed = True
		self.session.add(self.run_details_obj)
		self.session.commit()

	def cleanResourcesForClient(self):
		self.dest_file_size = 0
		self.total_sponsored_records = 0
		self.total_showcase_records = 0
		self.client = None
		self.client_file_name = None
		self.run_details_obj = None

	def startProcess(self):
		# For PC page sources
		print('Starting Step1: Downloading Sponsored Results of PC from s3')
		# download PC sponsored results
		step1_thread = S3PcDownloaderThread('Step1 Thread', self.client)
		step1_thread.start()
		print('-----------------------------------------')

		# For Mobile page sources
		print('Starting Step3: Downloading Page Sources of Mobile from s3')
		# download mobile page source
		step3_thread = S3MobileDownloaderThread('Step3 Thread', self.client)
		step3_thread.start()

		step1_thread.join()
		print('-----------------------------------------')
		print('Starting Step2: Processing Sponsored Results PC')
		step2_thread = PcSponsoredResultProcessorThread('Step2 Thread', self.client)
		step2_thread.start()
		print('-----------------------------------------')



		step3_thread.join()
		print('-----------------------------------------')
		print('Starting Step4a: Processing Sponsored Results Mobile')
		step4a_main(self.client)
		print('-----------------------------------------')
		print('Starting Step4b')
		step4b_main(self.client)
		print('-----------------------------------------')
		print('Starting Step4c')
		step4c_main(self.client)
		print('-----------------------------------------')
		print('Starting Step5a: Processing Showcase Results Mobile')
		step5a_main(self.client)
		print('-----------------------------------------')
		print('Starting Step5b')
		step5b_main(self.client)
		print('-----------------------------------------')
		print('Starting Step5c')
		step5c_main(self.client)

		# Waiting for intermediate threads to stop
		step2_thread.join()
		print('-----------------------------------------')
		# Merging PLA/Showcase for pc and mobile
		print('Starting Step6: Merging PLA/Showcase of pc and mobile')
		step6_main(self.client, self.client_file_name)
		print('-----------------------------------------')
		

		# aclk redirect
		print('Starting Step7a: Aclk redirect HTTP')
		step7a_main(self.client)
		print('-----------------------------------------')
		print('Starting Step7b: Aclk redirect Selenium')
		step7b_main(self.client)
		print('Process Completed')
		print('-----------------------------------------')

		# print('Copying computed batch to sftp s3 location')
		dest_file_path = self.CopyFileToDestinationDir()

		if dest_file_path:
			## Postgres DB insert
			print('Inserting Computed File to database')
			self.total_sponsored_records, self.total_showcase_records = insert_computed_file_to_db(self.engine, dest_file_path, self.client, 'Google')

			## Get file size
			self.dest_file_size = get_file_size(dest_file_path)


		print('Task terminated')

		if SERVER:
			self.persistClientDateTimeLogFile()
		shutil.rmtree(OUTPUT_DATE_DIR.format(self.client))


if __name__ == '__main__':

	print('For datetime: {}'.format(CURRENT_DATE_STAMP))
	post_processor_obj = PostProcessor()
	active_prospects_to_post_process = post_processor_obj.getActiveProspectCronJobsToPostProcess()

	print('Number of post processing jobs for platform {} : {}'.format(PLATFORM, len(active_prospects_to_post_process)))
	# exit(1)
	print('#############################################################################')
	for post_process_jobs in active_prospects_to_post_process:
		client = post_process_jobs.prospect.name
		client_file_name = post_process_jobs.prospect.file_name
		client = client.replace('/','_')
		print('For client: {}'.format(client))
		start_time = time.time()
		post_processor_obj.setClient(client, client_file_name)
		post_processor_obj.setRunDetailsObject(post_process_jobs)
		post_processor_obj.startProcess()
		post_processor_obj.updateRunDetailsObject()
		post_processor_obj.cleanResourcesForClient()
		end_time = time.time()
		print('Total time: {}'.format(end_time-start_time))
		print('----------------------------------------------------------------------------------------')