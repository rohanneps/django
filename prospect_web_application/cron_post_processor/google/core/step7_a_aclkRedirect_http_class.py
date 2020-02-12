import requests
import pandas as pd
import numpy as np
import os
from GlobalVariables import (
							MERGED_OUTPUT_PATH,
							OUTPUT_DATE_DIR,
							PAGE_TIMEOUT,
							ACLK_REDIRECT_HTTP_OUTPUT_FILE,
							ACLK_REDIRECT_LISTING_HTTP_FILE,
							SHOWCASE_FILE_PRODUCT_URL_HEADER,
							NUM_OF_ACLK_REDIRECT_THREADS
							)
from helper import get_store, get_store_url
from threading import Thread



class AclkRedirecterThread(Thread):
	
	def __init__(self, thread_name, aclk_url_list):
		Thread.__init__(self)
		self.thread_name = thread_name
		self.aclk_df = pd.DataFrame(columns=['url','redirected_url'])
		self.aclk_url_list = aclk_url_list

	def get_domain_redirected_url(self, url):
		try:
			if 'www.googleadservices.com/pagead/aclk' in url:
				res = requests.get(url, timeout=PAGE_TIMEOUT)
			else:
				# for /aclk
				res = requests.get('https://www.google.com'+url, timeout=PAGE_TIMEOUT)
			return res.url
		except:
			return url

	def run(self):
		for cnt, aclk_url in enumerate(self.aclk_url_list):
			self.aclk_url_dict = {}
			# print(cnt, aclk_url)
			redirected_url = self.get_domain_redirected_url(aclk_url)
			# print(redirected_url)
			self.aclk_url_dict['url'] = aclk_url
			self.aclk_url_dict['redirected_url'] = redirected_url
			self.aclk_df = self.aclk_df.append(self.aclk_url_dict, ignore_index=True)



def get_aclk_redirect_df(aclk_url_list, client):
	"""
	GET the aclk url and redirect url dataframe and persistance.
	"""
	if not os.path.exists(ACLK_REDIRECT_LISTING_HTTP_FILE.format(client)):
		print('HTTP aclk redirect file doesn\'t exist. Creating..')

		aclk_df = pd.DataFrame(columns=['url','redirected_url'])

		# Threading aclk redirect and merging result
		acl_url_subset_lists = np.array_split(aclk_url_list, NUM_OF_ACLK_REDIRECT_THREADS)
		thread_list = []

		for thread_num in range(0, NUM_OF_ACLK_REDIRECT_THREADS):
			aclk_url_subset_list = acl_url_subset_lists[thread_num]
			thread_name = 'Thread{}'.format(thread_num)
			thread = AclkRedirecterThread(thread_name, aclk_url_subset_list)
			thread_list.append(thread)		
			thread.start()

		for thread in thread_list:
			thread.join()
			aclk_df = aclk_df.append(thread.aclk_df)


		aclk_df.to_csv(ACLK_REDIRECT_LISTING_HTTP_FILE.format(client), index=False, sep='\t')
	else:
		print('HTTP aclk redirect file exists.')
		aclk_df = pd.read_csv(ACLK_REDIRECT_LISTING_HTTP_FILE.format(client), sep='\t')
	return aclk_df




def main(client):
	step6_output_file = MERGED_OUTPUT_PATH.format(client)
	if os.path.exists(step6_output_file):
		df = pd.read_csv(step6_output_file,sep='\t')
		df = df.fillna(value='')
		aclk_url_list = df[df[SHOWCASE_FILE_PRODUCT_URL_HEADER].str.contains('/aclk')][SHOWCASE_FILE_PRODUCT_URL_HEADER].unique().tolist()
		aclk_url_list_count = len(aclk_url_list)
		print('Total aclk count: {}'.format(aclk_url_list_count))
		if aclk_url_list_count > 0:
			aclk_df = get_aclk_redirect_df(aclk_url_list, client)

			merged_df = pd.merge(df, aclk_df, how='left',left_on=[SHOWCASE_FILE_PRODUCT_URL_HEADER],right_on=['url'])
			merged_df = merged_df.fillna(value='')
			# merged_df[merged_df[SHOWCASE_FILE_PRODUCT_URL_HEADER].isnull()]
			# merged_df[merged_df[SHOWCASE_FILE_PRODUCT_URL_HEADER]=='']
			merged_df[SHOWCASE_FILE_PRODUCT_URL_HEADER] = merged_df.apply(lambda x: x['redirected_url'] if '/aclk' in x[SHOWCASE_FILE_PRODUCT_URL_HEADER] and x['redirected_url']!='' else x[SHOWCASE_FILE_PRODUCT_URL_HEADER], axis=1)
			merged_df['PLA Store'] = merged_df.apply(get_store, axis=1)
			
			merged_df['PLA Domain'] = merged_df.apply(get_store_url, axis=1)

			del merged_df['url']
			del merged_df['redirected_url']
			merged_df.to_csv(ACLK_REDIRECT_HTTP_OUTPUT_FILE.format(client), index=False, sep='\t')
		else:
			df.to_csv(ACLK_REDIRECT_HTTP_OUTPUT_FILE.format(client), index=False, sep='\t')

	else:
		print('No output of step7a')
if __name__ == '__main__':
	main()