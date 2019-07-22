import pandas as pd
import os

class PriceDiffereCalculator(object):

	'''
	Provides the Price Difference between source and result product combination

	'''
	def __init__(self,
				input_file_path, 
				output_file_path):

		self.PRICE_DIFF_LIST = []
		self.PRICE_CONF1 = []
		# self.PRICE_CONF2 = []
		# self.PRICE_CONF3 = []
		self.PRICE_CONF4 = []
		self.input_file_path = input_file_path
		self.output_file_path = output_file_path


	def getAvgPrice(self,
					platfrom_product_price,
					split_by):

		price_list = platfrom_product_price.lower().split(split_by)
		price_total = 0
		for price_item in price_list:
			price_total += float(price_item)

		return (price_total/len(price_list))


	def getClientPlatformProductPriceDiff(self,
										  product_price,
										  platfrom_product_price ):
		try:
			product_price = float(product_price.replace('$','').replace(',',''))
		except:
			product_price = float(product_price)

		if '.-.' in platfrom_product_price:
			platfrom_product_price = self.getAvgPrice(platfrom_product_price,'.-.')

		# for cases like $21.77\nTrending
		if '\n' in platfrom_product_price:
			platfrom_product_price = platfrom_product_price.split('\n')[0].strip()
		try:
			platfrom_product_price = float(platfrom_product_price)
		except:
			platfrom_product_price = float(platfrom_product_price.split(' ')[0].replace('$','').replace(',',''))
		price_diff = abs(product_price - platfrom_product_price)
		
		if (product_price < platfrom_product_price):
			if product_price== 0:						# handler for cases where client product price is 0
				product_price = 1
			price_diff_per = (price_diff/product_price)*100
		else:
			if platfrom_product_price== 0:				# handler for cases where target platform price is 0
				platfrom_product_price = 1
			price_diff_per = (price_diff/platfrom_product_price)*100
		price_diff_per = float("%.2f" % price_diff_per)
		return price_diff_per


	def process(self,
		        row):
		sku = row['s_sku']
		client_price = row['s_price']

		compare_price = row['r_price']

		if str(compare_price) =='nan':
			self.PRICE_DIFF_LIST.append('cannot compare price')
			self.PRICE_CONF1.append(False)
			# self.PRICE_CONF2.append(False)
			# self.PRICE_CONF3.append(False)
			self.PRICE_CONF4.append(False)
		else:

			# Cleaning Source Price
			try:
				client_price = client_price.split(' ')[0]
			except:
				# handling for empty source price
				pass

			if type(compare_price) == float:
				compare_price = str(compare_price)

			# Cleaning Target Platfrom Price
			if '$ ' in compare_price:
				compare_price = compare_price.replace('$ ','$').replace(' ','.')
				compare_price = compare_price.split('.-.')[0]
				
			compare_price = compare_price.split(' ')[0].replace('$ ','').replace(' ','.').replace(',','')

			price_diff_per = self.getClientPlatformProductPriceDiff(client_price,compare_price)
			# print(price_diff_per)
			self.PRICE_DIFF_LIST.append(price_diff_per)
			
			if price_diff_per==0:
				self.PRICE_CONF1.append(True)
			else:
				self.PRICE_CONF1.append(False)

			# if (price_diff_per>0) and (price_diff_per<=10):
			# 	self.PRICE_CONF2.append(True)
			# else:
			# 	self.PRICE_CONF2.append(False)

			# if (price_diff_per>10) and (price_diff_per<=65):
			# 	self.PRICE_CONF3.append(True)
			# else:
			# 	self.PRICE_CONF3.append(False)


			if (price_diff_per>=0) and (price_diff_per<=50):
				self.PRICE_CONF4.append(True)
			else:
				self.PRICE_CONF4.append(False)


	def main(self):
		'''
		Class instance entry
		'''
		self.cpi_conf_df = pd.read_csv(self.input_file_path,
									   sep='\t',
									   encoding='ISO-8859-1')

		self.cpi_conf_df = self.cpi_conf_df[self.cpi_conf_df['s_image_url'].notnull()]
		column_list = ['sys_index','s_sku','s_product_url','s_price','SERP_URL','SERP_KEY','r_product_url','r_price']

		self.cpi_conf_df = self.cpi_conf_df[column_list]
		self.cpi_conf_df.apply(self.process, axis=1)

		self.cpi_conf_df['price_diff_per_sys'] = self.PRICE_DIFF_LIST
		self.cpi_conf_df['s_vs_r_price_conf(0)'] = self.PRICE_CONF1
		# self.cpi_conf_df['s_vs_r_price_conf(0-10)'] = self.PRICE_CONF2
		self.cpi_conf_df['s_vs_r_price_conf(0-50)'] = self.PRICE_CONF4
		# self.cpi_conf_df['s_vs_r_price_conf(10-65)'] = self.PRICE_CONF3
		
		self.cpi_conf_df.to_csv(self.output_file_path,
								index=False,
								sep='\t',
								encoding='iso-8859-1')