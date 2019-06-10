from django.urls import path
from .views import (
		ProjectList,
		ProjectIDList,
		ProjectDetail,
		create_project,
		start_project,
		get_inprogress_project,
		terminate_inprogress_project,
		ProjectMatchNotMatchCount,
		update_human_verification_status
	)
from rest_framework.urlpatterns import format_suffix_patterns


# project namespace
app_name='project'


urlpatterns = [
    path('all/', ProjectList.as_view(), name='projectlist'),
    path('idall/', ProjectIDList.as_view(), name='projectidlist'),
    # path('project/<int:pk>/', ProjectDetail.as_view(), name='projectdetail'),
    path('<int:pk>/', ProjectDetail.as_view(), name='projectdetail'),
    path('createproject/', create_project, name='createproject'),
    path('startproject/', start_project, name='startproject'),
    path('getinprogressproject/', get_inprogress_project, name='getinprogressproject'),
    path('terminateinprogressproject/', terminate_inprogress_project, name='terminateinprogressproject'),
    path('getprojectmatchnotmatchcount/<int:project_id>/',ProjectMatchNotMatchCount.as_view(), name='getprojectmatchnotmatchcount'),
    path('updatehumanverification/', update_human_verification_status, name='updatehumanverification'),
]

# for handling for cases like /project/1.json
urlpatterns = format_suffix_patterns(urlpatterns)