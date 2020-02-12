import os
from helper import (
					get_current_date,
					get_current_est_time,
					convert_s3_to_email_format
					)
from decouple import config

PLATFORM = 'Amazon'
### Root location ##############################################
BASE_DIR = os.getcwd()
################################################################

### TIME SETTINGS #####################################################################
DATE_TIME_DELIM = '__'
CURRENT_DATE_STAMP = get_current_date()						# returns GMT time
CURRENT_EST_TIME = get_current_est_time(CURRENT_DATE_STAMP)	# returns EST time
EMAIL_TIME_FORMAT = convert_s3_to_email_format(CURRENT_EST_TIME)
########################################################################################

### S3 Location Settings ##############################################
# Single Region for Amazon plotform
S3_REGION_LIST = ['us-east-1']
S3_BUCKET_DICT = {
					'us-east-1' : 'us-east-1-google-serp',
					'us-east-2' : 'us-east-2-google-serp',
					'us-west-1' : 'us-west-1-google-serp',
					'us-west-2' : 'us-west-2-google-serp'
				  }

S3_PREFIX_PC = 'rnd_region_amazon_scrape_details'
########################################################################################


SERVER = config('SERVER', cast=bool)

OUTPUT_ROOT_DIR = 'output'
OUTPUT_DATE_DIR = os.path.join(OUTPUT_ROOT_DIR, '{}', CURRENT_DATE_STAMP)


BATCH_OUTPUT_DIR_PC = os.path.join(OUTPUT_DATE_DIR,'Desktop')


DESTINATION_ROOT_PATH = os.path.join('final_outputs','{}')



### AWS CREDENTIALS ###################################################################
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
########################################################################################

### Web Application ROOT DIR ############################################################
WEB_APP_ROOT_DIR = ''
WEB_APP_MEDIA_ROOT = os.path.join(WEB_APP_ROOT_DIR, 'media')

#########################################################################################

## Mandatory File input fields##########################################################
MANDATORY_COLUMN_HEADERS = ['Advertiser URL','Keyword Category','Keyword SubCategory','Search Keyword','Is Branded']
########################################################################################

### TOP N RANK FILTER ##################################################################
TOP_N_RANK = 5
########################################################################################


### LOGGING DETAILS #####################################################################
LOG_DIR = 'logs'
LOG_FILE = 'cron.log'
#########################################################################################

#########################################################################################
### POSTGRES DB DETAILS #################################################################
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_NAME = config('DB_NAME')
PROSPECT_TABLE = config('PROSPECT_TABLE')
AMAZON_RUN_DETAILS_TABLE = config('AMAZON_RUN_DETAILS_TABLE')
GOOGLE_RUN_DETAILS_TABLE = config('GOOGLE_RUN_DETAILS_TABLE')

RELATED_BRAND_TABLE_NAME = config('DB_RELATED_BRAND_TABLE_NAME')
SPONSORED_TABLE_NAME = config('DB_SPONSORED_TABLE_NAME')
AMAZON_CHOICE_TABLE_NAME = config('DB_AMAZON_CHOICE_TABLE_NAME')
DB_TODAY_DEALS_TABLE_NAME = config('DB_TODAY_DEALS_TABLE_NAME')
EDITORIAL_RECOMMENDATION_TABLE_NAME = config('DB_EDITORIAL_RECOMMENDATION_TABLE_NAME')
ORGANIC_TABLE_NAME = config('DB_ORGANIC_TABLE_NAME')
#########################################################################################