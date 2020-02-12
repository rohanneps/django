import pandas as pd
from datetime import datetime, timedelta
from GlobalVariables import SPONSORED_TABLE_NAME
from helper import get_region_name
from core.AmazonHandler import AmazonHandler


OUTPUT_COLUMN_LIST = ['Search From','Search Keyword','Search Region','Search Datetime','Result Rank','ASIN',\
						'Product Title','Product Ratings','Product Reviews','Product Is Prime','Product Sponsored']


class SponsoredResultsHandler(AmazonHandler):
	def __init__(self, engine, client, client_file_name):
		AmazonHandler.__init__(self, engine, client, 'sponsored_result','SponsoredResults', OUTPUT_COLUMN_LIST, SPONSORED_TABLE_NAME, client_file_name)

	def get_computed_df(self, file_path, file, region):
		file = file.split('.')[0]
		df = pd.read_csv(file_path, sep='\t')
		df['Query'] = file.split('--')[0]
		df['Product Sponsored'] = 'Yes'
		# df['Query'] = df['Query'].str.replace('_',' ')
		
		# Convert GMT to EST
		date_time_stamp = file.split('--')[1].split('_sponsored_result')[0]
		date_time_obj = datetime.strptime(date_time_stamp, "%d_%m_%Y__%H_%M_%S")
		est_date_time_obj = date_time_obj - timedelta(hours=5)
		df['Search Datetime'] = est_date_time_obj.strftime('%m-%d-%Y:%H:%M:%S')

		# df['rating'] = df['rating'].apply(lambda x: x.split(' ')[0].replace('(','').replace(')','') if type(x)!=float else x)
		df['rating'] = df['rating'].apply(lambda x: x.split(' ')[0] if type(x)!=float else x)

		df['total_ratings'] = df['total_ratings'].astype(str).fillna(value='')
		df['total_ratings'] = df['total_ratings'].str.replace(',','')
		# df['total_ratings'] = df['total_ratings'].str.replace('k+','000').str.replace('+','')
		df['ASIN'] = df['url'].apply(lambda x: x.split('d/')[1].split('?')[0])

		df.rename(columns=
					{	
						'Query' : 'Search Keyword',
						'name' : 'Product Title',
						'rating' : 'Product Ratings',
						'total_ratings' : 'Product Reviews',
						'sale_price' :'Product Sale Price',
						'marked_price' : 'Product Marked Price',
						'prime_info' : 'Product Is Prime'
						},

					inplace=True)

		total_product_count = len(df)
		df['Result Rank'] = range(1, total_product_count+1)
		df['Search Region'] = get_region_name(region)
		df['Search From'] = 'Desktop'
		df = df[OUTPUT_COLUMN_LIST]
		return df
