from django.conf import settings

## for local

# CONFIDENCE_MATRIX_MAPPING_TYPE={
# 	settings.ES_COMPUTED_RESULT_INDEX:{
# 		"properties":{
# 		"s_vs_r_image_match":{
# 			"type":"float"	
# 		},
# 		"title_match":{
# 			"type":"float"	
# 		},
# 		"price_diff_per_sys":{
# 			"type":"float"	
# 		},
# 		"confidence_score":{
# 			"type":"float"
# 		},
# 		"mpn_match":{
# 			"type":"integer"
# 		},
# 		"gtin_match":{
# 			"type":"integer"
# 		},
# 		"asin_match":{
# 			"type":"integer"
# 		},
# 		"upc_match":{
# 			"type":"integer"
# 		},
# 		"human_verdict":{
# 			"type":"integer",
# 			"index":"not_analyzed"
# 		},
# 		"Result":{
# 			"type":"string",
# 			"index":"not_analyzed"
# 		}
# 		}
# 	}
# }

# for updated Elasticsearch
CONFIDENCE_MATRIX_MAPPING_TYPE={
	settings.ES_COMPUTED_RESULT_INDEX:{
		"properties":{
		"s_vs_r_image_match":{
			"type":"float"	
		},
		"title_match":{
			"type":"float"	
		},
		"price_diff_per_sys":{
			"type":"keyword"
			# "index":"false"
		},
		"confidence_score":{
			"type":"float"
		},
		"mpn_match":{
			"type":"integer"
		},
		"gtin_match":{
			"type":"integer"
		},
		"asin_match":{
			"type":"integer"
		},
		"upc_match":{
			"type":"integer"
		},
		"human_verdict":{
			"type":"keyword"
			# "index":"false"
		},
		"Result":{
			"type":"keyword"
			# "index":"false"
		},
		"request_id":{"type":"text"},
		"sys_index":{"type":"text"},
		
		# additional field for term search and sorting


		# "s_sku":{
		# 			"type":"text",
		# 			"fields": {
		# 						"keyword":{
		# 								"type":"keyword"
		# 								}
		# 						}
		# 		},
		"s_sku":{
			"type":"text",
			"fields": {
						"keyword":{
								"type":"text",
								"analyzer":"analyzer_case_insensitive"
								}
						}
		},

		"s_item_name":{
					"type":"text",
					"fields": {
								"keyword":{
										"type":"text",
										"analyzer":"analyzer_case_insensitive"
										}
								}
				},

		"s_price":{"type":"text"},
		"s_mpn":{"type":"text"},
		"s_upc":{"type":"text"},
		"s_asin":{"type":"text"},
		"s_gtin":{"type":"text"},
		"s_variant_info":{"type":"text"},
		"s_image_url":{"type":"text"},
		"s_product_url":{"type":"text"},
		"s_brand":{"type":"text"},
		"s_category":{"type":"text"},
		"s_description":{"type":"text"},
		"SERP_KEY":{"type":"text"},
		"SERP_URL":{"type":"text"},
		"r_item_name":{"type":"text"},
		"r_price":{"type":"text"},
		"r_mpn":{"type":"text"},
		"r_upc":{"type":"text"},
		"r_asin":{"type":"text"},
		"r_gtin":{"type":"text"},
		"r_variant_info":{"type":"text"},
		"r_image_url":{"type":"text"},
		"r_image_url_main":{"type":"text"},
		"r_product_url":{"type":"text"},
		"r_brand":{"type":"text"},
		"r_category":{"type":"text"},
		"r_description":{"type":"text"},
		"AdminEdit":{"type":"text"},
		"confusion":{"type":"text"},
		"user":{"type":"text"},
		"Group":{"type":"keyword"}
		}
	}
}