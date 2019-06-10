from __future__ import absolute_import

from celery import shared_task,task
from core.ProjectProcessHandler import ProjectProcessHandler
from .models import Project, ProjectStatus
from rest_image_match_server.celery_settings import app as celery_app
import logging
comp_logger = logging.getLogger(__name__)



# to start the celery worker daemon
#celery worker -A rest_image_match_server.celery_settings -l info
#flower -A rest_image_match_server --port=5555   --> to view error log of celery


@shared_task(bind=True)
def start_async_image_match(self, project_id):

	comp_logger.info('Initiating Matching Sequece for id:{}'.format(project_id))
	project = Project.objects.get(id=project_id)
	project_status = ProjectStatus.objects.get(project=project)
	async_task_id = self.request.id
	project_status.asynctask_id = async_task_id
	project_status.save()

	projecthandler = ProjectProcessHandler(project, project_status)
	comp_logger.info('Initiating Matching Sequece for id:{} with task_id:{}'.format(project_id, async_task_id))
	projecthandler.start()
