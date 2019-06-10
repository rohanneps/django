# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from project.models import Project,ProjectUser
from engine.models import ProjectComparator, ProjectUrl, ProjectXpath
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
import logging

comp_logger = logging.getLogger(__name__)


# Check to see if user is assigned to project
def is_user_assigned_to_project(request,project):
        return ProjectUser.objects.filter(user=request.user, project=project).exists()


# project comparison history view
class ProjectComparisonHistory(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'history/project_comparasion_history.html'
    context_object_name = 'project_comparison_history_list'
    paginate_by = 20
    def get_project_details(self,project_id):
        return Project.objects.filter(pk = project_id)

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        # project = Project.objects.filter(pk = project_id)
        user = self.request.user
        project = self.get_project_details(project_id)
        comp_logger.info('Project History seen for '+str(project_id)+' by user '+str(user))

        query = self.request.GET.get("q")
        if query:
            return ProjectComparator.objects.filter(project =project, user__username__icontains =query).select_related('project','user').order_by('-id')
        else:
            return ProjectComparator.objects.filter(project =project).select_related('project','user').order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(ProjectComparisonHistory, self).get_context_data(**kwargs)
        project_id = self.kwargs['project_id']
        try:
            # project = Project.objects.get(pk = project_id)
            project = self.get_project_details(project_id)
        except:
            # if project doesn't exist
            project = None
        context['project_id'] = project_id
        context['project_name'] = project[0].project_name
        # context['project_user'] = self.request.user
        context['is_user_assigned_to_project'] = is_user_assigned_to_project(self.request,project)

        return context

  
# project url history view
class ProjectUrlHistory(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'history/project_url_history.html'
    context_object_name = 'project_url_history_list'    
    paginate_by = 2
    
    def get_project(self,project_id):
        return Project.objects.filter(pk = project_id)

    def get_queryset(self):
        query = self.request.GET.get("primary_id")
        project_id = self.kwargs['project_id']
        # project = Project.objects.filter(pk = project_id)
        project = self.get_project(project_id)
        
        if query:
            return ProjectUrl.objects.filter(project =project,primary_identifier__icontains=query).select_related('project').order_by('-id')
        else:
            return ProjectUrl.objects.filter(project =project).select_related('project').order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(ProjectUrlHistory, self).get_context_data(**kwargs)
        project_id = self.kwargs['project_id']
        # project = Project.objects.get(pk = project_id)
        project = self.get_project(project_id)
        context['project_id'] = project_id
        context['project_name'] = project[0].project_name
        context['is_user_assigned_to_project'] = is_user_assigned_to_project(self.request,project)

        return context


# project xpath history view
class ProjectXpathHistory(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'history/project_xpath_history.html'
    context_object_name = 'project_xpath_history_list'
    paginate_by = 40

    def get_project(self,project_id):
        return Project.objects.filter(pk = project_id)

    def get_queryset(self):
        query = self.request.GET.get("xpath_field")
        project_id = self.kwargs['project_id']
        # project = Project.objects.filter(pk = project_id)
        project = self.get_project(project_id)
        if query:
            return ProjectXpath.objects.filter(project =project,field_name__icontains=query).select_related('project').order_by('-id')
        else:
            return ProjectXpath.objects.filter(project =project).select_related('project').order_by('-id')


        

    def get_context_data(self, **kwargs):
        context = super(ProjectXpathHistory, self).get_context_data(**kwargs)
        project_id = self.kwargs['project_id']
        # project = Project.objects.get(pk = project_id)
        project = self.get_project(project_id)
        context['project_name'] = project[0].project_name
        context['project_id'] = project_id
        context['is_user_assigned_to_project'] = is_user_assigned_to_project(self.request,project)
        return context
