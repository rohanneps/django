import os
import pandas as pd

def convert_number_to_percentage(df, column, divident):
	df[column] = df[column].astype(float)
	df[column] = (df[column]/divident)*100
	return df


def convert_feature_to_percentage(df):
	# df = convert_number_to_percentage(df, 'mpn_match', 1)
	# df = convert_number_to_percentage(df, 'upc_match', 1)
	# df = convert_number_to_percentage(df, 'asin_match', 1)
	# df = convert_number_to_percentage(df, 'gtin_match', 1)
	df = convert_number_to_percentage(df, 'title_match', 1)
	df = convert_number_to_percentage(df, 's_vs_r_image_match', 2)
	return df

def assign_groups(df):
	df.loc[df.Result == "Match", 'Group'] = "Grp1"
	df.loc[df.Result == 'Non Match', 'Group'] = "Grp2"
	return df


def main(project_id,client_input_file, step6_output_file, output_file):
	base_column_list = ['sys_index','s_sku','s_product_url','s_image_url', 'SERP_URL','SERP_KEY','r_product_url','r_image_url']

	cpi_conf_df = pd.read_csv(client_input_file, sep='\t', encoding='ISO-8859-1', dtype=object)			# dtype=object used to avoid cases of .0 in gtin and upc literals
	image_text_conf_df = pd.read_csv(step6_output_file, sep='\t', encoding='ISO-8859-1', dtype=object)

	image_text_conf_df = image_text_conf_df[base_column_list+['mpn_match','upc_match','asin_match','gtin_match','title_match','s_vs_r_image_match','price_diff_per_sys','confidence_score','Result','AdminEdit','confusion','human_verdict','user']]

	merged_df = pd.merge(cpi_conf_df, image_text_conf_df, how='inner', on=base_column_list)
	merged_df = merged_df.sort_values(by=['confidence_score'], ascending=False)

	# assigning group, currently boolean based on match/non match
	merged_df = assign_groups(merged_df)
	
	# convert numeric match scores to percentage
	merged_df = convert_feature_to_percentage(merged_df)
	
	column_list = merged_df.columns.tolist()
	merged_df['request_id'] = project_id
	merged_df = merged_df.reset_index()
	merged_df = merged_df[['request_id']+column_list]
	merged_df.fillna(value='',inplace=True)
	merged_df.to_csv(output_file, index=False, sep='\t',encoding='ISO-8859-1')