from project.models import Project, ProjectStatus
from serializers.project_serializers import (
		ProjectDetailSerializer,
		ProjectStartSerializer,
		FindProjectByClientSerializer,
		FindProjectByDateSerializer,
		FindProjectByStatusSerializer,
		FindProjectByClientDateStatusSerializer
	)

from django.conf import settings
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from helpers import helper
import logging
from rest_framework.parsers import JSONParser
from django.db.models import Q
from custom_views.CustomAPIView import CustomAPIPaginatorView


comp_logger = logging.getLogger(__name__)


class SearchProjectsByClient(CustomAPIPaginatorView):
	"""
	Find Project by client
	"""
	'''
	The CustomAPIPaginatorView handles the boilerplate code for handling LimitOffsetPagination for this class-based view.
	'''
	
	def get_queryset(self):
		project_client_lookup = Q(client_name__icontains=self.client_name)
		projects = Project.objects.filter(project_client_lookup).order_by('-id')
		return projects

	''' The post method is used to handle search request'''
	def post(self, request, *args, **kwargs):
		comp_logger.info('Call to SearchProjectsByClient')
		serializer = FindProjectByClientSerializer(data=request.data)
		if serializer.is_valid():
			self.client_name = serializer.data['client_name']
			comp_logger.info('Call to SearchProjectsByClient with query: {}'.format(self.client_name))
			request_field_list = serializer.data.keys()
			projects = self.get_queryset()								# get object instances matching the post request
			project_count = helper.get_total_project_count(projects)
			
			if project_count>0:

				# no need for pagination
				if 'all' in request_field_list:
					serializer = ProjectDetailSerializer(projects, many=True)
					return Response({'results':serializer.data,'count':project_count})

				# handling of LimitOffsetPagination
				else:
					result_set = self.paginate_queryset(projects)
					if result_set is not None:
						serializer = ProjectDetailSerializer(result_set, many=True)
						return self.get_paginated_response(serializer.data)
			else:
				return Response({'results':[],'count':0})

		else:
			comp_logger.info('{} is not valid'.format(request.data))
			comp_logger.info(serializer.errors)
			return Response({'response':serializer.errors})



# @api_view(['POST'])
# @renderer_classes((JSONRenderer,))
# def find_projects_by_client(request):
# 	"""
# 	Returns project list by client name
# 	"""
# 	if request.method == 'POST':
# 		comp_logger.info('Call to find_projects_by_client')
# 		data = JSONParser().parse(request)
# 		serializer = FindProjectByClientSerializer(data=data)

# 		if serializer.is_valid():
# 			client_name = serializer.data['client_name']
# 			project_client_lookup = Q(client_name__icontains=client_name)
# 			comp_logger.info('Call to find_projects_by_client with query: {}'.format(client_name))
# 			projects = Project.objects.filter(project_client_lookup).order_by('-id')
# 			project_count = helper.get_total_project_count(projects)

# 			if project_count>0:
# 				paginator = LimitOffsetPagination()
# 				paginated_response = paginator.paginate_queryset(projects, request)
# 				serializer = ProjectDetailSerializer(paginated_response, many=True)
# 				print(paginated_response)
# 				# serializer = ProjectDetailSerializer(projects, many=True)
# 				# return Response({'response':serializer.data,'total_hits':project_count})
# 				return paginator.paginate_queryset(projects,request)
# 			else:
# 				return Response({'response':[],'total_hits':0})

# 		else:
# 			comp_logger.info('{} is not valid'.format(data))
# 			comp_logger.info(serializer.errors)
# 			return Response({'response':serializer.errors})
# 	return Response({})


class SearchProjectsByDate(CustomAPIPaginatorView):
	"""
	Find Project by data range
	"""

	def get_queryset(self):
		projects = Project.objects.filter(start_date__gte=self.from_date).filter(start_date__lte=self.to_date).order_by('-id')
		return projects


	''' The post method is used to handle search request'''
	def post(self, request, *args, **kwargs):
		comp_logger.info('Call to SearchProjectsByDate')
		serializer = FindProjectByDateSerializer(data=request.data)

		if serializer.is_valid():
			from_date = serializer.data['from_date']
			to_date = serializer.data['to_date']
			comp_logger.info('Call to SearchProjectsByDate with range: {} and {}'.format(from_date, to_date))

			self.from_date, self.to_date = helper.get_from_date_to_date_format(from_date, to_date)

			# get project list by date range
			projects = self.get_queryset()
			project_count = helper.get_total_project_count(projects)

			if project_count>0:
				result_set = self.paginate_queryset(projects)
				if result_set is not None:
					serializer = ProjectDetailSerializer(result_set, many=True)
					return self.get_paginated_response(serializer.data)
			else:
				return Response({'results':[],'count':0})

		else:
			comp_logger.info('{} is not valid'.format(request.data))
			comp_logger.info(serializer.errors)
			return Response({'response':serializer.errors})



# @api_view(['POST'])
# @renderer_classes((JSONRenderer,))
# def find_projects_by_date(request):
# 	"""
# 	Find Project by data range
# 	"""
	
# 	if request.method == 'POST':
# 		comp_logger.info('Call to find_projects_by_date')
# 		data = JSONParser().parse(request)
# 		serializer = FindProjectByDateSerializer(data=data)

# 		if serializer.is_valid():
# 			from_date = serializer.data['from_date']
# 			to_date = serializer.data['to_date']
# 			comp_logger.info('Call to find_projects_by_date with range: {} and {}'.format(from_date, to_date))

# 			from_date, to_date = helper.get_from_date_to_date_format(from_date, to_date)

# 			# get project list by date range
# 			projects = Project.objects.filter(start_date__gte=from_date).filter(start_date__lte=to_date).order_by('-id')
# 			project_count = helper.get_total_project_count(projects)
# 			if project_count>0:
# 				serializer = ProjectDetailSerializer(projects, many=True)
# 				return Response({'response':serializer.data,'total_hits':project_count})
# 			else:
# 				return Response({'response':[],'total_hits':0})

# 		else:
# 			comp_logger.info('{} is not valid'.format(data))
# 			comp_logger.info(serializer.errors)
# 			return Response({'response':serializer.errors})
# 	return Response({})


class SearchProjectsByStatus(CustomAPIPaginatorView):
	"""
	Filter Project By Status
	"""
	def get_queryset(self):
		project_client_lookup = Q(status=self.status)
		projects = Project.objects.filter(project_client_lookup).order_by('-id')
		return projects

	''' The post method is used to handle search request'''
	def post(self, request, *args, **kwargs):
		comp_logger.info('Call to SearchProjectsByStatus')
		serializer = FindProjectByStatusSerializer(data=request.data)

		if serializer.is_valid():
			self.status = serializer.data['status']
			comp_logger.info('Call to find_projects_by_status with status: {}'.format(self.status))
			projects = self.get_queryset()
			project_count = helper.get_total_project_count(projects)
			if project_count>0:
				result_set = self.paginate_queryset(projects)
				if result_set is not None:
					serializer = ProjectDetailSerializer(result_set, many=True)
					return self.get_paginated_response(serializer.data)
			else:
				return Response({'results':[],'count':0})

		else:
			choices_list = [i[0] for i in settings.PROJECT_STATUS_LIST]
			comp_logger.info('{} is not valid'.format(request.data))
			comp_logger.info(serializer.errors)
			return Response({'response':serializer.errors,'status_options':choices_list})

# @api_view(['POST'])
# @renderer_classes((JSONRenderer,))
# def find_projects_by_status(request):
# 	"""
# 	Filter Project By Status
# 	"""
# 	if request.method == 'POST':
# 		comp_logger.info('Call to find_projects_by_status')
# 		data = JSONParser().parse(request)
# 		serializer = FindProjectByStatusSerializer(data=data)
# 		if serializer.is_valid():
# 			status = serializer.data['status']
# 			comp_logger.info('Call to find_projects_by_status with status: {}'.format(status))
# 			project_client_lookup = Q(status=status)
# 			projects = Project.objects.filter(project_client_lookup).order_by('-id')
# 			project_count = helper.get_total_project_count(projects)
# 			if project_count>0:
# 				serializer = ProjectDetailSerializer(projects, many=True)
# 				return Response({'response':serializer.data,'total_hits':project_count})
# 			else:
# 				return Response({'response':[],'total_hits':0})

# 		else:
# 			choices_list = [i[0] for i in settings.PROJECT_STATUS_LIST]
# 			comp_logger.info('{} is not valid'.format(data))
# 			comp_logger.info(serializer.errors)
# 			return Response({'response':serializer.errors,'status_options':choices_list})
# 	return Response({})
	

class SearchProjectsByClientDateStatus(CustomAPIPaginatorView):
	"""
	Filter Project By Status, Client And Date
	"""
	def get_queryset(self, serializer):
		status = serializer.data['status']
		if status!='All':
			status_query = Q(status=status)
			projects = Project.objects.filter(status_query)
		else:
			projects = Project.objects.all()
			

		request_field_list = serializer.data.keys()
		if 'client_name' in request_field_list:
			client_name = serializer.data['client_name']
			if client_name != '':
				project_client_lookup = Q(client_name__icontains=client_name)
				projects = projects.filter(project_client_lookup).distinct()

		if 'from_date' in request_field_list:
			from_date = serializer.data['from_date']
			if 'to_date' in request_field_list:
				to_date = serializer.data['to_date']
			else:
				to_date = helper.get_current_date()
			from_date, to_date = helper.get_from_date_to_date_format(from_date, to_date)
			if from_date != '' and to_date!='':
				projects = projects.filter(start_date__gte=from_date).filter(start_date__lte=to_date)
		return projects.order_by('-id')

	''' The post method is used to handle search request'''
	def post(self, request, *args, **kwargs):
		comp_logger.info('Call to SearchProjectsByClientDateStatus')
		serializer = FindProjectByClientDateStatusSerializer(data=request.data)

		if serializer.is_valid():
			comp_logger.info('Call to SearchProjectsByClientDateStatus with request: {}'.format(request.data))
			projects = self.get_queryset(serializer)
			project_count = helper.get_total_project_count(projects)
			if project_count>0:
				result_set = self.paginate_queryset(projects)
				if result_set is not None:
					serializer = ProjectDetailSerializer(result_set, many=True)
					return self.get_paginated_response(serializer.data)
			else:
				return Response({'results':[],'count':0})

		else:
			choices_list = [i[0] for i in settings.PROJECT_STATUS_LIST]
			comp_logger.info('{} is not valid'.format(request.data))
			comp_logger.info(serializer.errors)
			return Response({'response':serializer.errors,'status_options':choices_list})

# @api_view(['POST'])
# @renderer_classes((JSONRenderer,))
# def find_projects_by_client_date_status(request):
# 	"""
# 	Filter Project By Status, Client And Date
# 	"""
# 	if request.method == 'POST':
# 		comp_logger.info('Call to find_projects_by_client_date_status')
# 		data = JSONParser().parse(request)
# 		serializer = FindProjectByClientDateStatusSerializer(data=data)
# 		if serializer.is_valid():
# 			status = serializer.data['status']
# 			print(serializer.data)
# 			if status!='All':
# 				status_query = Q(status=status)
# 				projects = Project.objects.filter(status_query)
# 			else:
# 				projects = Project.objects.all()
				

# 			request_field_list = serializer.data.keys()
# 			print(request_field_list)

# 			if 'client_name' in request_field_list:
# 				client_name = serializer.data['client_name']
# 				if client_name != '':
# 					project_client_lookup = Q(client_name__icontains=client_name)
# 					projects = projects.filter(project_client_lookup).distinct()

# 			if 'from_date' in request_field_list:
# 				from_date = serializer.data['from_date']
# 				to_date = serializer.data['to_date']
# 				from_date, to_date = helper.get_from_date_to_date_fromat(from_date, to_date)
# 				if from_date != '' and to_date!='':
# 					projects = projects.filter(start_date__gte=from_date).filter(start_date__lte=to_date)

# 			project_count = helper.get_total_project_count(projects)
# 			if project_count>0:
# 				projects = projects.order_by('-id')
# 				serializer = ProjectDetailSerializer(projects, many=True)
# 				return Response({'response':serializer.data,'total_hits':project_count})
# 			else:
# 				return Response({'response':[],'total_hits':0})

# 		else:
# 			choices_list = [i[0] for i in settings.PROJECT_STATUS_LIST]
# 			comp_logger.info('{} is not valid'.format(data))
# 			comp_logger.info(serializer.errors)
# 			return Response({'response':serializer.errors,'status_options':choices_list})
# 	return Response({})


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def find_project_detail_report(request):
	"""
	Returns Detailed Project Report
	"""
	
	if request.method == 'POST':
		comp_logger.info('Call to find_project_detail_report')
		data = JSONParser().parse(request)
		serializer = ProjectStartSerializer(data=data)

		if serializer.is_valid():
			project_id = serializer.data['id']
			comp_logger.info('Call to find_project_detail_report with id: {}'.format(project_id))

			projects = Project.objects.filter(id=project_id).prefetch_related('projectstatus_set')
			project_count = helper.get_total_project_count(projects)

			if project_count>0:
				project = projects[0]
				serializer = ProjectDetailSerializer(projects, many=True)
				detailed_response_dict = dict(serializer.data[0])

				if project.status!='Pending':
					detailed_response_dict['project_phase'] = settings.PROJECT_PROCESS_STATUS_DICT[project.projectstatus_set.all()[0].project_phase]
					detailed_response_dict['project_completion_percentage'] = project.projectstatus_set.all()[0].project_completion_percentage
					detailed_response_dict['project_completion_datetime'] = project.projectstatus_set.all()[0].last_updated_date
					detailed_response_dict['project_process_initiation_datetime'] = project.projectstatus_set.all()[0].start_datetime
				
				return Response({'response':detailed_response_dict,'total_hits':project_count})
			else:
				return Response({'response':[],'total_hits':0})

		else:
			comp_logger.info('{} is not valid'.format(data))
			comp_logger.info(serializer.errors)
			return Response({'response':serializer.errors})
	return Response({})