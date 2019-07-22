from PIL import Image
from threading import Thread
from django.conf import settings
import pandas as pd
import os
from urllib.request import urlopen
import os
import numpy as np
import traceback
import logging
comp_logger = logging.getLogger(__name__)

class ResultImageDownloaderThread(Thread):
	def __init__(self,thread_name,input_df,image_download_dir):
		Thread.__init__(self)
		self.thread_name = thread_name
		self.input_df = input_df
		self.image_download_dir = image_download_dir

	def run(self):
		self.input_df.apply(self.process, axis=1)

	def downloadImage(self, url, file_path):
		if not os.path.exists(file_path):
			# try:
			f = open(file_path,'wb')
			f.write(urlopen(url).read())
			f.close()
			# except:
			# 	return 
			image = Image.open(file_path)
			image.convert('RGB').save(file_path)


	def process(self, row):
		product_image_url = row['r_image_url'].split('|')[0].strip()
		# r_title = str(row['r_item_name'])
		# image_name = r_title.replace(' ','_').replace('.','_').replace('/','_').replace('"','_').replace('\'','_')
		# image_name = '{}.jpg'.format(image_name)
		image_name = row['result_image']

		image_path = os.path.join(self.image_download_dir,image_name)
		try:
			if not os.path.exists(image_path):
				self.downloadImage(product_image_url,image_path)
		except:
			traceback_error = traceback.format_exc()
			comp_logger.info(traceback_error)


def getResultMapperFileDF(client_df, result_image_file_path):
	"""
	Creates a result image mapper file that holds result item name to image file mapping
	return the mapping data frame
	"""
	
	if os.path.exists(result_image_file_path):
		result_df = pd.read_csv(result_image_file_path,sep='\t', encoding='ISO-8859-1')
	else:	
		# Getting unique product images(single)
		result_df = client_df[['r_item_name']].copy()
		result_df = result_df.drop_duplicates(subset=['r_item_name'], keep='first')
		total_rows_in_client_file = len(result_df)
		result_df['result_image'] = list(map(lambda x: '{}.jpg'.format(x),range(1,total_rows_in_client_file+1)))
		result_df.to_csv(result_image_file_path, index=False,sep='\t', encoding='ISO-8859-1')


def main(file_path, image_download_dir,result_image_file_path):
	client_df = pd.read_csv(file_path, sep='\t', encoding='ISO-8859-1')
	client_df = client_df[client_df['r_image_url'].notnull()]
	client_df = client_df.fillna(value='')

	# # creating result title to image name mapper
	# if os.path.exists(result_image_file_path):
	# 	result_df = pd.read_csv(result_image_file_path,sep='\t', encoding='ISO-8859-1')
	# else:	
	# 	# Getting unique product images(single)
	# 	result_df = client_df[['r_item_name']].copy()
	# 	result_df = result_df.drop_duplicates(subset=['r_item_name'], keep='first')
	# 	result_df['result_image'] = list(map(lambda x: '{}.jpg'.format(x),range(1,len(result_df)+1)))
	# 	result_df.to_csv(result_image_file_path, index=False,sep='\t', encoding='ISO-8859-1')
	
	result_df = getResultMapperFileDF(client_df, result_image_file_path)

	client_df = pd.merge(client_df, result_df, how='inner', on=['r_item_name'])

	NUMBER_OF_THREAD = settings.PROJECT_IMAGES_DOWNLOAD_THREADS
	df_list = np.array_split(client_df, NUMBER_OF_THREAD)
	thread_list = []

	for item in range(0, NUMBER_OF_THREAD):
		df_subset = df_list[item]
		thread_name = 'Thread{}'.format(item)
		thread = ResultImageDownloaderThread(thread_name, df_subset, image_download_dir)
		thread_list.append(thread)		
		thread.start()

	client_df = client_df.iloc[0:0]

	for thread in thread_list:
		thread.join()
