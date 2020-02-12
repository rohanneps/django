import pandas as pd
import os
from GlobalVariables import (
							BATCH_OUTPUT_DIR_PC,
							BATCH_OUTPUT_DIR_MOBILE,
							OUTPUT_DATE_DIR,
							MERGED_OUTPUT_PATH,
							TOP_N_RANK,
							MANDATORY_COLUMN_HEADERS,
							WEB_APP_MEDIA_ROOT
							)

from helper import get_cleaned_name
import urllib.parse


def process_prospect_df(df, client, client_file_name):
	client_df = pd.read_csv(os.path.join(WEB_APP_MEDIA_ROOT, client_file_name), sep='\t')
	client_df = client_df[MANDATORY_COLUMN_HEADERS]
	# client_df['keyword'] = client_df['Search Keyword'].apply(get_cleaned_name)
	client_df['keyword'] = client_df['Search Keyword'].apply(lambda x: urllib.parse.quote(x).replace('/','__'))
	df.rename(columns={'Search Keyword':'keyword'}, inplace=True)

	# client_df = client_df[['URL GROUP','URL', 'URL_TYPE', ,'Search Keyword']]
	merged_df = pd.merge(client_df,df, how='inner', on=['keyword'])
	del merged_df['keyword']
	return merged_df


def main(client, client_file_name):
	output_df = pd.DataFrame()
	
	output_dir_pc = BATCH_OUTPUT_DIR_PC.format(client)
	output_dir_mobile = BATCH_OUTPUT_DIR_MOBILE.format(client)

	pla_ads_pc_file_path = os.path.join(output_dir_pc, 'SponsoredResult_Combined_allregion.tsv')
	if os.path.exists(pla_ads_pc_file_path):
		df = pd.read_csv(pla_ads_pc_file_path, sep='\t')
		output_df = output_df.append(df)

	pla_ads_mobile_file_path = os.path.join(output_dir_mobile, 'SponsoredAds_Combined_allregion.tsv')
	if os.path.exists(pla_ads_mobile_file_path):
		df = pd.read_csv(pla_ads_mobile_file_path, sep='\t')
		output_df = output_df.append(df)

	showcase_ads_mobile_file_path = os.path.join(output_dir_mobile, 'ShowcaseAds_Combined_allregion.tsv')
	if os.path.exists(showcase_ads_mobile_file_path):
		df = pd.read_csv(showcase_ads_mobile_file_path, sep='\t')
		output_df = output_df.append(df)


	# Getting Only Top Ranked Items
	output_df_count = len(output_df)
	print(output_df_count)

	if output_df_count>0:
		output_df = process_prospect_df(output_df, client, client_file_name)
		output_df['PLA Rank'] = output_df['PLA Rank'].astype(int)
		
		# Normalizing Field Value
		output_df['PLA Has Sale Tag'] = output_df['PLA Has Sale Tag'].fillna(value='').str.upper()

		column_list = output_df.columns.tolist()
		output_df['Prospect Name'] = client
		output_df = output_df[['Prospect Name']+column_list]
		output_df.to_csv(MERGED_OUTPUT_PATH.format(client), index=False,sep='\t')
	else:
		print('No output of step6')
		
if __name__ == '__main__':
	main()