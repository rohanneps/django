import os
import pandas as pd

def convert_number_to_percentage(df,
								column,
								divident):
	df[column] = df[column].astype(float)
	df[column] = (df[column]/divident)*100
	return df


def convert_feature_to_percentage(df):
	df = convert_number_to_percentage(df, 'title_match', 1)
	df = convert_number_to_percentage(df, 's_vs_r_image_match', 2)
	return df


def assign_groups(df):
	df.loc[df.Result == "Match", 'Group'] = "Grp1"
	df.loc[df.Result == 'Non Match', 'Group'] = "Grp2"
	return df


def assign_request_id_and_product_id(df, project_id):
	# Set Request ID to the Project for insertion into elasticsearch
	column_list = df.columns.tolist()
	df['request_id'] = project_id
	df['pid'] = df.groupby(['s_sku']).ngroup()					# assigning unique product id
	df = df.reset_index()
	df = df[['request_id','pid']+column_list]
	return df


def main(project_id,
		 client_input_file,
		 step6_output_file,
		 output_file):

	
	base_column_list = ['sys_index','s_sku','s_product_url','s_image_url',\
						'SERP_URL','SERP_KEY','r_product_url','r_image_url']

	cpi_conf_df = pd.read_csv(client_input_file,
							  sep='\t',
							  encoding='ISO-8859-1',
							  dtype=object)			# dtype=object used to avoid cases of .0 in gtin and upc literals

	image_text_conf_df = pd.read_csv(step6_output_file,
									 sep='\t',
									 encoding='ISO-8859-1',
									 dtype=object)

	image_text_conf_df = image_text_conf_df[base_column_list+['r_image_url_main',\
						'mpn_match','upc_match','asin_match','gtin_match','title_match',\
						's_vs_r_image_match','price_diff_per_sys','confidence_score','Result',\
						'AdminEdit','confusion','human_verdict','user']]

	merged_df = pd.merge(cpi_conf_df, image_text_conf_df, how='inner', on=base_column_list)
	merged_df = merged_df.sort_values(by=['confidence_score'], ascending=False)
	
	# assigning group, currently boolean based on match/non match
	merged_df = assign_groups(merged_df)
	
	# convert numeric match scores to percentage
	merged_df = convert_feature_to_percentage(merged_df)
	
	merged_df = assign_request_id_and_product_id(merged_df, project_id)

	merged_df.fillna(value='',inplace=True)
	merged_df.to_csv(output_file,
					 index=False,
					 sep='\t',
					 encoding='ISO-8859-1')
