from .models import Project, ProjectStatus
from serializers.project_serializers import (
		ProjectInputSerializer,
		ProjectDetailSerializer,
		ProjectStartSerializer,
		ProjectInitSerializer,
		UpdateProjectHumanProcessStatusSerializer
	)
from django.conf import settings
from project.async_tasks import start_async_image_match
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
import pandas as pd
from rest_framework.renderers import JSONRenderer
from helpers import helper, ftp_helper
import logging
from rest_framework.parsers import JSONParser
from django.db.models import Q
from paginators.pagination import ProjectLimitOffsetPagination

comp_logger = logging.getLogger(__name__)

class ProjectList(ListAPIView):
	"""
	List all Projects
	"""
	serializer_class = ProjectDetailSerializer
	pagination_class = ProjectLimitOffsetPagination

	def get_queryset(self, *args, **kwargs):
		projects = Project.objects.all().order_by('-id')
		return projects

class ProjectIDList(APIView):
	"""
	List all distinct client_name
	"""
	def get(self, request, format=None):
		distinct_projectids = Project.objects.all().values_list('id', flat=True)
		return Response({'project_ids':distinct_projectids})



class ProjectDetail(APIView):
	"""
	Retrieve, update or delete a Project instance.
	"""
	def get_object(self, pk):
		try:
			return Project.objects.get(pk=pk)
		except Project.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		project = self.get_object(pk)
		serializer = ProjectDetailSerializer(project)
		return Response(serializer.data)

	# def put(self, request, pk, format=None):
	# 	project = self.get_object(pk)
	# 	serializer = ProjectInputSerializer(project, data=request.data)
	# 	if serializer.is_valid():
	# 		serializer.save()
	# 		return Response(serializer.data)
	# 	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


	def delete(self, request, pk, format=None):
		project = self.get_object(pk)
		project.delete()
		# return Response(status=status.HTTP_204_NO_CONTENT)
		return Response({'status':'Deleted'})



class ProjectMatchNotMatchCount(APIView):
	"""
	Returns number of matched and non-match count for a project
	"""
	renderer_classes = (JSONRenderer, )

	def get(self, request, project_id, format=None):
		comp_logger.info('Call to ProjectMatchNotMatchCount')
		project = Project.objects.filter(id=project_id)

		project_count = helper.get_total_project_count(project)

		if project_count>0:
			project = project[0]
			if project.status in ['Completed','H_InProgress','H_Completed']:
				try:
					total_matched_count, total_notmatched_count = helper.get_project_match_notmatch_count(project_id)
				except:
					return Response({'Final computated file not present for project id:{}'.format(project_id)})	
				return Response({'Match':total_matched_count, 'NotMatch':total_notmatched_count})
			else:
				comp_logger.info('Cannot get result count of a project which is not completed for id:{}'.format(project_id))
				return Response({'response':'Cannot get result count of a project which is not completed'})
		else:
			return Response({'response':'Project with specified id is not completed.'})


def get_projects_inprogress():
	active_projects = Project.objects.filter(status='InProgress').order_by('-id')
	return active_projects


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def create_project(request):
	"""
	Create project and return information
	"""
	if request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = ProjectInitSerializer(data=data)
		comp_logger.info('Call to create_project')
		if serializer.is_valid():
			client_name = serializer.data['client_name']
			file_name = serializer.data['file_name']
			
			# project = Project(status='Pending', client_name=client_name,file_name=file_name, total_records=total_records,total_unique_products=total_unique_products)

			# Project save section
			try:
				project = Project(status='Pending', client_name=client_name,file_name=file_name)
				project.save(force_insert=True)
				comp_logger.info('Project created with id: {}'.format(project.id))
				
			except Exception as e:
				# Raise an issue if the project cannot be saved. Most likely due to ftp file transfer failure
				comp_logger.info('Cannot save project for client_name:{} and file:{}'.format(client_name, file_name))
				return Response({'response':str(e)})


			serializer = ProjectDetailSerializer(project)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		else:
			comp_logger.info('{} is not valid'.format(data))
			comp_logger.info(serializer.errors)
			return Response({'response':serializer.errors})
	return Response({})


@api_view(['PUT'])
@renderer_classes((JSONRenderer,))
def start_project(request):
	"""
	Start Project Process
	"""
	
	if request.method == 'PUT':
			
		data = JSONParser().parse(request)
		serializer = ProjectStartSerializer(data=data)
		comp_logger.info('Call to start_project')
		if serializer.is_valid():
			project_id = serializer.data['id']
			# check if there is another process already running
			currently_running_projects = get_projects_inprogress()
			currently_running_project_count = helper.get_total_project_count(currently_running_projects)
			if currently_running_project_count != 0:
				return Response({'response':'Cannot start project for id:{} since another project is already running.'.format(project_id),'started':False})		
			else:
				try:
					project = Project.objects.get(id=project_id)
				except Project.DoesNotExist:
					return Response({'response':'Project with id:{} not found'.format(project_id),'started':False})
				
				if project.status in ['Completed','H_InProgress','H_Completed']:
					return Response({'response':'Project with id:{} cannot be started as it is already completed.'.format(project_id),'started':False})	

				# starting project
				comp_logger.info('Starting project with id:{}'.format(project_id))
				
				# check if the input file has been successfully copied				
				if helper.check_input_file_exists(project_id,project.file_name):
					project.status = 'InProgress'
					project.save()
					project_status = ProjectStatus.objects.filter(project=project)
					# check if project status is present
					if len(project_status)>0:
						project_status = project_status[0]
					else:
						project_status = ProjectStatus(project=project,project_phase='1')
						project_status.save(force_insert=True)

					comp_logger.info('calling async task handler for id:{}'.format(project_id))
					start_async_image_match.delay(project_id=project_id)	# Async Process Start
					
					return Response({'response':'Project started for id:{}'.format(project_id),'started':True})
				else:
					return Response({'response':'Project for id:{} not started as file hasn\'t been copied from ftp location'.format(project_id),'started':False})
		else:
			comp_logger.info('{} is not valid'.format(data))
			comp_logger.info(serializer.errors)
			return Response({'response':serializer.errors})
	return Response({})


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def get_inprogress_project(request):
	"""
	Returns list of Projects currently in progress
	"""
	if request.method == 'GET':
		comp_logger.info('Call to get_inprogress_project')
		currently_running_projects = get_projects_inprogress()
		project_count = helper.get_total_project_count(currently_running_projects)
		if project_count>0:
			serializer = ProjectDetailSerializer(currently_running_projects, many=True)
			return Response({'response':serializer.data})
		else:
			return Response({'response':[]})
	return Response({})


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def terminate_inprogress_project(request):
	"""
	Terminate Asynchronous Image Matching Service
	"""
	
	if request.method == 'POST':
		comp_logger.info('Call to terminate_inprogress_project')
		data = JSONParser().parse(request)
		serializer = ProjectStartSerializer(data=data)

		if serializer.is_valid():
			project_id = serializer.data['id']
			comp_logger.info('Call to terminate_inprogress_project with id: {}'.format(project_id))

			projects = Project.objects.filter(id=project_id)
			project_count = helper.get_total_project_count(projects)

			if project_count>0:
				projects = projects.filter(status='InProgress')
				project_count = helper.get_total_project_count(projects)

				if project_count>0:
					project = projects[0]
					project_status = ProjectStatus.objects.get(project=project)
					async_task_id = project_status.asynctask_id
					helper.terminate_async_task(task_id=async_task_id)
					project.status = 'Terminated'
					project.failed_log = 'Project terminated externally.'
					project.save()

					return Response({'response':'Project Process Terminated'})
				else:
					return Response({'response':'Project with specified id is not in progress at the moment.'})

			else:
				return Response({'response':'Project with specified id not found.'})

		else:
			comp_logger.info('{} is not valid'.format(data))
			comp_logger.info(serializer.errors)
			return Response({'response':serializer.errors})
	return Response({})


@api_view(['PUT'])
@renderer_classes((JSONRenderer,))
def update_human_verification_status(request):
	"""
	Start Human Process
	"""
	
	if request.method == 'PUT':
		serializer = UpdateProjectHumanProcessStatusSerializer(data=request.data)
		comp_logger.info('Call to update_human_verification_status')
		if serializer.is_valid():
			project_id = serializer.data['id']
			project_status_to_update = serializer.data['status']


			# Only Human Verification Statuses Update
			if project_status_to_update in ['H_InProgress','H_Completed']:
				try:
					project = Project.objects.get(id=project_id)
				except Project.DoesNotExist:
					return Response({'response':'Project with id:{} not found'.format(project_id),'started':False})
				
				# Current Project Status
				current_project_status = project.status

				if project_status_to_update == 'H_InProgress':
					# For H_InProgress
					if current_project_status == 'H_InProgress':
						return Response({'response':'Human Verification for Project with id:{} cannot be updated as it is already in H_InProgress'.format(project_id),'started':False})	

					if current_project_status == 'H_InProgress':
						return Response({'response':'Human Verification for Project with id:{} cannot be updated as it is already in H_Completed'.format(project_id),'started':False})	

					elif current_project_status != 'Completed':
						return Response({'response':'Human Verification for Project with id:{} cannot be updated as it is not completed.'.format(project_id),'started':False})	

					project.status = 'H_InProgress'
					project.save()
					return Response({'response':'H_InProgress status updated for Project updated with id:{}'.format(project_id),'started':True})

				else:
					# For H_Completed
					if current_project_status == 'H_Completed':
						return Response({'response':'Human Verification for Project with id:{} cannot be updated as it is already in H_Completed'.format(project_id),'started':False})	

					elif current_project_status != 'H_InProgress':
						return Response({'response':'Human Verification for Project with id:{} cannot be updated as it is not in progress.'.format(project_id),'started':False})	

					project.status = 'H_Completed'
					project.save()
					return Response({'response':'H_Completed status updated for Project started with id:{}'.format(project_id),'started':True})
				
			else:
				return Response({'response':'Cannot update Project status with id:{}'.format(project_id),'started': False})
		else:
			choices_list = ['H_InProgress','H_Completed']
			comp_logger.info('{} is not valid'.format(request.data))
			comp_logger.info(serializer.errors)
			return Response({'response':serializer.errors,'status_options':choices_list})
	return Response({})