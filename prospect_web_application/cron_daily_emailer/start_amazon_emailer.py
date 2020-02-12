from GlobalVariables import (
								CURRENT_DATE_STAMP,
								EMAIL_SUBJECT_TEMPLATE,
								EMAIL_HEADER_TEMPLATE,
								AMAZON_EMAIL_TABLE_STRING,
								AMAZON_EMAIL_TABLE_ROW_STRING,
								CURRENT_EST_TIME,
								DATE_TIME_DELIM

							)
from db_helper.db_base import DBConnector
from db_helper.table_classes import ProspectDetails, AmazonRunDetails

import emailer as eml


def persist_date_time_log_file():
	CRON_LOG_FILE_PATH = os.path.join(BASE_DIR, LOG_DIR, LOG_FILE)
	DATE_TIME_STAMP_LOG_FILE_PATH = os.path.join(BASE_DIR, LOG_DIR, '{}.log'.format(CURRENT_DATE_STAMP))
	copy_file(CRON_LOG_FILE_PATH, DATE_TIME_STAMP_LOG_FILE_PATH)


def getActivePostProcessCronJobsForEmailBatch(session):
	"""
	Return query object of all post_processed tasks which hasn't been reported yet
	"""
	return session.query(AmazonRunDetails).filter(AmazonRunDetails.batch_email_sent == False).filter(AmazonRunDetails.post_process_completed == True)


def getDistinctProspectIdList(active_post_process_to_email_list):
	distinct_prospect_id_list = []
	distinct_prospect_id_list = list(set([item.prospect.id for item in  active_post_process_to_email_list.all()]))
	return distinct_prospect_id_list


def getDistinctProspectEmailBatch(prospect_id, active_post_process_to_email_list):
	return active_post_process_to_email_list.filter(AmazonRunDetails.prospect_id == prospect_id).all()

def send_email_for_completion(	
								platform,
								email_est_time,
								prospect,
								email_table_body,
								email_recipients
							 ):
	
	email_subject = EMAIL_SUBJECT_TEMPLATE.format(platform, prospect, email_est_time)
	email_header = EMAIL_HEADER_TEMPLATE.format(platform, email_est_time, prospect)
	# email_body = email_table_body
	
	# print(email_header)
	# print(email_table_body)

	eml.send_email(
				   prospect,
				   email_subject,
				   email_header,
				   email_table_body,
				   email_recipients
				   )

def update_prospect_run_details_batch_status(session, prospect_email_job):
	prospect_email_job.batch_email_sent = True
	session.add(prospect_email_job)
	session.commit()

if __name__ == '__main__':

	db_connector_obj = DBConnector()
	Session = db_connector_obj.get_session()
	session = Session()

	print('For datetime: {}'.format(CURRENT_DATE_STAMP))
	active_post_process_to_email_list = getActivePostProcessCronJobsForEmailBatch(session)
	active_post_process_to_email_count = len(active_post_process_to_email_list.all())
	print('Number of Email run detail jobs: {}'.format(active_post_process_to_email_count))

	email_est_time = CURRENT_EST_TIME.split(DATE_TIME_DELIM)[0].replace('_',':')
	# exit(1)
	print('---------------------------')
	if active_post_process_to_email_count> 0 :
		distinct_prospect_id_list = getDistinctProspectIdList(active_post_process_to_email_list)
		
		for prospect_id in distinct_prospect_id_list:
			# For each distinct client, email is sent
			prospect_obj = session.query(ProspectDetails).get(prospect_id)
			prospect_name = prospect_obj.name
			prospect_email_recipients = prospect_obj.email_recipients.split(',')
			prospect_email_recipients = list(map(lambda x: x.strip(), prospect_email_recipients))
			prospect_email_recipients
			print('For client: {}'.format(prospect_name))

			if len(prospect_email_recipients)>0:
				prospect_email_job_table_row_list = []

				for prospect_email_job in getDistinctProspectEmailBatch(prospect_id, active_post_process_to_email_list):
					run_details_id = prospect_email_job.id
					print('For run id: {}'.format(run_details_id))
					prospect_name = prospect_email_job.prospect.name
					prospect_run_datetime = prospect_email_job.date_time.strftime("%m-%d-%Y:%H")
					prospect_platform = prospect_email_job.prospect.platform

					prospect_run_total_amazon_choices = prospect_email_job.total_amazon_choices_records
					prospect_run_total_brands_related = prospect_email_job.total_brands_related_records
					prospect_run_total_editorial_recommendations = prospect_email_job.total_editorial_recommendations_records
					prospect_run_total_organic = prospect_email_job.total_organic_records
					prospect_run_total_sponsored = prospect_email_job.total_sponsored_records
					prospect_run_total_today_deals = prospect_email_job.total_today_deals_records


					prospect_run_post_process_completed = prospect_email_job.post_process_completed

					prospect_email_job_table_row_list.append(AMAZON_EMAIL_TABLE_ROW_STRING.format(run_details_id, prospect_run_datetime,\
																				prospect_platform, prospect_run_total_amazon_choices,\
																				prospect_run_total_brands_related, prospect_run_total_editorial_recommendations,\
																				prospect_run_total_organic,prospect_run_total_sponsored, prospect_run_total_today_deals,prospect_run_post_process_completed))

					print('--------')

					update_prospect_run_details_batch_status(session, prospect_email_job)
				prospect_email_table_string = AMAZON_EMAIL_TABLE_STRING.format(''.join(prospect_email_job_table_row_list))
				
				print('Sending Email')

				send_email_for_completion(prospect_platform, email_est_time, prospect_name, prospect_email_table_string, prospect_email_recipients)

			print('---------------------------')
			exit(1)

		print('#############################################################################')

		

		
		
		