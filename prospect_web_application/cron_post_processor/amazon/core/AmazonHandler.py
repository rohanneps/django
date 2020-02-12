import pandas as pd
import os
from GlobalVariables import (
							BATCH_OUTPUT_DIR_PC,
							S3_REGION_LIST,
							WEB_APP_MEDIA_ROOT,
							MANDATORY_COLUMN_HEADERS
							)
import urllib.parse

class AmazonHandler():

	def __init__(self, engine, client, input_dir, result_type, output_columns, table_name, client_file_name):
		self.engine = engine
		self.client = client
		self.result_type = result_type
		self.output_columns = output_columns
		self.input_dir = input_dir
		self.table_name = table_name
		self.client_file_name = client_file_name

	def getComputedDf(self, file_path, file, region):
		pass


	def main(self):
		for S3_REGION in S3_REGION_LIST:
			output_dir = BATCH_OUTPUT_DIR_PC.format(self.client)
			
			INPUT_DIR = os.path.join(output_dir, S3_REGION, self.input_dir)
			OUTPUT_DIR = os.path.join(output_dir, S3_REGION)
			output_df = pd.DataFrame()
			print(S3_REGION)

			if os.path.exists(INPUT_DIR):
				for file in os.listdir(INPUT_DIR):
					# print(file)
					if '~' not in file:
						file_path = os.path.join(INPUT_DIR, file)
						# df = get_computed_df(file_path, file, S3_REGION)
						# output_df = output_df.append(df)
						try:
							df = self.get_computed_df(file_path, file, S3_REGION)
							output_df = output_df.append(df)
						except Exception as e:
							print(str(e))
							print('Exception for file: {}'.format(file_path))
				

				if len(output_df)>0:
					output_df.to_csv(os.path.join(OUTPUT_DIR,'{}_Combined{}.tsv'.format(self.result_type,S3_REGION)), index=False,sep='\t')
				else:
					print('{} -- No {} results for {}'.format(S3_REGION, self.result_type,  __name__))

			else:
				print('{} -- No {} results for {}'.format(S3_REGION, self.result_type,  __name__))
		
		return self.mergeRegions()

	def mergeRegions(self):
		output_df = pd.DataFrame()
		output_dir = BATCH_OUTPUT_DIR_PC.format(self.client)
		
		for region in S3_REGION_LIST:
			print(region)
			region_related_path = os.path.join(output_dir, region, '{}_Combined{}.tsv'.format(self.result_type, region))
			if os.path.exists(region_related_path):
				df = pd.read_csv(region_related_path, sep='\t')
				output_df = output_df.append(df)

		record_count = len(output_df)
		if record_count>0:
			output_df.to_csv(os.path.join(output_dir,'{}_Combined_allregion.tsv'.format(self.result_type)), index=False,sep='\t')
			print('Inserting details to database.')
			self.insertRecordsToDB(output_df)
		else:
			print('No {} for all regions.'.format(self.result_type))
		return record_count


	def insertRecordsToDB(self, df):
		client_df = pd.read_csv(os.path.join(WEB_APP_MEDIA_ROOT, self.client_file_name), sep='\t')
		client_df = client_df[MANDATORY_COLUMN_HEADERS]
		# client_df['keyword'] = client_df['Search Keyword'].apply(get_cleaned_name)
		client_df['keyword'] = client_df['Search Keyword'].apply(lambda x: urllib.parse.quote(x).replace('/','__'))
		df.rename(columns={'Search Keyword':'keyword'}, inplace=True)

		# client_df = client_df[['URL GROUP','URL', 'URL_TYPE', ,'Search Keyword']]
		merged_df = pd.merge(client_df,df, how='inner', on=['keyword'])
		del merged_df['keyword']
		merged_df.to_sql(name=self.table_name, con=self.engine, if_exists='append', index=False)