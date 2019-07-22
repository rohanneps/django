from threading import Thread
from django.conf import settings
import requests
import pandas as pd
import os
import numpy as np
from PIL import Image

class SearchImageDownloaderThread(Thread):

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

	def getSourceCode(self,url):
		validUrlPrefix = ['http','https']

		def getCorrectUrlSchema(url):
			"""
			Correct URL pattern
			"""
			urlPrefix = url.split(':')[0]
			if urlPrefix not in validUrlPrefix:
				url = 'http://' + url
			url = url.replace('////','//')
			return url

		correctUrl = getCorrectUrlSchema(url)
		return requests.get(correctUrl)


	def downloadImage(self,url,file_path):
		if not os.path.exists(file_path):
			f = open(file_path,'wb')
			imageContent = self.getSourceCode(url).content
			f.write(imageContent)
			f.close()
			image = Image.open(file_path)
			image.convert('RGB').save(file_path)


	def process(self, row):
		product_image_url = row['s_image_url'].strip()
		product_name = product_image_url.split('/')[-1]
		# image_name = '{}.jpg'.format(product_name)
		image_name = settings.PROJECT_SEARCH_IMAGE_PATTERN.format(product_name)
		image_path = os.path.join(self.image_download_dir,image_name)

		try:
			self.downloadImage(product_image_url,image_path)
		except:
			pass
	

def main(file_path, 
		 image_download_dir):
	"""
	Script Entry point
	"""
	client_df = pd.read_csv(file_path, sep='\t',encoding='iso-8859-1')
	client_df = client_df[client_df['s_image_url'].notnull()]
	client_df = client_df.fillna(value='')

	# Parallel Processing
	NUMBER_OF_THREAD = settings.PROJECT_IMAGES_DOWNLOAD_THREADS
	df_list = np.array_split(client_df, NUMBER_OF_THREAD)
	thread_list = []

	for item in range(0, NUMBER_OF_THREAD):
		df_subset = df_list[item]
		thread_name = 'Thread{}'.format(item)
		thread = SearchImageDownloaderThread(thread_name=thread_name,
											 input_df=df_subset,
											 image_download_dir=image_download_dir)
		thread_list.append(thread)		
		thread.start()
	
	# memory release
	client_df = client_df.iloc[0:0]

	for thread in thread_list:
		thread.join()


