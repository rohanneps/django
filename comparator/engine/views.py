# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import models as auth_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect,render,reverse,render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from project.forms import StartProjectComparatorForm
from .databasehandler import ProjectComparatorORM, ProjectUrlORM, ProjectXpathORM
from project.models import Project,ProjectUser
from .models import ProjectComparator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
import logging
import os
import time
from django.views.decorators.clickjacking import xframe_options_sameorigin
from wsgiref.util import FileWrapper
import mimetypes

# initializing logger
comp_logger = logging.getLogger(__name__)

 #Saving uploaded files to media folder
def upload(request,project_id):
    current_timestamp = time.strftime("%y%m%d-%H%M%S")
    import_file_names = []

    #Creating project folder
    project = Project.objects.get(pk=project_id)
    project_folder = project.project_name
    import_file_dir = os.path.join(settings.MEDIA_ROOT,project_folder)


    if not os.path.exists (import_file_dir):
        os.makedirs (import_file_dir)

    for files in request.FILES:
        #open(settings.BASE_DIR + '/media/' + str(request.FILES[files]), 'wb')
        file_name = current_timestamp+'_'+str(request.FILES[files])
        file_name_path = os.path.join(project_folder,file_name)
        # print file_name_path
        import_file_names.append(file_name)
        with open(os.path.join(settings.MEDIA_ROOT,file_name_path), 'wb') as destination:
            for file_chunk in request.FILES[files].chunks():
                destination.write(file_chunk)  
    return import_file_names

def save_details_to_database(request,post_details, project_id, import_file_names):
    project = Project.objects.get(pk=project_id)
    # Storing Project Comparison details in database
    project_comparator_task = ProjectComparatorORM(request, post_details, project, import_file_names)
    project_comparator_task.insert_details_into_database()
    #request.COOKIES['sessionid'] another way to get session id
    # session_id =  request.session._session_key
    comp_logger.info('Inserting project comparison details to database for {} by {}'.format(str(project),str(request.user)))

    # project_url_thread = ProjectUrlORM(post_details['url_file'].name, project)
    # project_url_thread.start()
    # comp_logger.info('Inserting url details to database for '+str(project)+' by '+str(request.user))

    # project_xpath_thread = ProjectXpathORM(post_details['xpath_file'].name, project)
    # project_xpath_thread.start()
    # comp_logger.info('Inserting xpath details to database for '+str(project)+' by '+str(request.user))

    # project_comparator_thread.join()

    # getting the last inserted project comparison id.
    process_id = project_comparator_task.get_project_comparator_id()
    # print process_id
    return process_id


#Comparator entry point view
def process_comparison_start_form(request, project_id):
    # Check for user authentication
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, settings.LOGIN_REDIRECT_URL))
    else:
        # print request.FILES
        if request.method == 'POST' and request.FILES:
            form = StartProjectComparatorForm(request.POST, request.FILES)
            if form.is_valid():
                #Check to see if any comparison task if running for user.
                comparison_running = ProjectComparator.objects.filter(user =request.user,project_status=ProjectComparator.RUN)
                if comparison_running:
                    comparison_running = True
                    return HttpResponseRedirect (reverse ('engine:comparison_not_started'))
                else:
                    # uploading files to media folder and getting names of file
                    import_file_names = upload(request,project_id)
                    comp_logger.info('Project:[{}] Inserting details to database'.format(project_id))
                    process_id = save_details_to_database(request,form.cleaned_data, project_id, import_file_names)
                    return HttpResponseRedirect (reverse ('engine:after_form_valid', kwargs = {'process_id': process_id}))
        else:
            return HttpResponseRedirect(reverse('project:project_detail',args=(project_id)))


# Check to see if user is assigned to project
def get_project_comparator_object(request,process_id):
        return ProjectComparator.objects.filter(pk=process_id,user=request.user).select_related('project','user')


def comparison_not_started(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, settings.LOGIN_REDIRECT_URL))
    else:
        comp_logger.info('Comparator existing for user'+str(request.user))
        template = 'engine/comparator_not_started.html'
        context = {
            'user':request.user,
            }
        return render(request, template,context)


def begin_comparison(request, process_id):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, settings.LOGIN_REDIRECT_URL))
    else:
        comp_logger.info('Comparator started by '+str(request.user) +' with id: '+str(process_id))
        template = 'engine/startengine.html'
        project_comparator = get_project_comparator_object(request, process_id)
        context = {
            'process_id':process_id,
            'user':request.user,
            'project_comparator':project_comparator,
            }
        return render(request, template,context)



class ComparisonHistoryList(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'engine/comparison_history_list.html'
    context_object_name = 'comparison_history_list'
    paginate_by = 40
    def get_queryset(self):
        # return ProjectComparator.objects.filter(user =self.request.user).select_related('project')
        query = self.request.GET.get("q")
        if query:
            return ProjectComparator.objects.filter(user =self.request.user,project__project_name__icontains=query).values('id','start_time','project__project_name','project_status','run_priority').order_by('-id')            
        else:
            return ProjectComparator.objects.filter(user =self.request.user).values('id','start_time','project__project_name','project_status','run_priority').order_by('-id')


class ComparisonHistoryDetailView(LoginRequiredMixin, generic.DetailView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = ProjectComparator
    template_name = 'engine/comparison_history_detail.html'
    context_object_name = 'project_comparator'

    def get_object(self):
        process_id = self.kwargs['pk']
        try:
            return self.model.objects.filter(user=self.request.user, id=process_id).select_related('user','project')[0]
        except:
            return None
        
        
    
    def get_context_data(self, **kwargs):
        context = super(ComparisonHistoryDetailView, self).get_context_data(**kwargs)
        
        process_id = self.kwargs['pk']
        context['process_id'] = process_id
        return context


@xframe_options_sameorigin
def status(request, process_id):
    pc = ProjectComparator.objects.filter (user = request.user, id = process_id).select_related ('user', 'project')[0]
    return HttpResponse(pc.project_status)

#downloading files
def file_download(request,project_name,file_name,file_dir):
    # comp_logger.info(settings.OUTPUT_ROOT)
    # comp_logger.info(file_name)
    if file_dir == 'media':
        file_path = os.path.join(settings.MEDIA_ROOT,project_name,file_name)
    else:
        file_path = os.path.join(settings.OUTPUT_ROOT,project_name,file_name)
    file_wrapper = FileWrapper(file(file_path,'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype )
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % (file_name) 
    return response