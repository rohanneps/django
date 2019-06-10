import pandas as pd
import os



def main(input_file_path, output_dir, output_file_name, result_image_file_path):
	cpi_conf_df = pd.read_csv(input_file_path, sep='\t', encoding='ISO-8859-1')
	cpi_conf_df = cpi_conf_df[cpi_conf_df['s_image_url'].notnull()]
	# column_list = ['sku','searchurl','s_product_url','s_image_url', 'r_link','r_title','r_image']
	column_list = ['sys_index','s_sku','SERP_URL','SERP_KEY','s_product_url','s_image_url', 'r_product_url','r_item_name']
	cpi_conf_df = cpi_conf_df[column_list]
	result_image_df = pd.read_csv(result_image_file_path, sep='\t', encoding='ISO-8859-1')
	cpi_conf_df = pd.merge(cpi_conf_df, result_image_df, how='left', on=['r_item_name'])
	cpi_conf_df.to_csv(os.path.join(output_dir, output_file_name), index=False, sep='\t',  encoding='ISO-8859-1')
