from project.models import Project
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from django.conf import settings
from wsgiref.util import FileWrapper
from rest_framework.reverse import reverse
import mimetypes
from django.http import HttpResponse
from pandasticsearch import Select

from helpers import helper
import os
import pandas as pd
import logging
comp_logger = logging.getLogger(__name__)



class InitiateESHumanVeriedMatchedResultSetDownloader(APIView):
	"""
	Prepare human verified matched resultset for a project
	returns: download link
	"""
	HUMAN_VERIFICATION_MATCH_REQUEST_BODY = {	
												"_source": settings.DOWNLOAD_HEADERS,
												"query":{
															"bool":{
																"filter":{
																		"bool":{
																		"must":[
																					{"term":{"request_id":None}},
																					{"term":{"human_verdict.keyword":"Match"}}
																		]
											}}}}}
	def get_object(self, project_id):
		try:
			return Project.objects.get(pk=project_id)
		except Project.DoesNotExist:
			raise Http404

	def set_request_body_project_id(self,project_id):
		self.HUMAN_VERIFICATION_MATCH_REQUEST_BODY['query']['bool']['filter']['bool']['must'][0]['term']['request_id'] = project_id

	def get(self, request, project_id, format=None):
		comp_logger.info("Initiating file downloader for id: {}".format(project_id))
		project = self.get_object(project_id)
		if project.status =='H_Completed':
			comp_logger.info("Project with id: {} is H_Completed, creating downloadable file".format(project_id))

			# set project_id for the request body
			self.set_request_body_project_id(project_id)
			self.generate_downloadable_file(project, project_id)
			return Response({'status':True, 'download_link': reverse('download:file_download', kwargs={'project_id':project_id}, request=request)})
		else:
			comp_logger.info("Project with id: {} is not H_Completed, cannot create downloadable file".format(project_id))
			return Response({'status':False, 'response':'Project is not H_Completed'})

	def generate_downloadable_file(self, project, project_id):
		# project_download_dir = os.path.join(settings.PROJECT_DIR,str(project_id),settings.PROJECT_DOWNLOAD_FOLDER)
		# helper.create_dir(project_download_dir)
		project_download_dir = settings.PROJECT_DOWNLOAD_FOLDER
		project_download_file_path = os.path.join(project_download_dir,settings.PROJECT_DOWNLOAD_FILE.format(project_id))

		# generate ES resultset for the given project id
		self.generate_es_resultset_file(request_id=project_id,output_file=project_download_file_path)

	
	def generate_es_resultset_file(self,request_id,output_file):
		initial_result_set = settings.ES.search(index=settings.ES_COMPUTED_RESULT_INDEX, body=self.HUMAN_VERIFICATION_MATCH_REQUEST_BODY)  # to get size parameter
		resultset_size = initial_result_set['hits']['total']
		self.HUMAN_VERIFICATION_MATCH_REQUEST_BODY['size'] = resultset_size
		result_set = settings.ES.search(index=settings.ES_COMPUTED_RESULT_INDEX, body=self.HUMAN_VERIFICATION_MATCH_REQUEST_BODY)
		downloadable_df = Select.from_dict(result_set).to_pandas()

		try:
			comp_logger.info("Generating dataframe from ES resultset for id: {}".format(request_id))
			downloadable_df = downloadable_df[settings.DOWNLOAD_HEADERS]
		except:
			# if there is no human verdict match\
			comp_logger.info("ES resultset empty for human_verdict match for id: {} is empty".format(request_id))
			downloadable_df = pd.DataFrame(columns=settings.DOWNLOAD_HEADERS)

		if not os.path.exists(output_file):
			comp_logger.info("ES human_verdict match resultset initiated for id: {}".format(request_id))
			downloadable_df.to_csv(output_file, sep='\t', index=False, encoding='iso-8859-1')
		else:
			comp_logger.info("ES human_verdict match resultset already generated for id: {}".format(request_id))



def file_download(requests,project_id):
	"""
	File Download View Handler
	"""
	comp_logger.info("Initiating human verification match resultset file download for id: {}".format(project_id))

	try:
		# project_download_dir = os.path.join(settings.PROJECT_DIR,str(project_id),settings.PROJECT_DOWNLOAD_FOLDER)
		# project_download_file_path = os.path.join(project_download_dir,settings.PROJECT_DOWNLOAD_FILE.format(project_id))

		project_download_dir = settings.PROJECT_DOWNLOAD_FOLDER
		project_download_file_path = os.path.join(project_download_dir,settings.PROJECT_DOWNLOAD_FILE.format(project_id))

		
		file_name = settings.PROJECT_DOWNLOAD_FILE.format(project_id)
		file_path = project_download_file_path

		
		file_wrapper = FileWrapper(open(file_path,'rb'))
		file_mimetype = mimetypes.guess_type(file_path)
		response = HttpResponse(file_wrapper, content_type=file_mimetype )
		response['X-Sendfile'] = file_path
		response['Content-Length'] = os.stat(file_path).st_size
		response['Content-Disposition'] = 'attachment; filename=%s' % (file_name) 
		comp_logger.info("Completed human verification match resultset file download for id: {}".format(project_id))
		return response

	# For file not found cases
	except:
		comp_logger.info("Human verification match resultset file download failed for id: {}".format(project_id))
		return HttpResponse("{'status':False,'response':'cannot download file'}")
		