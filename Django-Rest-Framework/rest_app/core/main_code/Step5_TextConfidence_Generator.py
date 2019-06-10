import pandas as pd
import os
import re
from nltk.stem.porter import PorterStemmer

class TextConfidenceGenerator(object):

	def __init__(self,input_file_path, output_file_path):
		self.input_file_path = input_file_path
		self.output_file_path = output_file_path
		self.l2_1_list = []
		self.l4_1_list = []
		self.l5_1_list = []
		self.l6_1_list = []
		self.l2_2_list = []
		self.l4_2_list = []
		self.l5_2_list = []
		self.l6_2_list = []
		self.l7_list = []
		self.title_match_list = []  # added, checking s_itemname in r_title

		# Added For UI
		self.mpn_check_list = []
		self.upc_check_list = []
		self.asin_check_list = []
		self.gtin_check_list = []

		self.text_confidence_score = []

		self.stemmer = PorterStemmer()


	def check_field_contains(self,superset, subset):
		try:
			if type(superset) == float or type(subset) == float:
				return 0
			elif superset == '' or subset=='':
				return 0
			elif (str(superset).lower().find(str(subset).lower()) == -1)&(str(subset).lower().find(str(superset).lower()) == -1):
				return 0
			else:
				return 1
		except:
			return 0
    
	def check_field_variants(self,superset, variant_info):
		try:
			if (type(variant_info)==float) or variant_info=='':
				return 0
			subsetlist = re.split(r"\s*\^\s*", variant_info)
			agg_score = 0
			for x in subsetlist:
				agg_score = agg_score + self.check_field_contains(superset, str(x))
			return agg_score
		except:
			return 0 

	def check_category_in_field(self,superset, category):
		if (type(superset) == float or superset =='') or (type(category) == float or category==''):
			return 0

		categories = category.split('>')
		superset = superset.lower()

		if (type(superset) == float) or (type(categories) == float):
			return 0
		conf = 0
		for cat in categories:
			stemmed_cat = self.stemmer.stem(cat)
			
			if (stemmed_cat in superset) or (superset in cat.lower()):
				conf = 1
		return conf


	def check_field_in_another_field(self,superset, field):
		if (type(superset) == float or superset =='') or (type(field) == float or field=='') :
			return 0
		field = field.lower()
		stemmed_field = self.stemmer.stem(field)
		superset = superset.lower()
		if stemmed_field in superset:
			return 1
		else:
			field_subset = field.split()
			field_subset_match_count = 0
			for part in field_subset:
				if (part in superset) or (self.stemmer.stem(part) in superset):
					field_subset_match_count += 1
			field_in_another_field_weight = field_subset_match_count/len(field_subset)
			field_in_another_field_weight = "%.4f" % field_in_another_field_weight
			return (float(field_in_another_field_weight))


	def check_unique_identifier_match(self, search_id, result_id):
		search_id = str(search_id)
		result_id = str(result_id)

		if (type(search_id) == float or search_id =='' ) or (type(result_id) == float or result_id==''):
			return 0
		elif search_id in result_id or result_id in search_id:			# handles cases of multiple asin/upc/mpn/gtin
			return 1	
		else:
			return 0


	def process(self,row):
		product_sku = row['s_sku']

		l2_1 = self.check_category_in_field(row['r_item_name'], row['s_category'])
		self.l2_1_list.append(l2_1)
		l4_1 = self.check_field_variants(row['r_item_name'], row['s_variant_info'])
		self.l4_1_list.append(l4_1)
		l5_1 = self.check_field_in_another_field(row['r_item_name'], row['s_manufacturer'])
		self.l5_1_list.append(l5_1)
		l6_1 = self.check_field_contains(row['r_item_name'], row['s_mpn'])
		self.l6_1_list.append(l6_1)

		l2_2 = self.check_category_in_field(row['r_description'], row['s_category'])
		self.l2_2_list.append(l2_2)
		l4_2 = self.check_field_variants(row['r_description'], row['s_variant_info'])
		self.l4_2_list.append(l4_2)
		l5_2 = self.check_field_in_another_field(row['r_description'], row['s_manufacturer'])
		self.l5_2_list.append(l5_2)
		l6_2 = self.check_field_contains(row['r_description'], row['s_mpn'])
		self.l6_2_list.append(l6_2)
		l7 = self.check_field_contains(row['r_description'], row['s_item_name'])
		self.l7_list.append(l7)

		title_match = self.check_field_in_another_field(row['r_item_name'], row['s_item_name'])
		self.title_match_list.append(title_match)


		# additional checks
		mpn_check = self.check_unique_identifier_match(row['s_mpn'], row['r_mpn'])
		upc_check = self.check_unique_identifier_match(row['s_upc'], row['r_upc'])
		asin_check = self.check_unique_identifier_match(row['s_asin'], row['r_asin'])
		gtin_check = self.check_unique_identifier_match(row['s_gtin'], row['r_gtin'])

		self.mpn_check_list.append(mpn_check)
		self.upc_check_list.append(upc_check)
		self.asin_check_list.append(asin_check)
		self.gtin_check_list.append(gtin_check)

		total_row_confidence = l2_1 + l4_1 + l5_1 + l6_1 + l2_2 + l4_2 + l5_2 + l6_2 + l7 + title_match + mpn_check + upc_check + gtin_check + asin_check

		# total_row_confidence = l2_1 + l4_1 + l5_1 + l6_1 +  title_match
		self.text_confidence_score.append(total_row_confidence)


	def main(self):
		self.cpi_conf_df = pd.read_csv(self.input_file_path, sep='\t', encoding='ISO-8859-1', dtype=object)
		# self.cpi_conf_df.rename(columns={'s_image': 's_image_url', 's_link': 's_product_url','URL':'search_url', 's_title':'s_item_name'}, inplace=True)
		self.input_file_column_list = self.cpi_conf_df.columns.tolist()
		self.cpi_conf_df = self.cpi_conf_df.fillna(value='')
		search_columns = ['s_mpn','s_upc','s_asin','s_gtin','s_variant_info','s_manufacturer','s_category','s_description']
		result_columns = ['r_mpn','r_upc','r_asin','r_gtin','r_variant_info','r_manufacturer','r_category','r_description']

		for col in search_columns + result_columns:
			# adding missing columns
			if col not in self.input_file_column_list:
				self.cpi_conf_df[col] = ''

		self.cpi_conf_df.apply(self.process, axis=1)
		column_list = ['sys_index','s_sku','s_product_url','s_item_name','s_category','s_description','s_variant_info','s_manufacturer','s_mpn'\
						,'s_upc','s_asin','s_gtin','SERP_URL','SERP_KEY',\
						'r_product_url','r_item_name','r_description','r_mpn','r_upc','r_asin','r_gtin','r_variant_info','r_manufacturer','r_category']

		self.cpi_conf_df = self.cpi_conf_df[column_list]
		self.cpi_conf_df['s_vs_r_text_confidence_matrix'] = self.text_confidence_score

		# self.cpi_conf_df['s_category_in_r_title'] = self.l2_1_list
		# self.cpi_conf_df['s_variant_info_in_r_title'] = self.l4_1_list
		# self.cpi_conf_df['s_manufacturer_in_r_title'] = self.l5_1_list
		# self.cpi_conf_df['s_mpn_in_r_title'] = self.l6_1_list

		self.cpi_conf_df['mpn_match'] = self.mpn_check_list
		self.cpi_conf_df['upc_match'] = self.upc_check_list
		self.cpi_conf_df['asin_match'] = self.asin_check_list
		self.cpi_conf_df['gtin_match'] = self.gtin_check_list

		self.cpi_conf_df['title_match'] = self.title_match_list
		self.cpi_conf_df.to_csv(self.output_file_path, index=False, sep='\t',encoding='iso-8859-1')

