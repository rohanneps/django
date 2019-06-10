from django.conf.urls import url
from . import views

app_name = 'project'

urlpatterns = [
	url(r'^changepassword/',views.changePassword,name='change_password'),
	url(r'^passwordchangereq/',views.changePasswordResult,name='change_password_request'),
	url(r'^(?P<pk>[0-9]+)/$', views.ProjectDetailView.as_view(), name='project_detail'),
    url(r'^',views.ProjectList.as_view(),name='project_list'),
       

]