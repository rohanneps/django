# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect
from django.shortcuts import render,render_to_response,reverse
from django.views import generic
from .models import Project,ProjectUser
from django.contrib.auth import models as auth_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from .forms import StartProjectComparatorForm,PasswordUpdateForm
import logging
from django.shortcuts import redirect

comp_logger = logging.getLogger(__name__)
# Create your views here.


class ProjectList(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'project/project_list.html'
    context_object_name = 'project_list'
    paginate_by = 15
    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return ProjectUser.objects.filter(user =self.request.user,project__project_name__icontains=query).select_related('project')
        else:
            return ProjectUser.objects.filter(user =self.request.user).select_related('project')


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Project
    template_name = 'project/project_detail.html'

    def is_user_assigned_to_project(self,project):
        return ProjectUser.objects.filter(user=self.request.user, project=project).exists()


    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['project_id'] = context['project'].id
        context['form'] = StartProjectComparatorForm()
        context['is_user_assigned_to_project'] = self.is_user_assigned_to_project(context['project'])

        return context


#Change Password request handler
def changePassword(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, settings.LOGIN_REDIRECT_URL))
    else:
        template = 'project/change_password.html'
        context= {
            'password_update_form' : PasswordUpdateForm()
            }
        return render(request, template,context)



# Handling Whether password is changed or not

def changePasswordResult(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, settings.LOGIN_REDIRECT_URL))
    else:
        if len(request.POST)>1:
            current_password = request.POST['current_password']
            new_password = request.POST['new_password']


            # Checking current password
            if request.user.check_password(current_password):
                comp_logger.info('Password updated successfully for -> '+str(request.user))
                request.user.set_password(new_password)
                request.user.save()
                is_password_changed = 1
                
            else:
                is_password_changed = 2
            template = 'project/change_password_result.html'
            context = {
                'is_password_changed':is_password_changed,
                }
            return render(request, template,context)
        else:
            return HttpResponseRedirect(reverse('project:change_password'))            



