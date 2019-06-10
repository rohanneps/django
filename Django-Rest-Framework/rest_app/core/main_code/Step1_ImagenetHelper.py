import pandas as pd
import os
from keras.applications import VGG19
from keras.applications import imagenet_utils
from keras.applications.inception_v3 import preprocess_input
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
import numpy as np
# from threading import Thread
from django.conf import settings
import keras
import logging
comp_logger = logging.getLogger(__name__)

class ImagenetBatchClassifier():
	
	def __init__(self, image_dir_path, output_file_path):
		# Thread.__init__(self)
		self.image_dir_path = image_dir_path
		self.output_file_path = output_file_path
		self.BATCH_SIZE = 16
		self.output_df = pd.DataFrame(columns=['filename','prediction'])
		self.filename_list = []
		self.prediction_list = []

		self.Network = VGG19
		# self.model = self.Network(weights="imagenet", include_top=True)
		self.model = self.Network(weights=settings.VGG19_MODEL_PATH, include_top=True)
		self.model._make_predict_function() 
		self.inputShape = (224, 224)
		self.preprocess = imagenet_utils.preprocess_input

	def classifyImageList(self, image_location_list):
		image_list = []
		comp_logger.info('Loading Image')
		for img in image_location_list:
			try:
				image_full_path = os.path.join(self.image_dir_path, img)
				image = load_img(image_full_path)
				image = image.resize(settings.DEFAULT_IMAGE_SHAPE)
				image = image.resize(self.inputShape)
				image = img_to_array(image)
				image = self.preprocess(image)
				image_list.append(image)
				self.filename_list.append(img)
			except:
				pass
		image_list = np.array(image_list)
		pred_list = self.model.predict(image_list)
		downscaled_pred_list = imagenet_utils.decode_predictions(pred_list)
		
		for item in downscaled_pred_list:
			max_prob_item_tuple = item[0]
			max_label = max_prob_item_tuple[1]
			max_prob = max_prob_item_tuple[2]
			self.prediction_list.append(max_label)

	def run(self):
		cnt= 0
		image_location_list = []
		for roots, dirs, files in os.walk(self.image_dir_path):
			file_count = len(files)
			for file in files:
				cnt += 1

				image_location_list.append(file)
				if (cnt%self.BATCH_SIZE ==0 or cnt==file_count) and (file_count!=0):
					comp_logger.info('classify')
					comp_logger.info(len(image_location_list))
					self.classifyImageList(image_location_list)
					image_location_list = []

		self.output_df['filename'] = self.filename_list
		self.output_df['prediction'] = self.prediction_list
		self.output_df.to_csv(self.output_file_path, sep='\t',index=False)

	def close_resources(self):
		del self.model

def get_final_merged_output(input_file, search_img_classification_file,result_img_classification_file, output_file):
	df = pd.read_csv(input_file, sep='\t',encoding='iso-8859-1')
	# search
	df['filename'] = df['s_image_url'].apply(lambda x: '{}.jpg'.format(x.split('/')[-1].strip()))
	search_classification_df = pd.read_csv(search_img_classification_file, sep='\t',encoding='iso-8859-1')
	merged_df = pd.merge(df, search_classification_df, how='left', on='filename')
	merged_df = merged_df.rename(columns={'prediction':'s_image_vgg19'})

	# result
	# merged_df['filename'] = merged_df['r_title'].apply(lambda x: '{}.jpg'.format(x.replace(' ','_').replace('.','_').replace('/','_').replace('"','_').replace('\'','_').encode('utf-8').strip()))
	# merged_df['filename'] = merged_df['r_title'].apply(lambda x: '{}.jpg'.format(x.replace(' ','_').replace('.','_').replace('/','_').replace('"','_').replace('\'','_')))
	# merged_df['filename'] = merged_df['r_image'].apply(lambda x: '{}.jpg'.format(x.split('|')[-1].strip().split('/')[-1].replace(' ','_').replace('.','_').replace('/','_').replace('"','_').replace('\'','_')))
	merged_df['filename'] = merged_df['result_image']

	result_classification_df = pd.read_csv(result_img_classification_file, sep='\t',encoding='iso-8859-1')
	merged_df = pd.merge(merged_df, result_classification_df, how='left', on='filename')
	merged_df = merged_df.rename(columns={'prediction':'r_image_vgg19'})

	merged_df['s_image_vgg19'] = merged_df['s_image_vgg19'].apply(lambda img: 'no_search_img' if type(img)==float else img)
	merged_df['r_image_vgg19'] = merged_df['r_image_vgg19'].apply(lambda img: 'no_result_img' if type(img)==float else img)

	merged_df['s_vs_r_image_vgg19_conf'] = merged_df['s_image_vgg19'] == merged_df['r_image_vgg19']
	del merged_df['filename']
	del merged_df['result_image']
	try:
		merged_df.to_csv(output_file,sep='\t',index=False,encoding='iso-8859-1')
	except:
		merged_df.to_csv(output_file,sep='\t',index=False,encoding='iso-8859-1')


def main(input_file_path, output_dir, image_download_main_dir, project_id):
	
	# for classification

	keras.backend.clear_session()
	with keras.backend.get_session().graph.as_default():
		# for search images
		search_image_dir_path = os.path.join(image_download_main_dir, settings.PROJET_SEARCH_IMAGES_FOLDER)
		search_output_file_name = os.path.join(output_dir, settings.PROJECT_STEP_FILE_1_SEARCH)
		
		if not os.path.exists(search_output_file_name):
			comp_logger.info('Search images classification initiated for project id: {}'.format(project_id))
			search_imagenet_batch_classifier = ImagenetBatchClassifier(search_image_dir_path, search_output_file_name)
			# search_imagenet_batch_classifier.start()
			# search_imagenet_batch_classifier.join()
			search_imagenet_batch_classifier.run()
			search_imagenet_batch_classifier.close_resources()
			comp_logger.info('Search images classification completed for project id: {}'.format(project_id))
		else:
			comp_logger.info('Search images classification already completed for project id: {}. Restart process'.format(project_id))

	keras.backend.clear_session()
	with keras.backend.get_session().graph.as_default():
		# for result images
		result_image_dir_path = os.path.join(image_download_main_dir, settings.PROJET_RESULT_IMAGES_FOLDER)
		result_output_file_name = os.path.join(output_dir, settings.PROJECT_STEP_FILE_1_RESULT)

		if not os.path.exists(result_output_file_name):
			comp_logger.info('Result images classification initiated for project id: {}'.format(project_id))
			result_imagenet_batch_classifier = ImagenetBatchClassifier(result_image_dir_path, result_output_file_name)
			# result_imagenet_batch_classifier.start()
			# result_imagenet_batch_classifier.join()
			result_imagenet_batch_classifier.run()
			result_imagenet_batch_classifier.close_resources()
			comp_logger.info('Result images classification completed for project id: {}'.format(project_id))
		else:
			comp_logger.info('Result images classification already completed for project id: {}. Restart process'.format(project_id))

	step1_final_output = os.path.join(output_dir,settings.PROJECT_STEP_FILE_1)

	if not os.path.exists(step1_final_output):
		get_final_merged_output(input_file=input_file_path, search_img_classification_file=search_output_file_name, result_img_classification_file=result_output_file_name, output_file=step1_final_output)
	else:
		comp_logger.info('Imagenet classification already completed for project id: {}. Restart process'.format(project_id))		
