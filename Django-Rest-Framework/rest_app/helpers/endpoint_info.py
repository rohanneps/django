# from project.models import Project
from django.conf import settings

status_options = [i[0] for i in settings.PROJECT_STATUS_LIST]

ENDPOINT_DICT ={
	'/project/all':{
		'objective': 'Returns all the project details',
		'methods_allowed': '["GET"]',
		'required-fields': None,
	},
	'project/project/_id_':{
		'objective': 'Retrieval and Deletion operation on project.',
		'methods_allowed': '["GET","DELETE"]',
		'required-fields': '["id"]',
	},
	'project/createproject':{
		'objective': 'Initiates a project',
		'methods_allowed': '["POST"]',
		'required-fields': '["client_name","file_name"]',
		'returns':'Created Project Information.',
	},
	'project/startproject':{
		'objective': 'Starts an initiated project',
		'methods_allowed': '["PUT"]',
		'required-fields': '["id"]',
		'returns':'Whether project has been started or not.',
	},
	'project/updatehumanverification':{
		'objective': 'Initiates/Completed human verification process',
		'methods_allowed': '["PUT"]',
		'required-fields': '["id"]',
		'returns':'Whether project human verification has been started or not/ completed or not.',
	},
	'project/getinprogressproject':{
		'objective': 'Returns all the project which are currently in progress',
		'methods_allowed': '["GET"]',
		'required-fields': None,
	},
	'search/searchprojectsbyclient':{
		'objective': 'Search Project By Client Name',
		'methods_allowed': '["POST"]',
		'required-fields': '["client_name"]',
		'returns':'Project List matching client name',
	},
	'search/searchprojectsbydate':{
		'objective': 'Search Project By Date Range',
		'methods_allowed': '["POST"]',
		'required-fields': '["from_date","to_date"] of the format (MM/DD/YYYY)',
		'returns':'Project List within date range',
	},
	'search/searchprojectsbystatus':{
		'objective': 'Search Project By status',
		'methods_allowed': '["POST"]',
		'required-fields': '["status"]',
		'returns':'Project List with the status provided',
		'status_options': status_options
	},
	'search/searchprojectsbyclientdatestatus':{
		'objective': 'Search Project By status',
		'methods_allowed': '["POST"]',
		'optional-fields': '["status","client_name","from_date","to_date"]',
		'returns':'Project List with the filters provided',
		'status_options': status_options
	},
	'search/searchprojectdetailedreport':{
		'objective': 'Get Detailed Report of a project',
		'methods_allowed': '["POST"]',
		'required-fields': '["id"]',
		'returns':'Detailed report of a given project id',
	},

	'project/terminateinprogressproject':{
		'objective': 'Terminates an inprogress project',
		'methods_allowed': '["POST"]',
		'required-fields': '["id"]',
		'returns':'True/False',
	},
	'project/getprojectmatchnotmatchcount':{
		'objective': 'Returns number of matched and Non-matched combination',
		'methods_allowed': '["GET"]',
		'required-fields': '["id"]',
		'returns':'Match count and NonMatch count',
	},
	'client/all':{
		'objective': 'Returns all the distinct client names',
		'methods_allowed': '["GET"]',
		'required-fields': None,
	},
	'download/initiatematchdownload/_id_':{
		'objective': 'Initiates Downloadable File with Human Verdict Match',
		'methods_allowed': '["GET"]',
		'required-fields': '["id"]',
	},
	'project/idall':{
		'objective': 'Returns all the project ids in insertion order',
		'methods_allowed': '["GET"]',
		'required-fields': None,
	},
}