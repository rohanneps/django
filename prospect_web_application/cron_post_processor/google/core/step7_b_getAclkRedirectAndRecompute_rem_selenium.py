import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from GlobalVariables import (
							OUTPUT_DATE_DIR,
							SELENIUM_WEBDRIVER_PATH,
							SELENIUM_HEADLESS_CHROMIUM_PATH,
							PAGE_TIMEOUT,
							SHOWCASE_FILE_PRODUCT_URL_HEADER,
							ACLK_REDIRECT_HTTP_OUTPUT_FILE,
							ADS_COMPUTED_OUTPUT_FILE_PATH,
							ACLK_REDIRECT_LISTING_SEL_FILE,
							BASE_DIR
							)
import os
from helper import get_store

def getFullUrl(url):
	if 'www.googleadservices.com/pagead/aclk' in url:
		url = url
	elif 'aclk' in url:
		url = 'https://www.google.com'+ url 		# for cases like /aclk
	else:
		return url


def get_aclk_redirect_df(aclk_url_list, client):
	"""
	GET the aclk url and redirect url dataframe and persistance.
	"""
	if not os.path.exists(ACLK_REDIRECT_LISTING_SEL_FILE.format(client)):
		print('Selenium aclk redirect file doesn\'t exist. Creating..')
		aclk_df = pd.DataFrame(columns=['url','redirected_url'])

		for cnt, aclk_url in enumerate(aclk_url_list):
			aclk_url_dict = {}
			# print(cnt, aclk_url)
			redirected_url = get_domain_redirected_url(aclk_url)
			# print(redirected_url)
			aclk_url_dict['url'] = aclk_url
			aclk_url_dict['redirected_url'] = redirected_url
			aclk_df = aclk_df.append(aclk_url_dict, ignore_index=True)

		aclk_df.to_csv(ACLK_REDIRECT_LISTING_SEL_FILE.format(client), index=False, sep='\t')
	else:
		print('Selenium aclk redirect file exists.')
		aclk_df = pd.read_csv(ACLK_REDIRECT_LISTING_SEL_FILE.format(client), sep='\t')
	return aclk_df

def main(client):
	step7_output_file = ACLK_REDIRECT_HTTP_OUTPUT_FILE.format(client)
	if os.path.exists(step7_output_file):
		df = pd.read_csv(step7_output_file, sep='\t')
		df = df.fillna(value='')
		aclk_url_list = df[df[SHOWCASE_FILE_PRODUCT_URL_HEADER].str.contains('/aclk')][SHOWCASE_FILE_PRODUCT_URL_HEADER].unique().tolist()
		aclk_url_list_count = len(aclk_url_list)
		print('Total aclk count: {}'.format(aclk_url_list_count))
		# if aclk_url_list_count > 0:
		# 	# driver = webdriver.Firefox(executable_path=SELENIUM_WEBDRIVER_PATH)
		# 	chrome_options = Options()
		# 	chrome_options.add_argument('--headless')
		# 	chrome_options.add_argument('--no-sandbox')
		# 	chrome_options.add_argument('--disable-gpu')
		# 	chrome_options.add_argument('--window-size=1280x1696')
		# 	chrome_options.add_argument('--user-data-dir=/tmp/user-data')
		# 	chrome_options.add_argument('--hide-scrollbars')
		# 	chrome_options.add_argument('--enable-logging')
		# 	chrome_options.add_argument('--log-level=0')
		# 	chrome_options.add_argument('--v=99')
		# 	chrome_options.add_argument('--single-process')
		# 	chrome_options.add_argument('--data-path=/tmp/data-path')
		# 	chrome_options.add_argument('--ignore-certificate-errors')
		# 	chrome_options.add_argument('--disable-dev-shm-usage')
		# 	chrome_options.add_argument('--homedir=/tmp')
		# 	chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
		# 	chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
		# 	chrome_options.binary_location = BASE_DIR + SELENIUM_HEADLESS_CHROMIUM_PATH

		# 	driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=SELENIUM_WEBDRIVER_PATH)
		# 	driver.set_page_load_timeout(PAGE_TIMEOUT)
			
		# 	aclk_df = get_aclk_redirect_df(aclk_url_list, client)
			
		# 	merged_df = pd.merge(df, aclk_df, how='left',left_on=[SHOWCASE_FILE_PRODUCT_URL_HEADER],right_on=['url'])
		# 	merged_df[SHOWCASE_FILE_PRODUCT_URL_HEADER] = merged_df.apply(lambda x: x['redirected_url'] if '/aclk' in x[SHOWCASE_FILE_PRODUCT_URL_HEADER] and x['redirected_url']!='' else x[SHOWCASE_FILE_PRODUCT_URL_HEADER], axis=1)
		# 	merged_df['PLA Store'] = merged_df.apply(get_store, axis=1)
		# 	del merged_df['url']
		# 	del merged_df['redirected_url']
		# 	merged_df.to_csv(ADS_COMPUTED_OUTPUT_FILE_PATH.format(client), index=False,sep='\t')
		# 	driver.close()
		# else:
		df[SHOWCASE_FILE_PRODUCT_URL_HEADER] = df[SHOWCASE_FILE_PRODUCT_URL_HEADER].apply(getFullUrl)
		df['PLA Store'] = df.apply(get_store, axis=1)
		df.to_csv(ADS_COMPUTED_OUTPUT_FILE_PATH.format(client), index=False,sep='\t')

	else:
		print('No output of step7b')
		
if __name__ == '__main__':
	main()