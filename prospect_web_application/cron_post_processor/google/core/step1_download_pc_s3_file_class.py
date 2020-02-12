import boto3
import os
from threading import Thread
from helper import get_current_date, create_dir
from GlobalVariables import (
							SERVER,
							S3_BUCKET_DICT,
							S3_PREFIX_PC,
							# S3_REGION,
							S3_REGION_LIST,
							AWS_ACCESS_KEY_ID,
							AWS_SECRET_ACCESS_KEY,
							BATCH_OUTPUT_DIR_PC,
							CURRENT_DATE_STAMP
							)

class S3PcDownloaderThread(Thread):
	def __init__(self, thread_name, client_name):
		Thread.__init__(self)
		self.thread_name = thread_name
		self.client_name = client_name
		self.batch_output_dir = BATCH_OUTPUT_DIR_PC.format(self.client_name)

	def run(self):	
		global S3_BUCKET_DICT
		
		for S3_REGION in S3_REGION_LIST:
			BUCKET = S3_BUCKET_DICT[S3_REGION]
			OUTPUT_DIR = os.path.join(self.batch_output_dir, S3_REGION)
			create_dir(OUTPUT_DIR)

			# For thread safety
			session = boto3.session.Session()

			if SERVER:
				s3 = session.resource('s3')
			else:	
				s3 = session.resource('s3',aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
			
			print('{}: {}'.format(self.thread_name,BUCKET))
			bucket = s3.Bucket(BUCKET)
			files = bucket.objects.filter(Prefix=S3_PREFIX_PC)

			for file in files:
				file_key = file.key
				if '_mobile/' not in file_key and CURRENT_DATE_STAMP in file_key:
					if 'sponsored_result' in file_key and self.client_name in file_key:
						# print('{}: {}'.format(self.thread_name,file_key))
						# print(file_key)
						file_dir = file_key.split('/')[-2]
						file_path = os.path.join(OUTPUT_DIR, file_dir)
						create_dir(file_path)
						file_name = file_key.split('/')[-1]
						download_file_path = os.path.join(file_path,file_name)
						if not os.path.exists(download_file_path):
							obj = s3.Object(BUCKET, file_key).download_file(download_file_path)

		print('{} Completed'.format(self.thread_name))