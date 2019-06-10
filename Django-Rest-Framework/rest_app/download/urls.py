from django.urls import path

from .views import (
		InitiateESHumanVeriedMatchedResultSetDownloader,
		file_download
	)
from rest_framework.urlpatterns import format_suffix_patterns


app_name='download'

urlpatterns = [
	
	path('initiatematchdownload/<int:project_id>/', InitiateESHumanVeriedMatchedResultSetDownloader.as_view(), name='initiatematchdownload'),
	path('matchresultsetdownload/<int:project_id>/', file_download, name='file_download'),
]

urlpatterns = format_suffix_patterns(urlpatterns)