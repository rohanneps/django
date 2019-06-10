from threading import Thread
import logging
import os
from django.conf import settings
from core.image_download_helper import downloadSearchImageHelper, downloadResultImageHelper
from core.main_code import Step0_GetRequiredFields, Step6_MergeAll_price_image_text_conf,Step7_AppendScoreDetails
from core.main_code.Step2_Color_Classifier import ImageColorClassifier
from core.main_code import Step1_ImagenetHelper
from core.main_code.Step4_PriceDiff_Calculator import PriceDiffereCalculator
from core.main_code.Step5_TextConfidence_Generator import TextConfidenceGenerator
from helpers import helper, ftp_helper
import traceback

comp_logger = logging.getLogger(__name__)


class ProjectProcessHandler():

	def __init__(self, project, project_status):
		# Thread.__init__(self)
	
		self.project = project
		self.project_status = project_status
		self.project_id = self.project.id

		# creating directory for project
		project_dir = os.path.join(settings.PROJECT_DIR,str(self.project_id))
		helper.create_dir(project_dir)
		project_input_dir = os.path.join(project_dir,settings.PROJECT_PROCESS_INPUT_FOLDER)
		helper.create_dir(project_input_dir)

		# creating image directories
		self.image_download_main_dir = os.path.join(settings.PROJECT_DIR, str(self.project_id),settings.PROJECT_IMAGES_FOLDER)
		helper.create_dir(self.image_download_main_dir)
		# self.input_conf_file_path = os.path.join(settings.MEDIA_ROOT,settings.INPUT_DIR,self.project.file)
		
		
		# file_format = project.file_name.split('.')[-1]
		# global_project_input_file_path = os.path.join(settings.FTP_ROOT_FOLDER_LOCATION,settings.PROJECT_INPUT_FILE_PATTERN.format(self.project_id, file_format))
		global_project_input_file_path = os.path.join(settings.FTP_ROOT_FOLDER_LOCATION,self.project.file_name)

		self.input_conf_file_path = os.path.join(project_input_dir,project.file_name)


		if not os.path.exists(self.input_conf_file_path):
			# copy remote project input file to local
			self.copy_project_input_file(global_project_input_file_path, self.input_conf_file_path)	
		

		self.output_dir = os.path.join(settings.PROJECT_DIR, str(self.project_id),settings.PROJECT_STEP_FOLDER)
		helper.create_dir(self.output_dir)

	def copy_project_input_file(self, src_file_loc, dest_file_loc):
		# copy project input file from input collection folder
		# helper.copy(src_file_loc, dest_file_loc)
		try:
			ftp_helper.copy_ftp_file_over_sftp_using_key(src_file_loc, dest_file_loc)	
		except Exception as e:
			comp_logger.info(str(e))
			comp_logger.info('FTP file transfer exception for project id:  {}'.format(self.project_id))
			self.update_project_status_failed('FTP file transfer exception, '+ str(e))
			traceback_error = traceback.format_exc()
			comp_logger.info(traceback_error)

	def start(self):
		comp_logger.info('Process started for project id: {}'.format(self.project_id))

		#Image Download
		self.download_images()

		self.get_base_file()
		self.start_imagenet_classification()
		self.start_color_classification()
		self.price_difference_calculation()
		self.text_confidence_generation()
		self.merge_computation()
		self.append_score_details()
		self.insert_computed_output_into_elasticsearch()


		if self.project.status == 'Failed':
			comp_logger.info('Product Matching Process exception for id: {}'.format(self.project_id))
		else:
			comp_logger.info('Product Matching Process completed for id: {}'.format(self.project_id))
		
	def change_project_status(self,state):
		# changing project status
		if self.project.status != 'Failed':
			self.project_status.project_phase = state
			self.project_status.project_completion_percentage = helper.get_project_phase_completion(state)
			self.project_status.save()


	def download_images(self):
		# Search Image Download Section
		comp_logger.info('Search image downloader started for project id: {}'.format(self.project_id))
		image_download_dir = os.path.join(self.image_download_main_dir,settings.PROJET_SEARCH_IMAGES_FOLDER)
		helper.create_dir(image_download_dir)
		try:
			downloadSearchImageHelper.main(self.input_conf_file_path,image_download_dir)
			comp_logger.info('Search image downloader completed for project id: {}'.format(self.project_id))
		except Exception as e:
			comp_logger.info(str(e))
			comp_logger.info('Search image downloader exception for project id:  {}'.format(self.project_id))
			traceback_error = traceback.format_exc()
			comp_logger.info(traceback_error)

		# Result Image Download Section
		comp_logger.info('Result image downloader started for project id: {}'.format(self.project_id))
		image_download_dir = os.path.join(self.image_download_main_dir,settings.PROJET_RESULT_IMAGES_FOLDER)
		helper.create_dir(image_download_dir)
		try:
			self.result_image_file_path = os.path.join(self.image_download_main_dir, settings.PROJECT_RESULT_IMAGE_MAPPER)
			downloadResultImageHelper.main(self.input_conf_file_path,image_download_dir,self.result_image_file_path)
			comp_logger.info('Result image downloader completed for project id: {}'.format(self.project_id))
			self.change_project_status('2')
		except Exception as e:
			comp_logger.info(str(e))
			comp_logger.info('Result image downloader exception for project id:  {}'.format(self.project_id))
			traceback_error = traceback.format_exc()
			comp_logger.info(traceback_error)
	
	def update_project_status_failed(self, error_message):
		if self.project.status != 'Failed':
			self.project.status = 'Failed'
			self.project.failed_log = error_message
			self.project.save()

	def project_status_not_failed(self):
		if self.project.status != 'Failed':
			return True
		else:
			return False

	def get_base_file(self):
		comp_logger.info('Initiating Step 0 for project id: {}'.format(self.project_id))
		self.output_dir_step0 = os.path.join(self.output_dir,settings.PROJECT_STEP_FOLDER_0)
		helper.create_dir(self.output_dir_step0)
		try:
			Step0_GetRequiredFields.main(self.input_conf_file_path, self.output_dir_step0, settings.PROJECT_STEP_FILE_0, self.result_image_file_path)
			comp_logger.info('Step 0 completed for project id: {}'.format(self.project_id))
		except Exception as e:
			comp_logger.info(str(e))
			comp_logger.info('Step 0 exception for project id:  {}'.format(self.project_id))
			self.update_project_status_failed('Step 0 exception, '+ str(e))
			traceback_error = traceback.format_exc()
			comp_logger.info(traceback_error)

	def start_imagenet_classification(self):
		if self.project_status_not_failed():
			comp_logger.info('Initiating Imagenet Classification for project id: {}'.format(self.project_id))
			output_dir_step1 = os.path.join(self.output_dir,settings.PROJECT_STEP_FOLDER_1)
			helper.create_dir(output_dir_step1)
			input_file_path = os.path.join(self.output_dir_step0, settings.PROJECT_STEP_FILE_0)
			
			try:
				Step1_ImagenetHelper.main(input_file_path, output_dir_step1, self.image_download_main_dir, self.project_id)
				comp_logger.info('Imagenet Classification completed for project id: {}'.format(self.project_id))
				self.change_project_status('3')
			except Exception as e:
				comp_logger.info(str(e))
				comp_logger.info('Imagenet Classification exception for project id:  {}'.format(self.project_id))
				self.update_project_status_failed('Imagenet Classification exception, '+ str(e))
				traceback_error = traceback.format_exc()
				comp_logger.info(traceback_error)
		else:
			comp_logger.info('Imagenet Classification skipped for project id: {} due to failed project status'.format(self.project_id))
		


	def start_color_classification(self):
		if self.project_status_not_failed():
			comp_logger.info('Initiating Color Classification for project id: {}'.format(self.project_id))
			output_dir_step2 = os.path.join(self.output_dir,settings.PROJECT_STEP_FOLDER_2)
			helper.create_dir(output_dir_step2)
			input_file_path = os.path.join(self.output_dir_step0, settings.PROJECT_STEP_FILE_0)
			output_file_path = os.path.join(output_dir_step2, settings.PROJECT_STEP_FILE_2)
			# print(self.image_download_main_dir)
			
			if not os.path.exists(output_file_path):
				try:
					color_classifier = ImageColorClassifier(input_file_path, output_file_path, self.image_download_main_dir)
					color_classifier.start()
					comp_logger.info('Color Classification completed for project id: {}'.format(self.project_id))
					self.change_project_status('4')
				except Exception as e:
					comp_logger.info(str(e))
					comp_logger.info('Color Classification exception for project id:  {}'.format(self.project_id))
					self.update_project_status_failed('Color Classification exception, '+ str(e))
					traceback_error = traceback.format_exc()
					comp_logger.info(traceback_error)

			else:
				comp_logger.info('Color classification already completed for project id: {}. Restart process'.format(self.project_id))		
		else:
			comp_logger.info('Color Classification skipped for project id: {} due to failed project status'.format(self.project_id))


	def price_difference_calculation(self):
		if self.project_status_not_failed():
			comp_logger.info('Initiating Price Diff Calculation for project id: {}'.format(self.project_id))
			output_dir_step4 = os.path.join(self.output_dir,settings.PROJECT_STEP_FOLDER_4)
			helper.create_dir(output_dir_step4)
			input_file_path = self.input_conf_file_path
			output_file_path = os.path.join(output_dir_step4, settings.PROJECT_STEP_FILE_4)
			
			if not os.path.exists(output_file_path):
				try:
					# Step4_PriceDiff_Calculation.main(input_file_path, output_file_path)
					price_diff_calculator = PriceDiffereCalculator(input_file_path, output_file_path)
					price_diff_calculator.main()
					comp_logger.info('Price Diff Calculation completed for project id: {}'.format(self.project_id))
					self.change_project_status('5')
				except Exception as e:
					comp_logger.info(str(e))
					comp_logger.info('Price Diff Calculation exception for project id:  {}'.format(self.project_id))
					self.update_project_status_failed('Price Diff Calculation exception, '+ str(e))
					traceback_error = traceback.format_exc()
					comp_logger.info(traceback_error)
			else:
				comp_logger.info('Price Differece calculation already completed for project id: {}. Restart process'.format(self.project_id))		
		else:
			comp_logger.info('Price Diff Calculation skipped for project id: {} due to failed project status'.format(self.project_id))

	def text_confidence_generation(self):
		if self.project_status_not_failed():
			comp_logger.info('Initiating Text Confidence computation for project id: {}'.format(self.project_id))
			output_dir_step5 = os.path.join(self.output_dir,settings.PROJECT_STEP_FOLDER_5)
			helper.create_dir(output_dir_step5)
			input_file_path = self.input_conf_file_path
			output_file_path = os.path.join(output_dir_step5, settings.PROJECT_STEP_FILE_5)

			if not os.path.exists(output_file_path):
				try:
					# Step5_TextConfidence_Generation.main(input_file_path, output_file_path)
					text_conf_generator = TextConfidenceGenerator(input_file_path, output_file_path)
					text_conf_generator.main()
					comp_logger.info('Text confidence Computation completed for project id: {}'.format(self.project_id))
					self.change_project_status('6')
				except Exception as e:
					comp_logger.info(str(e))
					comp_logger.info('Text confidence Computation exception for project id:  {}'.format(self.project_id))
					self.update_project_status_failed('Text confidence Computation exception, '+ str(e))
					traceback_error = traceback.format_exc()
					comp_logger.info(traceback_error)
			else:
				comp_logger.info('Text confidence computation already completed for project id: {}. Restart process'.format(self.project_id))		
		else:
			comp_logger.info('Text confidence Computation skipped for project id: {} due to failed project status'.format(self.project_id))



	def merge_computation(self):
		"""
		Merge previous steps records
		"""
		if self.project_status_not_failed():
			comp_logger.info('Initiating Image, Price, Text Confidence merger for project id: {}'.format(self.project_id))
			self.output_dir_step6 = os.path.join(self.output_dir,settings.PROJECT_STEP_FOLDER_6)
			helper.create_dir(self.output_dir_step6)
			input_file_path = self.input_conf_file_path
			output_file_path = os.path.join(self.output_dir_step6, settings.PROJECT_STEP_FILE_6)
			
			try:
				Step6_MergeAll_price_image_text_conf.main(self.project.id, input_file_path, output_file_path)
				comp_logger.info('Image, Price, Text Confidence merger completed for project id: {}'.format(self.project_id))
			
			except Exception as e:
				comp_logger.info(str(e))
				comp_logger.info('Image, Price, Text Confidence merger exception for project id:  {}'.format(self.project_id))
				self.update_project_status_failed('Image, Price, Text Confidence merger exception, '+ str(e))
				traceback_error = traceback.format_exc()
				comp_logger.info(traceback_error)
		else:
			comp_logger.info('Image, Price, Text Confidence merger skipped for project id: {} due to failed project status'.format(self.project_id))


	def append_score_details(self):
		if self.project_status_not_failed():
			comp_logger.info('Initiating score details appender for project id: {}'.format(self.project_id))
			output_dir_step7 = os.path.join(self.output_dir,settings.PROJECT_STEP_FOLDER_7)
			helper.create_dir(output_dir_step7)

			input_file_path = self.input_conf_file_path
			step6_output_file_path = os.path.join(self.output_dir_step6, settings.PROJECT_STEP_FILE_6)
			self.step7_output_file_path = os.path.join(output_dir_step7, settings.PROJECT_STEP_FILE_7.format(self.project_id))
			try:
				Step7_AppendScoreDetails.main(project_id=self.project_id,client_input_file=input_file_path, step6_output_file=step6_output_file_path, output_file= self.step7_output_file_path)
				comp_logger.info('Score Details appender completed for project id: {}'.format(self.project_id))		
				self.project.status = 'Completed'
				self.project.save()
				self.change_project_status('7')
			except Exception as e:
				comp_logger.info(str(e))
				comp_logger.info('Score Details appender exception for project id:  {}'.format(self.project_id))
				self.update_project_status_failed('Score Details appender exception, '+ str(e))
				traceback_error = traceback.format_exc()
				comp_logger.info(traceback_error)
		else:
			comp_logger.info('Score Details appender skipped for project id: {} due to failed project status'.format(self.project_id))


	def insert_computed_output_into_elasticsearch(self):
		"""
			insert computed output to elasticsearch index
		"""
		if self.project_status_not_failed():
			comp_logger.info('Initiating ES bulk importer for project id: {}'.format(self.project_id))
			if os.path.exists(self.step7_output_file_path):
				from helpers import es_helper
				try:
					es_helper.insert_records_into_elasticsearch_index(index=settings.ES_COMPUTED_RESULT_INDEX, file_location=self.step7_output_file_path)
					comp_logger.info('ES insertion completed for project id: {} '.format(self.project_id))
				except Exception as e:
					exception = str(e)
					if len(exception)>1400:
						exception = exception[:1400]
					self.update_project_status_failed('Elasticsearch bulk insert exception, '+ exception)
					traceback_error = traceback.format_exc()
					comp_logger.info(traceback_error)
			else:
				comp_logger.info('ES insertion skipped for project id: {} due to absence step7 outputfile'.format(self.project_id))
		else:
			comp_logger.info('ES insertion skipped for project id: {} due to failed project status'.format(self.project_id))