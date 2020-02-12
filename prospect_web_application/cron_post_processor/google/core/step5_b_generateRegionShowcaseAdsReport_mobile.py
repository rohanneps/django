import pandas as pd
import os
from datetime import datetime, timedelta
from GlobalVariables import (
							S3_REGION_LIST,
							BATCH_OUTPUT_DIR_MOBILE
							
							)
from helper import get_region_name

TITLE_CONVERSION_DICT = {
						'Site Name':'PLA Store',
						'name': 'PLA Title',
						'url' : 'PLA URL',
						'price' : 'PLA Price Text',
						'Min Price' : 'PLA Price MIN',
						'Max Price' : 'PLA Price MAX',
						'review' : 'PLA Reviews',
						'rating' : 'PLA Ratings',
						'price_drop' : 'PLA PriceDrop Percentage',
						'Query': 'Search Keyword',
						'PRICEC DROP TAG': 'PLA Has Price Drop Tag',
						'SALE TAG': 'PLA Has Sale Tag',
						'Store_Name': 'PLA Domain',
						'In Store/Pick up Today' : 'PLA Has Special Tags'
						}

OUTPUT_COLUMN_LIST = ['Search From','Search Keyword','Search Region','Search Datetime','PLA Rank','PLA Store','PLA Title',\
					  'PLA Price Text','PLA Price MIN','PLA Price MAX','PLA PriceDrop Percentage','PLA Has Special Tags',\
					  'PLA Has Price Drop Tag','PLA Has Sale Tag',\
					  'PLA Ratings','PLA Reviews','PLA Domain','PLA URL','PLA/Showcase']

EXTRA_COLUMNS_FOR_SHOWCASE = ['In Store/Pick up Today']

def get_domain_url(url):
		if url=='':
			return url
		elif '/aclk' in url:
			return url
		else:
			return url.split('/')[2]

def get_computed_df(file_path, file, region):
	file = file.split('.')[0]
	df = pd.read_csv(file_path, sep='\t')
	df['Query'] = file.split('--')[0]
	# df['Query'] = df['Query'].str.replace('_',' ')
	
	# Convert GMT to EST
	date_time_stamp = file.split('--')[1].split('_showcase_ads')[0]
	date_time_obj = datetime.strptime(date_time_stamp, "%d_%m_%Y__%H_%M_%S")
	est_date_time_obj = date_time_obj - timedelta(hours=5)
	df['Search Datetime'] = est_date_time_obj.strftime('%m-%d-%Y:%H:%M:%S')
	
	column_list = df.columns.tolist()
	for col in TITLE_CONVERSION_DICT.keys():
		if col not in column_list:
			df[col]=''

	for col in EXTRA_COLUMNS_FOR_SHOWCASE:
		if col not in column_list:
			df[col]=''

	df['Min Price'] = df['price'].apply(lambda x: x.split('-')[0])
	df['Max Price'] = df['price'].apply(lambda x: x.split('-')[-1] if '-' in x else '')

	df['Store_Name'] = df['url'].apply(get_domain_url)
	df.rename(columns=TITLE_CONVERSION_DICT,inplace=True)
	total_product_count = len(df)
	df['PLA Rank'] = range(1, total_product_count+1)
	df['Search Region'] = get_region_name(region)
	df['PLA/Showcase'] = 'Showcase'
	df['Search From'] = 'Mobile'
	df = df[OUTPUT_COLUMN_LIST]
	return df

def main(client):
	for S3_REGION in S3_REGION_LIST:
		output_dir = BATCH_OUTPUT_DIR_MOBILE.format(client)
		INPUT_DIR = os.path.join(output_dir, S3_REGION,'showcase_result_computed')
		OUTPUT_DIR = os.path.join(output_dir, S3_REGION)
		output_df = pd.DataFrame()
		print(S3_REGION)

		if os.path.exists(INPUT_DIR):
			for file in os.listdir(INPUT_DIR):
				# print(file)
				if '~' not in file:
					file_path = os.path.join(INPUT_DIR, file)
					
					try:
						df = get_computed_df(file_path, file, S3_REGION)
						output_df = output_df.append(df)
					except Exception as e:
						print(str(e))
						print('Exception for file: {}'.format(file_path))

			if len(output_df)>0:
				output_df.to_csv(os.path.join(OUTPUT_DIR,'ShowcaseAds_Combined{}.tsv'.format(S3_REGION)), index=False,sep='\t')
			else:
				print('{} -- No sponsored results for Mobile step 5.b'.format(S3_REGION))
		else:
			print('{} -- No sponsored results for Mobile step 5.b'.format(S3_REGION))

if __name__ == '__main__':
	main()