import os
from bs4 import BeautifulSoup
from GlobalVariables import (
							S3_REGION_LIST,
							BATCH_OUTPUT_DIR_MOBILE
							)
from helper import create_dir


def get_showcase_ad_details(output_dir, soup, query_clean_name):
	showcase_ads_tag = soup.find('div',{'class':'uctzDb'})

	if showcase_ads_tag:
		showcase_ads_query_file = '{}_showcase_ads_result.tsv'.format(query_clean_name)
		showcase_ads_query_file_path = os.path.join(output_dir, showcase_ads_query_file)
		with open(showcase_ads_query_file_path,'w') as req_file:
			req_file.write('Site URL'+'\t'+'Site Name'+'\t'+'Site Category'+'\t'+'Site Text'+'\t'+'Site Additional Info')
			req_file.write('\n')
			showcase_ad_list = showcase_ads_tag.findChildren('div', recursive=False)
			for showcase_ad in showcase_ad_list:
				try:
					showcase_ad_site_url = showcase_ad.find('a')['href']
				except:
					showcase_ad_site_url = ''

				try:
					showcase_ad_category = showcase_ad.find('div',{'class':'mlSk0c'}).text.strip()
				except:
					showcase_ad_category = ''

				showcase_ad_E4HrTe_div_tag = showcase_ad.find('div',{'class':'E4HrTe'})

				try:
					showcase_ad_site_name = showcase_ad.find('span',{'class':'OgoMu'}).text.replace('Visit','').strip()
				except:
					try:
						showcase_ad_site_name = showcase_ad_E4HrTe_div_tag.find('div').text
					except:
						showcase_ad_site_name = ''

				try:
					showcase_ad_site_text = showcase_ad_E4HrTe_div_tag.find('div',{'class':'lc2FU'}).text
				except:
					showcase_ad_site_text = ''

				try:
					showcase_ad_site_additional_info = showcase_ad_E4HrTe_div_tag.find('div',{'class':'g7NDnf'}).text.replace('\xa0',' ')
				except:
					showcase_ad_site_additional_info = ''

				req_file.write(showcase_ad_site_url+'\t'+showcase_ad_site_name+'\t'+showcase_ad_category+'\t'+showcase_ad_site_text+'\t'+showcase_ad_site_additional_info)
				req_file.write('\n')


def main(client):
	# file_list = ['ableton__26_12_2019__12_33_10.html','argireline__26_12_2019__16_00_19.html']
	for S3_REGION in S3_REGION_LIST:
		print(S3_REGION)
		output_dir = BATCH_OUTPUT_DIR_MOBILE.format(client)
		INPUT_DIR = os.path.join(output_dir, S3_REGION, 'page_source')
		OUTPUT_DIR = os.path.join(output_dir, S3_REGION,'showcase_result_computed')

		if os.path.exists(INPUT_DIR):
			create_dir(OUTPUT_DIR)
			for file in os.listdir(INPUT_DIR):
			# for file in file_list:
				# print(file)

				file_path = os.path.join(INPUT_DIR, file)
				with open(file_path, 'r') as f:
					page_data = f.read()

					soup = BeautifulSoup(page_data,'html.parser')
					query_clean_name = file.split('.')[0]
					get_showcase_ad_details(OUTPUT_DIR, soup, query_clean_name)
		else:
			print('{} -- No showcase results for Mobile step 5.a'.format(S3_REGION))

		print('--------------------------------------------')

if __name__ == '__main__':
	main()