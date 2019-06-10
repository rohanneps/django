from django.conf.urls import url
from . import views

app_name = 'history'

urlpatterns = [
	url(r'^(?P<project_id>[0-9]+)/projectcomparatorhistory$', views.ProjectComparisonHistory.as_view(),name='project_comparator_history'),
	url(r'^(?P<project_id>[0-9]+)/projecturlhistory$', views.ProjectUrlHistory.as_view(),name='project_url_history'),
	url(r'^(?P<project_id>[0-9]+)/projectxpathhistory$', views.ProjectXpathHistory.as_view(),name='project_xpath_history'),

]