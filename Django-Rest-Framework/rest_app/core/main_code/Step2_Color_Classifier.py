import pandas as pd
import os
import numpy as np
import cv2
from keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
from keras.models import load_model
from keras.utils.np_utils import to_categorical
from sklearn.preprocessing import LabelBinarizer
from imutils import paths
from django.conf import settings
import keras
import logging
comp_logger = logging.getLogger(__name__)


class ImageColorClassifier(object):
	
	def __init__(self,input_file_path, output_file_path, image_download_dir):
		self.input_file_path = input_file_path
		self.output_file_path = output_file_path
		self.image_download_dir = image_download_dir

		self.IMAGE_PRED_LIST = []
		self.IMAGE_PROB_LIST = []

		self.RESULT_PLATFORM_IMAGE_PRED_LIST = []
		self.RESULT_PLATFORM_IMAGE_PROB_LIST = []

		self.IMAGE_RESULT_COMP_LIST = []

		self.MODEL_PATH = settings.COLOR_MODEL_PATH
		# reading labels
		self.label_df = pd.read_csv(settings.COLOR_LABEL_LISTING_FILE, sep='\t')
		self.labels = self.label_df['Labels'].tolist()

		self.labels = np.array(self.labels)
		self.lb = LabelBinarizer()
		self.labels = self.lb.fit_transform(self.labels)


	# def getImageSize(self, image_path):
	# 	im = Image.open(image_path)
	# 	return (im.size)

	def classifyImage(self, image_path):
		try:
			image = cv2.imread(image_path)
			image = cv2.resize(image, (112, 112))
			image = image.astype("float") / 255.0
			image = img_to_array(image)
			image = np.expand_dims(image, axis=0)
			proba = self.model.predict(image)[0]
			idx = np.argmax(proba)
			label = self.lb.classes_[idx]
			max_prob = "%.4f" % proba[idx]
			return label,max_prob
		except:
			return 'Error classifying', 0.00


	def process(self, row):
		# search image
		product_image_url = row['s_image_url'].strip()
		product_name = product_image_url.split('/')[-1]
		# client image
		# print('For {}'.format(product_name))
		image_name = '{}.jpg'.format(product_name)
		image_path = os.path.join(self.image_download_dir,settings.PROJET_SEARCH_IMAGES_FOLDER,image_name)
		
		image_classification, search_image_prob = self.classifyImage(image_path)
		self.IMAGE_PRED_LIST.append(image_classification)
		self.IMAGE_PROB_LIST.append(search_image_prob)

		# client image
		# r_title = str(row['r_title'])
		# image_name = r_title.replace(' ','_').replace('.','_').replace('/','_').replace('"','_').replace('\'','_')
		# search_image_name = '{}.jpg'.format(image_name)
		result_image_name = row['result_image']

		if type(result_image_name) == float:
			result_platform_image_classification,result_image_prob = 'Error classifying', 0.00
		else:
			result_image_path = os.path.join(self.image_download_dir,settings.PROJET_RESULT_IMAGES_FOLDER,result_image_name)
			result_platform_image_classification,result_image_prob = self.classifyImage(result_image_path )
			
		self.RESULT_PLATFORM_IMAGE_PRED_LIST.append(result_platform_image_classification)
		self.RESULT_PLATFORM_IMAGE_PROB_LIST.append(result_image_prob)

		comp_result = False

		if image_classification==result_platform_image_classification:
			if image_classification != 'Error classifying':
				comp_result = True

		self.IMAGE_RESULT_COMP_LIST.append(comp_result)

		comp_logger.info('color row number: {}'.format(row.name))


	def start(self):
		df = pd.read_csv(self.input_file_path,sep='\t',encoding='iso-8859-1')
		
		with keras.backend.get_session().graph.as_default():
			self.model = load_model(self.MODEL_PATH)
			df.apply(self.process,axis=1)
			del self.model
		keras.backend.clear_session()
		
		df['s_image_color'] = self.IMAGE_PRED_LIST
		df['s_image_conf_color'] = self.IMAGE_PROB_LIST
		df['r_image_color'] = self.RESULT_PLATFORM_IMAGE_PRED_LIST
		df['r_image_conf_color'] = self.RESULT_PLATFORM_IMAGE_PROB_LIST
		df['s_vs_r_image_color_conf'] = self.IMAGE_RESULT_COMP_LIST
		df.to_csv(self.output_file_path,sep='\t',index=False,encoding='iso-8859-1')