import pandas as pd
import boto3
import json
import os
import time
from datetime import datetime, timedelta
from GlobalVariables import (
								MAX_PROSPECT_CRON_JOB_LIFE_TYPE,
								MEDIA_ROOT,
								MAX_PROSPECT_RUN_COUNT,
								AWS_ACCESS_KEY_ID,
								AWS_SECRET_ACCESS_KEY,
								AWS_REGION_LIST,
								AWS_LAMBDA_REQUEST_WAIT_TIME,
								KEYWORD_COLUMN
							)

from db_helper.db_base import DBConnector
from db_helper.table_classes import ProspectDetails, AmazonRunDetails

START_INDEX = 1
BATCH_SIZE = 20

class CronProspect():

	def __init__(self, current_est_time):
		self.platform = 'Amazon'
		self.current_est_time = current_est_time
		# DB objects
		db_connector_obj = DBConnector()
		Session = db_connector_obj.get_session()
		self.session = Session()
		
		self.current_date_time_obj = self.getCurrentDateTime()
		self.prospect_max_life_time = self.current_date_time_obj - timedelta(days=MAX_PROSPECT_CRON_JOB_LIFE_TYPE)


	def getCurrentDateTime(self):
		return datetime.now()

	def getActiveProspectCronJobs(self):
		return self.session.query(ProspectDetails).filter(ProspectDetails.platform == self.platform).filter(ProspectDetails.status == True).all()


	def prospect_has_expired(self, prospect, run_count):
		if run_count < MAX_PROSPECT_RUN_COUNT:
			return False
		else:
			print('Prospect: {} exipred with run count: {}'.format(prospect, run_count))
			return True

	def invokeLambdaFunction(self, client, keyword_list_batch, region):
		payload = {
					"query_list":keyword_list_batch,
					"client": client
					}

		CLIENT = boto3.client(  
								'lambda', 
								aws_access_key_id=AWS_ACCESS_KEY_ID, 
					  			aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
					  			region_name=region
					  		 )

		## Invocation for PC Page Source
		response = CLIENT.invoke(
									FunctionName='rndProspectAmazon',
									InvocationType='Event',
									LogType='Tail',
									Payload=json.dumps(payload)
								)

		print('Desktop')
		print(response)

	def updateInactiveProspectState(self, prospect_obj):
		prospect_obj.status = False
		self.session.commit()

	def updateProspectRunCount(self, prospect_obj):
		prospect_obj.run_count +=1 
		self.session.commit()

	def addRunDetails(self, prospect_obj):
		print('Adding Run Details')
		prospect_run_details = AmazonRunDetails(prospect_id=prospect_obj.id, date_time=self.getCurrentDateTime())
		self.session.add(prospect_run_details)
		self.session.commit()


	def main(self):

		# Sending invocation email
		prospect_active_projects = self.getActiveProspectCronJobs()

		print('For run: {}, the number of active cron jobs for {} prospects are: {}'.format(self.current_est_time, self.platform, len(prospect_active_projects)))
		# exit(1)
		print('-----------------------------------------')
		for prospect_obj in prospect_active_projects:
			client = prospect_obj.name
			prospect_id = prospect_obj.id
			file_name = prospect_obj.file_name
			email_recipients = prospect_obj.email_recipients
			prospect_start_date = prospect_obj.start_date
			run_count = prospect_obj.run_count

			print('For client: {}'.format(client))
			print('Start time: {}'.format(prospect_start_date))
			print('Run count: {}'.format(run_count))

			if self.prospect_has_expired(client, run_count):
				# update status
				self.updateInactiveProspectState(prospect_obj)
			else:

				# updating run count
				self.updateProspectRunCount(prospect_obj)
				self.addRunDetails(prospect_obj)
				prospect_file_full_path = os.path.join(MEDIA_ROOT, file_name)
				print(prospect_file_full_path)
				df = pd.read_csv(prospect_file_full_path, sep='\t')
				df[KEYWORD_COLUMN] = df[KEYWORD_COLUMN].str.strip()
				df = df[df[KEYWORD_COLUMN].notnull()]
				keyword_list = df[KEYWORD_COLUMN].unique().tolist()
				print('Number of Keywords: {}'.format(len(keyword_list)))

				num_unique_keywords = len(keyword_list) 
				num_list = num_unique_keywords/BATCH_SIZE
				rem_rows = num_unique_keywords % BATCH_SIZE


				if rem_rows != 0:
					num_list += 1

				start_index = 0
				list_counter = 1
				num_list = int(num_list)

				for df_num in range(0,num_list):
					if list_counter == num_list and rem_rows!=0:
						last_index = start_index+rem_rows
					else:	
						last_index = start_index + BATCH_SIZE

					keyword_list_batch = keyword_list[start_index:last_index]
					print(start_index, last_index)
					print(list_counter)
					start_index = last_index

					# function here
					for region in ['us-east-1']:
						print(region)
						self.invokeLambdaFunction(client.replace('/','_'), keyword_list_batch, region)
						print('------')
					list_counter += 1
					time.sleep(AWS_LAMBDA_REQUEST_WAIT_TIME)
					print('-----------------------------------------------------------')
				# 	# exit(1)

			print('----------------------------------------------------------')

def get_current_est_time():
	""" 
	GMT to EST
	"""
	now = datetime.now()
	est_date_time_obj = now - timedelta(hours=5)
	return est_date_time_obj.strftime("%d_%m_%Y__%H")


if __name__ == '__main__':
	current_est_time = get_current_est_time()
	print('Starting cron job of Prospects for est time: {}'.format(current_est_time))

	cron_prospect_obj_handler = CronProspect(current_est_time)
	cron_prospect_obj_handler.main()
	print('Task Completed')
	print('##################################################################################')