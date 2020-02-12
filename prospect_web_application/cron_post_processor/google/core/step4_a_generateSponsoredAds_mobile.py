import os
from bs4 import BeautifulSoup
from GlobalVariables import (
							S3_REGION_LIST,
							BATCH_OUTPUT_DIR_MOBILE
							)
from helper import create_dir



def get_sponsored_ad_details(output_dir, soup, query_clean_name):
	sponsored_ads_tag = soup.find('div',{'class':'EDblX DAVP1 zP8yCf pjhcKc'})

	if sponsored_ads_tag:
		sponsored_ads_query_file = '{}_sponsored_ads_result.tsv'.format(query_clean_name)
		sponsored_ads_query_file_path = os.path.join(output_dir, sponsored_ads_query_file)
		with open(sponsored_ads_query_file_path,'w') as req_file:
			req_file.write('url'+'\t'+'name'+'\t'+'price'+'\t'+'price_drop'+'\t'+'image'+'\t'+'brand'+\
							'\t'+'In Store/Pick up Today'+'\t'+'PRICEC DROP TAG'+'\t'+'SALE TAG'+
							'\t'+'rating'+'\t'+'review'+'\t'+'return_policy')
			req_file.write('\n')
			sponsored_elem_list = sponsored_ads_tag.findChildren('g-inner-card', recursive=False)

			if len(sponsored_elem_list) == 0:
				sponsored_elem_list = soup.findAll('div',{'class':'rWBhnc'})
			for sponsored_elem in sponsored_elem_list:
				# image section:
				try:
					sponsored_elem_image = sponsored_elem.find('img')['src']
				except:
					sponsored_elem_image = ''

				# name price section
				try:
					try:
						sponsored_elem_name = sponsored_elem.find('div',{'class': 'nyhI9c'}).find('h4').text.strip()
					except:
						sponsored_elem_name = sponsored_elem.find('div',{'class': 'lzDfvd Hwk6bc'}).text.strip()
				except:
					sponsored_elem_name = ''

				try:
					sponsored_elem_url = sponsored_elem.find('a')['href']
				except:
					sponsored_elem_url = ''

				try:
					try:
						sponsored_elem_price = sponsored_elem.find('div',{'class': 'dOp6Sc aVryAb'}).find_all(text=True, recursive=False)[0]
					except:
						sponsored_elem_price = sponsored_elem.find('div',{'class': 'RQi8m'}).text.strip()
				except:
					try:
						sponsored_elem_price = sponsored_elem.find('div',{'class': 'dOp6Sc'}).text.strip()
					except:
						sponsored_elem_price = ''

				try:
					# this is for cases where there is no images in sponsored results and many values are present in the same xpath
					sponsored_elem_generic_tag_value = sponsored_elem.find('span',{'class': 'vUd64b'}).text.strip()
				except:
					sponsored_elem_generic_tag_value = ''


				try:
					# not found as of yet
					sponsored_elem_price_drop = sponsored_elem.find('div',{'class': 'wEE4ud'}).text.strip()
				except:
					sponsored_elem_price_drop = ''

				# For In Store/Pickup
				try:
					try:
						sponsored_elem_store_pickup = sponsored_elem.find('div',{'class':'dBmERc'}).find('span').text.strip()
					except:
						if 'pick up' in sponsored_elem_generic_tag_value.lower():
							sponsored_elem_store_pickup = sponsored_elem_generic_tag_value
						else:
							sponsored_elem_store_pickup = ''
				except:
					sponsored_elem_store_pickup = ''

				# For Price Drop Tag
				try:
					# not found as of yet
					sponsored_elem_pricedrop_tag = sponsored_elem.find('div',{'class':'joSMwd vXDus'}).find('span').text.strip()
				except:
					sponsored_elem_pricedrop_tag = ''

				# For Sale Tag
				try:
					sponsored_elem_sale_tag = sponsored_elem.find('div',{'class':'XsRVud'}).find('span').text.strip()
				except:
					sponsored_elem_sale_tag = ''

				

				try:
					try:
						sponsored_elem_brand = sponsored_elem.find('div',{'class': 'hBvPxd a'}).text.strip()
					except:
						sponsored_elem_brand = sponsored_elem.find('span',{'class': 'gu6Kyc'}).text.strip()
				except:
					sponsored_elem_brand = ''

				# for rating and reviews
				try:
					sponsored_elem_rating = sponsored_elem.find('g-review-stars').find('span')['aria-label'].strip()
					sponsored_elem_rating = sponsored_elem_rating.replace('Rated','').replace('out of 5,','').strip()
				except:
					sponsored_elem_rating = ''

				try:
					sponsored_elem_total_reviews = sponsored_elem.find('div',{'class':'QhqGkb'}).text
				except:
					sponsored_elem_total_reviews = ''

				try:
					sponsored_elem_return_policy = sponsored_elem.find('div',{'class':'cYBBsb'}).text.strip()
				except:
					sponsored_elem_return_policy = ''

				req_file.write(sponsored_elem_url+'\t'+sponsored_elem_name+'\t'+sponsored_elem_price+'\t'+\
								sponsored_elem_price_drop+'\t'+sponsored_elem_image+'\t'+sponsored_elem_brand+\
								'\t'+sponsored_elem_store_pickup+'\t'+sponsored_elem_pricedrop_tag+'\t'+sponsored_elem_sale_tag+\
								'\t'+sponsored_elem_rating+'\t'+sponsored_elem_total_reviews+'\t'+sponsored_elem_return_policy)
				req_file.write('\n')

def main(client):

	# file_list = ['ableton__26_12_2019__26_12_2019__16_01_08.html','acqua_di_parma__26_12_2019__20_01_05.html','becca_highlighter__26_12_2019__20_01_07.html']
	for S3_REGION in S3_REGION_LIST:
		print(S3_REGION)
		output_dir = BATCH_OUTPUT_DIR_MOBILE.format(client)
		
		INPUT_DIR = os.path.join(output_dir, S3_REGION, 'page_source')
		OUTPUT_DIR = os.path.join(output_dir, S3_REGION,'sponsored_result_computed')

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
					get_sponsored_ad_details(OUTPUT_DIR, soup, query_clean_name)
		else:
			print('{} -- No sponsored results for Mobile step 4.a'.format(S3_REGION))

		print('--------------------------------------------')

if __name__ == '__main__':
	main()