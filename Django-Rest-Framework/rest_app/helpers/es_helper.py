from django.conf import settings
from elasticsearch import helpers
import csv
import json
import logging
import requests
from . import mapping_info
from . import index_settings_info

comp_logger = logging.getLogger(__name__)

def insert_records_into_elasticsearch_index(index, file_location):
	"""
	Bulk insert into csv

	"""
	f = open(file_location,'r')
	reader = csv.DictReader(f, delimiter='\t')
	resp = helpers.bulk(settings.ES, 
						reader,
						index=index,
						doc_type=index)

	total_rows_inserted = resp[0]
	if total_rows_inserted>0:
		comp_logger.info('Bulk inserted {} rows for file {}'.format(total_rows_inserted, file_location))
	else:
		comp_logger.info('Bulk inserted failure for file {}'.format(total_rows_inserted, file_location))





def create_index(index):
	# headers = {'content-type':'application/json'}
	# resp = requests.put('http://{}:{}/{}/'.format(settings.ES_HOST, settings.ES_PORT, index),headers=headers)
	create_index_settings(index)

def create_index_settings(index):
	"""
	Settings creation info for index
	"""
	headers = {'content-type':'application/json'}
	index_settings = index_settings_info.CONFIDENCE_MATRIX_SETTINGS

	resp = requests.put('http://{}:{}/{}/'.format(settings.ES_HOST,
												  settings.ES_PORT,
												  index),
		   				data=json.dumps(index_settings),
		   				headers=headers)

	if resp.status_code == 200:
		comp_logger.info('Settings created successfully for index: {}'.format(index))
	else:
		comp_logger.info('Settings creation failed for index: {}'.format(index))
		comp_logger.info(resp.content)
		


def create_index_mapping(index):
	"""
	Mapping creation info for index
	"""
	headers = {'content-type':'application/json'}
	mapping = mapping_info.CONFIDENCE_MATRIX_MAPPING_TYPE
	mapping_type = list(mapping.keys())[0]
	r = requests.post('http://{}:{}/{}/_mapping/{}/'.format(settings.ES_HOST, 
															settings.ES_PORT, 
															index,
															mapping_type),
					 	data=json.dumps(mapping), 
					 	headers=headers)
	
	if r.status_code == 200:
		comp_logger.info('Mapping created successfully for index: {}'.format(index))
		
	else:
		comp_logger.info('Mapping creation failed for index: {}'.format(index))
		comp_logger.info(r.content)
