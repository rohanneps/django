from rest_framework.views import APIView
from rest_framework.response import Response
from project.models import Project
import logging


comp_logger = logging.getLogger(__name__)


class ClientDistinctList(APIView):
	"""
	List all distinct client_name
	"""
	def get(self, request, format=None):
		distinct_clients = Project.objects.all().values_list('client_name', flat=True).distinct()
		return Response({'client_name':distinct_clients})


