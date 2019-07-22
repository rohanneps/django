import os
import pandas as pd
import math
from django.conf import settings
import logging
comp_logger = logging.getLogger(__name__)




def main(project_id,
		 input_file_path,
		 output_file_path):

	base_column_list = ['sys_index','s_sku','s_product_url','s_image_url','SERP_URL','SERP_KEY',\
						'r_product_url','r_item_name']

	# Imagenet Classified Section
	imagenet_file_path = os.path.join(settings.PROJECT_DIR, 
									  str(project_id),
									  settings.PROJECT_STEP_FOLDER,
									  settings.PROJECT_STEP_FOLDER_1,
									  settings.PROJECT_STEP_FILE_1)

	imagenet_df = pd.read_csv(imagenet_file_path,
							  sep='\t',
							  encoding='iso-8859-1')

	imagenet_df = imagenet_df[base_column_list +['s_vs_r_image_vgg19_conf']]
	comp_logger.info('Total rows in Imagenet Classification: {}'.format(len(imagenet_df)))

	merge_df = imagenet_df


	# Color Classified Section
	color_file_path = os.path.join(settings.PROJECT_DIR,
								   str(project_id),
								   settings.PROJECT_STEP_FOLDER,
								   settings.PROJECT_STEP_FOLDER_2,
								   settings.PROJECT_STEP_FILE_2)

	color_df = pd.read_csv(color_file_path,
						   sep='\t',
						   encoding='iso-8859-1')

	color_df = color_df[base_column_list +['s_vs_r_image_color_conf','r_image_url_main']]
	comp_logger.info('Total rows in Color Classification: {}'.format(len(color_df)))
	merge_df = pd.merge(merge_df, color_df, how='inner', left_on=base_column_list, right_on=base_column_list)
	comp_logger.info('Total rows in Merged: {}'.format(len(merge_df)))

	comp_logger.info(len(merge_df))
	

	# Price Difference Computed Section
	base_column_list = ['sys_index','s_sku','s_product_url','SERP_URL','SERP_KEY','r_product_url']
	price_file_path = os.path.join(settings.PROJECT_DIR,
								   str(project_id),
								   settings.PROJECT_STEP_FOLDER,
								   settings.PROJECT_STEP_FOLDER_4,
								   settings.PROJECT_STEP_FILE_4)

	price_df = pd.read_csv(price_file_path,
						   sep='\t',
						   encoding='iso-8859-1')

	price_df = price_df[base_column_list +['price_diff_per_sys','s_vs_r_price_conf(0-50)']]
	comp_logger.info('Total rows in Price Differentiation: {}'.format(len(price_df)))
	merge_df = pd.merge(merge_df, price_df, how='inner', left_on=base_column_list, right_on=base_column_list)
	comp_logger.info('Total rows in Merged: {}'.format(len(merge_df)))
	


	# Text Difference Computed Section
	text_file_path = os.path.join(settings.PROJECT_DIR, 
								  str(project_id),
								  settings.PROJECT_STEP_FOLDER,
								  settings.PROJECT_STEP_FOLDER_5,
								  settings.PROJECT_STEP_FILE_5)
	
	text_df = pd.read_csv(text_file_path,sep='\t',encoding='iso-8859-1')
	text_df = text_df[base_column_list+['s_vs_r_text_confidence_matrix','mpn_match','upc_match','asin_match',\
										'gtin_match','title_match']]

	comp_logger.info('Total rows in Text Differentiation: {}'.format(len(text_df)))
	merge_df = pd.merge(merge_df, text_df, how='inner', left_on=base_column_list, right_on=base_column_list)
	comp_logger.info('Total rows in Merged: {}'.format(len(merge_df)))

	# merge_df = merge_df.drop_duplicates(subset=base_column_list, keep=False)
	comp_logger.info(len(merge_df))
	comp_logger.info('before client file merge')	
	merge_df['conf1'] = merge_df['s_vs_r_image_vgg19_conf'].astype(str).replace('True',1).replace('False',0)
	merge_df['conf2'] = merge_df['s_vs_r_image_color_conf'].astype(str).replace('True',1).replace('False',0)
	# merge_df['conf3'] = merge_df['s_vs_r_image_brand_conf'].astype(str).replace('True',1).replace('False',0)
	merge_df['s_vs_r_price_match'] = merge_df['s_vs_r_price_conf(0-50)'].astype(str).replace('True',1).replace('False',0)

	merge_df['s_vs_r_image_match'] = merge_df['conf1'] + merge_df['conf2'] 
	
	merge_df['confidence_score'] = merge_df['s_vs_r_image_match']+ merge_df['s_vs_r_price_match'] + merge_df['s_vs_r_text_confidence_matrix']

	max_confidence = round(merge_df['confidence_score'].max())
	
	# System Match/NotMatch Verdict
	merge_df['Result'] = merge_df['confidence_score'].apply(lambda x:'Match' if x >= settings.MATCH_LOWER_THRESHOLD else 'Non Match')

	# Default Settings
	merge_df['AdminEdit'] = False
	merge_df['confusion'] = ''
	merge_df['human_verdict'] = 'Awaiting'
	merge_df['user'] = 'system'

	del merge_df['conf1']
	del merge_df['conf2']
	del merge_df['s_vs_r_price_match']
	# del merge_df['s_vs_r_text_confidence_matrix']
	# del merge_df['s_vs_r_image_match']
	# del merge_df['confidence_score']



	# Client Input File
	client_df = pd.read_csv(input_file_path,
							sep='\t',
							encoding='iso-8859-1')

	comp_logger.info('Total rows in Client File: {}'.format(len(client_df)))
	client_df = client_df[['sys_index','r_product_url','r_image_url','s_sku','s_product_url',\
						   's_item_name','r_price','s_price']]

	merge_df = pd.merge(merge_df, client_df, how='left', on=['sys_index','r_product_url','s_sku','s_product_url'])
	
	
	comp_logger.info('Total rows in Merged: {}'.format(len(merge_df)))
	
	merge_df.to_csv(output_file_path,
					index=False,
					sep='\t',
					encoding='iso-8859-1') 