import pandas as pd
import os
import numpy as np
from keras.applications import VGG16
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



class SourceResultImageSimilarityClassifier():

	def __init__(self, 
				 image_dir_path,
				 client_input_file_path,
				 result_image_mapper_file_path,
				 project_id):

		self.project_id = project_id
		
		self.image_download_dir = image_dir_path
		self.client_input_df = pd.read_csv(client_input_file_path,sep='\t',encoding='iso-8859-1')
		self.result_image_mapper_df = pd.read_csv(result_image_mapper_file_path, sep='\t',encoding='iso-8859-1')

		self.result_image_similarity_mapper_file_path = os.path.join(image_dir_path, 
																	 settings.PROJECT_RESULT_IMAGE_MAPPER_FINAL)
		self.result_image_similarity_mapper_df = pd.DataFrame(columns=['s_sku','r_item_name','result_image','r_image_url_main'])


		# Feature Extractor Model Details
		self.model = VGG16(weights=settings.VGG16_MODEL_PATH, include_top=False)
		self.inputShape = (224, 224)
		self.preprocess = imagenet_utils.preprocess_input


	def getVGG16BottleneckFeature(self, image_path):
		image = load_img(image_path)
		image = image.resize(self.inputShape)
		image = img_to_array(image)
		image = self.preprocess(image)
		image = np.expand_dims(image, axis=0)
		image_pred_features = self.model.predict(image)[0]
		return image_pred_features


	def getSourceImageProductSimilarity(self, s_sku):
		# uniq_source_image_df = self.client_result_image_mapper_df[self.client_result_image_mapper_df['s_image_url']==source_image_url]
		uniq_source_sku_df = self.client_result_image_mapper_df[self.client_result_image_mapper_df['s_sku']==s_sku]
		

		source_product_image_url = uniq_source_sku_df['s_image_url'].iloc[0]

		# comp_logger.info('for s_sku:{}'.format(s_sku))
		# Flag to check if source image has issue
		source_image_has_issue = False

		if type(source_product_image_url) in ['float', np.float64]:
			# to check if there is source image url
			source_image_has_issue = True

		else:
			source_product_name = source_product_image_url.split('/')[-1]
			source_image_name = settings.PROJECT_SEARCH_IMAGE_PATTERN.format(source_product_name)
			
			source_image_path = os.path.join(self.image_download_dir,
											 settings.PROJET_SEARCH_IMAGES_FOLDER,
											 source_image_name)
		if not source_image_has_issue:
			try:
				# handling of source image read issue
				source_feature_vectors = self.getVGG16BottleneckFeature(source_image_path)
			except:
				source_image_has_issue = True
				comp_logger.info('{} for project id:{} has image issue with path: {}'.format(s_sku, 
																							 self.project_id,
																							 source_image_path))
		else:
			comp_logger.info('{} for project id:{} has no image url'.format(s_sku, self.project_id))
		


		for result_item_name in uniq_source_sku_df['r_item_name'].unique().tolist():
			# for each unique result item and source sku partition
			uniq_source_image_result_item_name_df = uniq_source_sku_df[uniq_source_sku_df['r_item_name']==result_item_name]
			
			if len(uniq_source_image_result_item_name_df) == 0:
				# empty result itemname check
				if str(result_item_name) == 'nan':
					comp_logger.info('{} has r_item_name is blank'.format(s_sku))
					uniq_source_image_result_item_name_df = uniq_source_sku_df[uniq_source_sku_df['r_item_name'].isnull()]
					# comp_logger.info(len(uniq_source_image_result_item_name_df))

			
			min_distance = 10000
			result_similar_image_name = None

			source_result_similar_image_dict = {}
			source_result_similar_image_dict['r_item_name'] = result_item_name
			source_result_similar_image_dict['s_sku'] = s_sku

			if not source_image_has_issue:
				unique_source_result_item_result_image_list = uniq_source_image_result_item_name_df['result_image'].unique().tolist()
				#comp_logger.info(unique_source_result_item_result_image_list)

				if len(unique_source_result_item_result_image_list) == 1:
					# no need for feature comparison
					result_similar_image_name = unique_source_result_item_result_image_list[0]
					#comp_logger.info('No Need for feature extraction')
				else:
					for result_image_name in unique_source_result_item_result_image_list:
						# comp_logger.info('for result: {}'.format(result_image_name))
						result_image_path = os.path.join(self.image_download_dir,
														 settings.PROJET_RESULT_IMAGES_FOLDER,
														 result_image_name)
						
						try:
							#handling of result image read issue
							result_feature_vectors = self.getVGG16BottleneckFeature(result_image_path)
							euclidean_distance = np.linalg.norm(source_feature_vectors-result_feature_vectors)
						except:
							euclidean_distance = min_distance
						
						if euclidean_distance <= min_distance:
							min_distance = euclidean_distance
							result_similar_image_name = result_image_name
					
				source_result_similar_image_dict['r_image_url_main'] = uniq_source_image_result_item_name_df[uniq_source_image_result_item_name_df['result_image']==result_similar_image_name]['r_image_url'].iloc[0] # Image url
				source_result_similar_image_dict['result_image'] = result_similar_image_name	# Internal image name

			else:
				# Handling for source image issue
				result_similar_image_name = uniq_source_image_result_item_name_df['result_image'].tolist()[0]

				source_result_similar_image_dict['r_image_url_main'] = uniq_source_image_result_item_name_df[uniq_source_image_result_item_name_df['result_image']==result_similar_image_name]['r_image_url'].iloc[0] # Image url
				source_result_similar_image_dict['result_image'] = result_similar_image_name	# Internal image name

			self.result_image_similarity_mapper_df = self.result_image_similarity_mapper_df.append(source_result_similar_image_dict,
																								   ignore_index = True)


	def start(self):
		if not os.path.exists(self.result_image_similarity_mapper_file_path):
			comp_logger.info('Total rows in client file : {} and project id: {}'.format(len(self.client_input_df),
																						self.project_id))
			comp_logger.info('Total rows in result mapper temp before similarity computation: {} and project id: {}'.format(len(self.result_image_mapper_df),self.project_id))

			del self.client_input_df['r_image_url']

			self.client_result_image_mapper_df = pd.merge(self.client_input_df, self.result_image_mapper_df, 
														  how='inner', on=['s_sku','r_item_name'])

			self.client_result_image_mapper_df = self.client_result_image_mapper_df.drop_duplicates(subset=['s_sku','r_item_name','r_image_url'],
																									keep='first')

			
			comp_logger.info('Total Merged rows : {} for project_id: {}'.format(len(self.client_result_image_mapper_df), 
																				self.project_id))

			self.client_result_image_mapper_df = self.client_result_image_mapper_df[ ['s_image_url'] + self.result_image_mapper_df.columns.tolist()]

			with keras.backend.get_session().graph.as_default():
				# for uniq_source_image_url in self.client_result_image_mapper_df['s_image_url'].unique().tolist():
				for uniq_source_sku in self.client_result_image_mapper_df['s_sku'].unique().tolist():
					# comp_logger.info('for source : {}'.format(uniq_source_image_url))
					try:
						self.getSourceImageProductSimilarity(uniq_source_sku)
					except:
						raise Exception('Exception for sku: {}'.format(uniq_source_sku))

			keras.backend.clear_session()

			# Persist final image mapper consisting of most similar source-result image relation
			self.result_image_similarity_mapper_df.to_csv(self.result_image_similarity_mapper_file_path,
														  index=False,
														  sep='\t',
														  encoding='iso-8859-1' )




def main(image_dir_path,
		 client_input_file_path,
		 result_image_mapper_file_path,
		 project_id):
	source_result_image_similarity_classifier = SourceResultImageSimilarityClassifier(image_dir_path = image_dir_path, 
																				      client_input_file_path = client_input_file_path, 
																					  result_image_mapper_file_path = result_image_mapper_file_path,
																					  project_id = project_id)
	source_result_image_similarity_classifier.start()
