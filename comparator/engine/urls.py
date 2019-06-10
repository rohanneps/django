from django.conf.urls import url
from . import views

app_name = 'engine'

urlpatterns = [
    url(r'^userhistory/',views.ComparisonHistoryList.as_view(),name='comparison_list'),
    url(r'^(?P<pk>[0-9]+)/comphistory$', views.ComparisonHistoryDetailView.as_view(), name='project_comparison_detail'),
    url(r'^(?P<project_id>[0-9]+)/$',views.process_comparison_start_form,name='start_comparator'),
    url(r'^(?P<process_id>[0-9]+)/process/$', views.begin_comparison, name='after_form_valid'),
    url(r'^comparison-not-started/$', views.comparison_not_started, name='comparison_not_started'),
    url(r'^(?P<process_id>[0-9]+)/get-comparison-status$', views.status, name = 'stats'),
    url(r'^download/(?P<file_dir>.+)/(?P<project_name>.+)/(?P<file_name>.+)$', views.file_download, name='file_download'),

]