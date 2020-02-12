import os
from helper import (
					get_current_date,
					get_current_est_time,
					convert_s3_to_email_format
					)
from decouple import config

PLATFORM = 'Google'
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
# S3_REGION = 'us-east-1'
S3_REGION_LIST = ['us-east-1','us-east-2','us-west-1','us-west-2']
S3_BUCKET_DICT = {
					'us-east-1' : 'us-east-1-google-serp',
					'us-east-2' : 'us-east-2-google-serp',
					'us-west-1' : 'us-west-1-google-serp',
					'us-west-2' : 'us-west-2-google-serp'
				  }

S3_PREFIX_PC = 'rnd_region_prospect_google_pla_showcase'
S3_PREFIX_MOBILE = 'rnd_region_prospect_google_pla_showcase_mobile'
########################################################################################


SERVER = config('SERVER', cast=bool)

OUTPUT_ROOT_DIR = 'output'
OUTPUT_DATE_DIR = os.path.join(OUTPUT_ROOT_DIR, '{}', CURRENT_DATE_STAMP)


BATCH_OUTPUT_DIR_PC = os.path.join(OUTPUT_DATE_DIR,'Desktop')


BATCH_OUTPUT_DIR_MOBILE = os.path.join(OUTPUT_DATE_DIR,'Mobile')

DESTINATION_ROOT_PATH = os.path.join('final_outputs','{}')

SHOWCASE_COLUMNS = ['Search Region','Search Datetime','PLA Rank','PLA Store']

### OUTPUT OF STEP 6 ##################################
MERGED_OUTPUT_PATH = os.path.join(OUTPUT_DATE_DIR,'PLA_Showcase_pc_mobile_allregion.tsv')
########################################################################################

### AWS CREDENTIALS ###################################################################
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
########################################################################################

### ACLK REDIRECT #####################################
SELENIUM_WEBDRIVER_PATH = './bin/chromedriver'
SELENIUM_HEADLESS_CHROMIUM_PATH = '/bin/headless-chromium'
PAGE_TIMEOUT = 20											# N seconds page timeout for aclk redirect

SHOWCASE_FILE_PRODUCT_URL_HEADER = 'PLA URL'

# ACLK_REDIRECT_MASTER_FILE = os.path.join('aclk_redirect_master','Aclk_url_redirected_master.tsv')
# ACLK_REDIRECT_HISTORY_FILE = os.path.join(OUTPUT_DATE_DIR, 'SponsoredResult_Combined_allregion_Redirected_hist.tsv')

NUM_OF_ACLK_REDIRECT_THREADS = 8

# Step 7a files
ACLK_REDIRECT_HTTP_OUTPUT_FILE = os.path.join(OUTPUT_DATE_DIR, 'SponsoredResult_Combined_allregion_Redirected_http.tsv')
ACLK_REDIRECT_LISTING_HTTP_FILE = os.path.join(OUTPUT_DATE_DIR,'Aclk_RedirectList_req.tsv')
# Step 7b files
ACLK_REDIRECT_LISTING_SEL_FILE = os.path.join(OUTPUT_DATE_DIR,'Aclk_RedirectList_sel.tsv')
ADS_COMPUTED_OUTPUT_FILE = 'SponsoredResults_combined__{}.tsv'.format(EMAIL_TIME_FORMAT)
ADS_COMPUTED_OUTPUT_FILE_PATH = os.path.join(OUTPUT_DATE_DIR, ADS_COMPUTED_OUTPUT_FILE)

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
GOOGLE_RUN_DETAILS_TABLE = config('GOOGLE_RUN_DETAILS_TABLE')
AMAZON_RUN_DETAILS_TABLE = config('AMAZON_RUN_DETAILS_TABLE')
SHOWCASE_TABLE_NAME = config('DB_SHOWCASE_TABLE_NAME')
SPONSORED_TABLE_NAME = config('DB_SPONSORED_TABLE_NAME')
#########################################################################################