import pandas as pd
import os
from datetime import datetime, timedelta
from GlobalVariables import (
							S3_REGION_LIST,
							BATCH_OUTPUT_DIR_PC
							)
from helper import get_region_name
from threading import Thread

class PcSponsoredResultProcessorThread(Thread):
	
	def __init__(self, thread_name, client_name):
		Thread.__init__(self)
		self.thread_name = thread_name
		self.client_name = client_name
		self.batch_output_dir = BATCH_OUTPUT_DIR_PC.format(self.client_name)
		self.output_column_list = ['Search From','Search Keyword','Search Region','Search Datetime','PLA Rank','PLA Store','PLA Title',\
								  'PLA Price Text','PLA Price MIN','PLA Price MAX','PLA PriceDrop Percentage','PLA Has Special Tags',\
								  'PLA Has Price Drop Tag','PLA Has Sale Tag',\
								  'PLA Ratings','PLA Reviews','PLA Domain','PLA URL','PLA/Showcase']
	def get_domain_url(self, url):
		if url=='':
			return url
		elif '/aclk' in url:
			return url
		else:
			return url.split('/')[2]


	def get_range_price(self, price):
		if price.count('$') ==2 :
			return price.replace('$','-$')[1:]
		else:
			return price

	def get_computed_df(self, file_path, file, region):
		file = file.split('.')[0]
		df = pd.read_csv(file_path, sep='\t')
		del df['image']
		del df['return_policy']
		df['url'] = df['url'].fillna(value='')
		df['price'] = df['price'].fillna(value='')
		df['review'] = df['review'].fillna(value='')
		df['Query'] = file.split('--')[0]
		# df['Query'] = df['Query'].str.replace('custom_t_shirts','Custom T-shirts').str.replace('men_s_shoes','Men\'s shoes').str.replace('red_sweater','Red Sweater')
		# df['Query'] = df['Query'].str.replace('_',' ')

		# Convert GMT to EST
		date_time_stamp = file.split('--')[1].split('_sponsored_')[0]
		date_time_obj = datetime.strptime(date_time_stamp, "%d_%m_%Y__%H_%M_%S")
		est_date_time_obj = date_time_obj - timedelta(hours=5)
		df['Search Datetime'] = est_date_time_obj.strftime('%m-%d-%Y:%H:%M:%S')

		df['Store_Name'] = df['url'].apply(self.get_domain_url)

		df['url'] = df['url'].apply(lambda x: x.split('?')[0] if 'google.com' in x and 'www.googleadservices.com/pagead/aclk' not in x else x)
		df['price_drop'] = df['price_drop'].apply(lambda x: x.split('%')[0] if type(x)!=float else x)

		df['Min Price'] = df['price'].apply(lambda x: x.split('-')[0])
		df['Max Price'] = df['price'].apply(lambda x: x.split('-')[-1] if '-' in x else '')

		df['rating'] = df['rating'].apply(lambda x: x.split(' ')[1] if type(x)!=float else x)
		df['review'] = df['review'].apply(lambda x: x.split(' ')[0].replace('(','').replace(')','') if type(x)!=float else x)
		df['review'] = df['review'].fillna(value='')
		df['review'] = df['review'].str.replace('k+','000').str.replace('+','')

		# df['price'] = df['price'].apply(self.get_range_price)
		df.rename(columns=
					{
					'brand':'PLA Store',
					'name': 'PLA Title',
					'url' : 'PLA URL',
					'price' : 'PLA Price Text',
					'Min Price' : 'PLA Price MIN',
					'Max Price' : 'PLA Price MAX',
					'review' : 'PLA Reviews',
					'rating' : 'PLA Ratings',
					'price_drop' : 'PLA PriceDrop Percentage',
					'Hour': 'Search Hour',
					'Date': 'Search Date',
					'Query': 'Search Keyword',
					'PRICEC DROP TAG': 'PLA Has Price Drop Tag',
					'SALE TAG': 'PLA Has Sale Tag',
					'Store_Name': 'PLA Domain',
					'In Store/Pick up Today' : 'PLA Has Special Tags'
					},

						inplace=True)
		

		total_product_count = len(df)

		df['PLA Rank'] = range(1, total_product_count+1)
		df['Search Region'] = get_region_name(region)
		df['PLA/Showcase'] = 'PLA'
		df['Search From'] = 'Desktop'
		df = df[df['PLA URL']!='']
							
		df = df[self.output_column_list]
		return df
		
	def start_region_file_computation(self):
		for S3_REGION in S3_REGION_LIST:
			INPUT_DIR = os.path.join(self.batch_output_dir, S3_REGION,'sponsored_result')
			OUTPUT_DIR = os.path.join(self.batch_output_dir, S3_REGION)
			output_df = pd.DataFrame()
			print('{}: {}'.format(self.thread_name, S3_REGION))

			if os.path.exists(INPUT_DIR):
				for file in os.listdir(INPUT_DIR):
					# print(file)
					file_path = os.path.join(INPUT_DIR, file)
					# df = self.get_computed_df(file_path, file, S3_REGION)
					# output_df = output_df.append(df)
					try:
						df = self.get_computed_df(file_path, file, S3_REGION)
						output_df = output_df.append(df)
					except Exception as e:
						print(str(e))
						print('Exception for file: {}:{}'.format(self.thread_name, file_path))

				output_df.to_csv(os.path.join(OUTPUT_DIR,'SponsoredResult_Combined{}.tsv'.format(S3_REGION)), index=False,sep='\t')
			else:
				print('{}: {} -- No sponsored results for Desktop'.format(self.thread_name, S3_REGION))

			


	def merge_region_results(self):
		output_df = pd.DataFrame()
		for region in S3_REGION_LIST:
			print('{}: {}'.format(self.thread_name, region))
			region_related_path = os.path.join(self.batch_output_dir, region, 'SponsoredResult_Combined{}.tsv'.format(region))
			if os.path.exists(region_related_path):
				df = pd.read_csv(region_related_path, sep='\t')
				output_df = output_df.append(df)

		if len(output_df)>0:
			for col in ['PLA Price Text', 'PLA Price MIN', 'PLA Price MAX']:
				output_df[col] = output_df[col].fillna(value='')
				output_df[col] = output_df[col].str.replace('$','').str.replace(',','').str.strip()

			output_df.to_csv(os.path.join(self.batch_output_dir,'SponsoredResult_Combined_allregion.tsv'), index=False,sep='\t')
		else:
			print('No sponsored Desktop for all regions.')	


	def run(self):
		self.start_region_file_computation()
		self.merge_region_results()
		print('{} Completed'.format(self.thread_name))