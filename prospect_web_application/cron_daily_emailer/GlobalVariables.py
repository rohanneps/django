import os
from helper import (
					get_current_date,
					get_current_est_time,
					convert_s3_to_email_format
					)
from decouple import config

### Root location ##############################################
BASE_DIR = os.getcwd()
################################################################

### TIME SETTINGS #####################################################################
DATE_TIME_DELIM = '__'
CURRENT_DATE_STAMP = get_current_date()						# returns GMT time
CURRENT_EST_TIME = get_current_est_time(CURRENT_DATE_STAMP)	# returns EST time
########################################################################################



### EMAIL DETAILS ######################################################################
EMAIL_SUBJECT_TEMPLATE = 'GrowByData - {} PLA - Sponsored Data Processing for Prospect {} has Completed ({}).'
EMAIL_HEADER_TEMPLATE = '{} - {} SERP - Sponsored Data Processing for Prospect {} has Completed.'
# EMAIL_BODY_TEMPLATE = 'The computed file is uploaded to location: <strong>{}</strong/>.<br/>The computed file size: <strong>{}</strong>.<br/>Total PLA records: <strong>{}</strong>.<br/>Total Showcase records: <strong>{}</strong>.'
GOOGLE_EMAIL_TABLE_STRING = '''<table cellspacing="10">
<thead class="thead-dark">
<tr>
<th scope="col">Run Id</th>
<th scope="col">Run datetime</th>
<th scope="col">Platform</th>
<th scope="col">File Size</th>
<th scope="col">Total PLA</th>
<th scope="col">Total Showcase</th>
</tr></thead><tbody>{}<tbody></table>'''

GOOGLE_EMAIL_TABLE_ROW_STRING = '''<tr>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
</tr>'''

AMAZON_EMAIL_TABLE_STRING = '''<table cellspacing="10">
<thead class="thead-dark">
<tr>
<th scope="col">Run Id</th>
<th scope="col">Run datetime</th>
<th scope="col">Platform</th>
<th scope="col">Amazon Choices</th>
<th scope="col">Brands Related</th>
<th scope="col">Editorial Recommendations</th>
<th scope="col">Organic</th>
<th scope="col">Sponsored</th>
<th scope="col">Today Deals</th>
</tr></thead><tbody>{}<tbody></table>'''

AMAZON_EMAIL_TABLE_ROW_STRING = '''<tr>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
</tr>'''

########################################################################################


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
