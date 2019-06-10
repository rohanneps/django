from django.urls import path
from .views import (
		# find_projects_by_client,
		# find_projects_by_date,
		# find_projects_by_status,
		# find_projects_by_client_date_status,
		find_project_detail_report,
		SearchProjectsByClient,
		SearchProjectsByDate,
		SearchProjectsByStatus,
		SearchProjectsByClientDateStatus
	)
from rest_framework.urlpatterns import format_suffix_patterns

# project name
app_name='search'

urlpatterns = [
    # path('searchprojectsbyclient/', find_projects_by_client, name='searchprojectsbyclient'),
    path('searchprojectsbyclient/', SearchProjectsByClient.as_view(), name='searchprojectsbyclient'),
    path('searchprojectsbydate/', SearchProjectsByDate.as_view(), name='searchprojectsbydate'),
    # path('searchprojectsbydate/', find_projects_by_date, name='searchprojectsbydate'),
    # path('searchprojectsbystatus/', find_projects_by_status, name='searchprojectsbystatus'),
    path('searchprojectsbystatus/', SearchProjectsByStatus.as_view(), name='searchprojectsbystatus'),
    # path('searchprojectsbyclientdatestatus/', find_projects_by_client_date_status, name='searchprojectsbyclientdatestatus'),
    path('searchprojectsbyclientdatestatus/', SearchProjectsByClientDateStatus.as_view(), name='searchprojectsbyclientdatestatus'),
    path('searchprojectdetailedreport/', find_project_detail_report, name='searchprojectdetailedreport'),

]

urlpatterns = format_suffix_patterns(urlpatterns)