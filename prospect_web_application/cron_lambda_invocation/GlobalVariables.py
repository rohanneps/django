import os
from decouple import config

### Root location ##############################################
BASE_DIR = os.getcwd()
################################################################

KEYWORD_COLUMN = 'Search Keyword'

MAX_PROSPECT_CRON_JOB_LIFE_TYPE = 3
MAX_PROSPECT_RUN_COUNT = 84

AWS_REGION_LIST = ['us-east-1','us-east-2','us-west-1','us-west-2']

AWS_LAMBDA_REQUEST_WAIT_TIME = 2
### AWS CREDENTIALS #####################################################################
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
#########################################################################################


### Web Application ROOT DIR ############################################################
WEB_APP_ROOT_DIR = ''
MEDIA_ROOT = os.path.join(WEB_APP_ROOT_DIR, 'media')
KEYWORD_COLUMN = 'Search Keyword'
#########################################################################################
### POSTGRES DB DETAILS #################################################################
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_NAME = config('DB_NAME')
PROSPECT_TABLE = config('PROSPECT_TABLE')
GOOGLE_RUN_DETAILS_TABLE = config('GOOGLE_RUN_DETAILS_TABLE')
AMAZON_RUN_DETAILS_TABLE = config('AMAZON_RUN_DETAILS_TABLE')
#########################################################################################