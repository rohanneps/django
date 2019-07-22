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

	def __init__(self,
				 thread_name,
				 input_df,
				 image_download_dir):

		Thread.__init__(self)
		self.thread_name = thread_name
		self.input_df = input_df
		self.image_download_dir = image_download_dir


	def run(self):
		self.input_df.apply(self.process, axis=1)


	def downloadImage(self,url,file_path):
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
		product_image_url = row['r_image_url'].split(settings.IMAGE_LIST_SEPARATOR)[0].strip()
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




def getResultImageMapperFileDF(client_df,
							   result_image_mapper_file_path):
	"""
	Creates a result image mapper file that holds result item name to image file mapping
	return the mapping data frame
	"""
	
	if os.path.exists(result_image_mapper_file_path):
		result_df = pd.read_csv(result_image_mapper_file_path,sep='\t', encoding='ISO-8859-1')
	else:	
		# Getting unique product images(single)
		result_df = client_df[['r_item_name']].copy()
		result_df = result_df.drop_duplicates(subset=['r_item_name'], keep='first')
		total_rows_in_client_file = len(result_df)
		result_df['result_image'] = list(map(lambda x: settings.PROJECT_RESULT_IMAGE_PATTERN.format(x),range(1,total_rows_in_client_file+1)))
		result_df.to_csv(result_image_mapper_file_path, index=False,sep='\t', encoding='ISO-8859-1')
	return result_df




def getResultMultiImageMapperFile(client_df, 
								  result_image_mapper_file_path):
	"""
	Creates a result image mapper file that holds result item name to image file mapping
	return the mapping data frame
	"""
	
	if os.path.exists(result_image_mapper_file_path):
		result_df = pd.read_csv(result_image_mapper_file_path,sep='\t', encoding='ISO-8859-1')

	else:
		# split single image list to multiple image listing
		r_image_stack_df = pd.DataFrame(client_df['r_image_url'].str.split(settings.IMAGE_LIST_SEPARATOR).tolist(), 
								index=[client_df['r_item_name'],client_df['s_sku']]).stack()

		r_image_stack_df = r_image_stack_df.reset_index()

		del r_image_stack_df['level_2']

		r_image_stack_df.rename(columns={0:'r_image_url'}, inplace=True)
		r_image_stack_df['r_image_url'] = r_image_stack_df['r_image_url'].str.strip()

		# unique r_image_url listing and integer name mapping
		r_image_uniq_df = r_image_stack_df[['r_image_url']]
		r_image_uniq_df = r_image_uniq_df.drop_duplicates(subset=['r_image_url'], keep='first')
		total_rows_in_client_file = len(r_image_uniq_df)
		# r_image_uniq_df['result_image'] = list(map(lambda x: '{}.jpg'.format(x),range(1,total_rows_in_client_file+1)))
		r_image_uniq_df['result_image'] = list(map(lambda x: settings.PROJECT_RESULT_IMAGE_PATTERN.format(x),range(1,total_rows_in_client_file+1)))
		
		"""
		merging r_image stacked df with unique integer name mapping
		Exploded r_image_url df with integer name mapping
		"""

		result_df = pd.merge(r_image_stack_df, r_image_uniq_df, how='inner',on=['r_image_url'])
		result_df.drop_duplicates(subset=['s_sku','r_item_name','r_image_url'], keep='first', inplace=True)

		# There is no redundant product combination(redundancy may occur due to SERP KEY used) in this df persistance
		result_df.to_csv(result_image_mapper_file_path, index=False,sep='\t', encoding='ISO-8859-1')
		
	return result_df




def main(client_input_file_path, 
		  image_download_dir,
		  result_image_mapper_file_path):

	client_df = pd.read_csv(client_input_file_path, sep='\t', encoding='ISO-8859-1')
	client_df = client_df[client_df['r_image_url'].notnull()]
	client_df = client_df.fillna(value='')


	# result_df = getResultImageMapperFileDF(client_df, result_image_mapper_file_path)
	# client_df = pd.merge(client_df, result_df, how='inner', on=['r_item_name'])

	result_df = getResultMultiImageMapperFile(client_df=client_df,
											  result_image_mapper_file_path=result_image_mapper_file_path)


	NUMBER_OF_THREAD = settings.PROJECT_IMAGES_DOWNLOAD_THREADS
	df_list = np.array_split(result_df, NUMBER_OF_THREAD)
	thread_list = []

	# Threaded image downloader
	for item in range(0, NUMBER_OF_THREAD):
		df_subset = df_list[item]
		thread_name = 'Thread{}'.format(item)
		thread = ResultImageDownloaderThread(thread_name=thread_name,
											 input_df=df_subset,
											 image_download_dir=image_download_dir)
		thread_list.append(thread)		
		thread.start()

	client_df = client_df.iloc[0:0]

	for thread in thread_list:
		thread.join()
