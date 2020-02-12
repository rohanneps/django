from core.step1_download_pc_s3_file_class import S3PcDownloaderThread

from core.step2_generate_RelatedBrands_pc import RelatedBrandsHandler
from core.step3_generate_AmazonChoices_pc import AmazonChoicesHandler
from core.step4_generate_SponsoredResults_pc import SponsoredResultsHandler
from core.step5_generate_TodayDeals_pc import TodayDealsHandler
from core.step6_generate_EditorialRecommedation_pc import EditorialRecommendationHandler
from core.step7_generate_OrganicResults_pc import OrganicResultsHandler


from GlobalVariables import (
								DESTINATION_ROOT_PATH,
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
import shutil
from db_helper.db_base import DBConnector
from db_helper.table_classes import ProspectDetails, AmazonRunDetails

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
		# return self.session.query(AmazonRunDetails).filter(AmazonRunDetails.prospect.has(ProspectDetails.platform == self.platform))\
		# 		.filter(AmazonRunDetails.post_process_completed == False).all()
		return self.session.query(AmazonRunDetails).filter(AmazonRunDetails.post_process_completed == False).all()

	def persistClientDateTimeLogFile(self):
		CRON_LOG_FILE_PATH = os.path.join(BASE_DIR, LOG_DIR, LOG_FILE)
		DATE_TIME_STAMP_LOG_FILE_PATH = os.path.join(BASE_DIR, LOG_DIR, '{}_{}.log'.format(self.client, CURRENT_DATE_STAMP))
		copy_file(CRON_LOG_FILE_PATH, DATE_TIME_STAMP_LOG_FILE_PATH)

	def updateRunDetailsObject(self):
		self.run_details_obj.total_amazon_choices_records = self.total_amazon_choices
		self.run_details_obj.total_brands_related_records = self.total_related_brands
		self.run_details_obj.total_editorial_recommendations_records = self.total_editorial_recommendations
		self.run_details_obj.total_organic_records = self.total_organic_results
		self.run_details_obj.total_sponsored_records = self.total_sponsored_results
		self.run_details_obj.total_today_deals_records = self.total_today_deals
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
		step1_thread.join()

		print('-----------------------------------------')
		print('Starting Step2: Processing Brands Related')
		related_brands_handler_obj = RelatedBrandsHandler(self.engine, self.client, self.client_file_name)
		self.total_related_brands = related_brands_handler_obj.main()
		print('-----------------------------------------')

		print('Starting Step3: Processing Amazon Choices')
		amazon_choices_handler_obj = AmazonChoicesHandler(self.engine, self.client, self.client_file_name)
		self.total_amazon_choices = amazon_choices_handler_obj.main()
		print('-----------------------------------------')

		print('Starting Step4: Processing Sponsored Results')
		sponsored_results_handler_obj = SponsoredResultsHandler(self.engine, self.client, self.client_file_name)
		self.total_sponsored_results = sponsored_results_handler_obj.main()
		print('-----------------------------------------')
		
		print('Starting Step5: Processing Today Deals')
		today_deals_handler_obj = TodayDealsHandler(self.engine, self.client, self.client_file_name)
		self.total_today_deals =today_deals_handler_obj.main()
		print('-----------------------------------------')

		print('Starting Step6: Processing Editorial Recommendations')
		editorial_recommendation_handler_obj = EditorialRecommendationHandler(self.engine, self.client, self.client_file_name)
		self.total_editorial_recommendations = editorial_recommendation_handler_obj.main()
		print('-----------------------------------------')

		print('Starting Step7: Processing Organic Results')
		organic_results_handler_obj = OrganicResultsHandler(self.engine, self.client, self.client_file_name)
		self.total_organic_results = organic_results_handler_obj.main()
		print('-----------------------------------------')

		print('Process Completed')
		print('-----------------------------------------')


		if SERVER:
			self.persistClientDateTimeLogFile()
		shutil.rmtree(OUTPUT_DATE_DIR.format(self.client))


if __name__ == '__main__':

	print('For datetime: {}'.format(CURRENT_DATE_STAMP))
	post_processor_obj = PostProcessor()
	active_prospects_to_post_process = post_processor_obj.getActiveProspectCronJobsToPostProcess()

	print('Number of post processing jobs for platform {} : {}'.format(PLATFORM, len(active_prospects_to_post_process)))
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
		# exit(1)
		post_processor_obj.updateRunDetailsObject()
		post_processor_obj.cleanResourcesForClient()
		end_time = time.time()
		print('Total time: {}'.format(end_time-start_time))
		print('----------------------------------------------------------------------------------------')