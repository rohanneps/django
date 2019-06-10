from django import template
from django.conf import settings
import os

register = template.Library()


@register.assignment_tag(takes_context=True)
def file_exists(context,file_name, project_name, file_dir):
	
	if file_dir == 'media':
		file_path = os.path.join(settings.MEDIA_ROOT,project_name,file_name)
	else:
		file_path = os.path.join(settings.OUTPUT_ROOT,project_name,file_name)

	if os.path.exists(file_path):
		return True
	else:
		return False