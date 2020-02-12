from django.shortcuts import reverse, render
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.http import HttpResponseRedirect
from .models import Prospect, RunDetails, AmazonRunDetails
from .forms import ProspectForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

import logging

comp_logger = logging.getLogger(__name__)

def home(request):
	# return HttpResponse("Home of Prospects")
	if not request.user.is_authenticated:
		return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
	else:
		return HttpResponseRedirect (reverse ('app_home'))



class ProspectListView(LoginRequiredMixin, ListView):
	login_url = settings.LOGOUT_REDIRECT_URL
	redirect_field_name = 'redirect_to'
	queryset = Prospect.objects.all().order_by('-id')
	template_name = 'prospect/list.html'
	context_object_name = 'prospect_list'
	paginate_by = 10

	def get_queryset(self):
		query = self.request.GET.get("q")
		if query and query not in ['',' ']:
			comp_logger.info('Prospect search for term: {}.'.format(query))
			prospect_lookup = (Q(name__icontains=query) | Q(status__icontains=query) | Q(file_name__icontains=query) | \
								Q(id__icontains=query) | Q(run_count__icontains=query))
			return Prospect.objects.filter(prospect_lookup).distinct().order_by('-id')
		else:
			return Prospect.objects.all().order_by('-id')


class ProspectDetailView(LoginRequiredMixin, DetailView):
	login_url = settings.LOGOUT_REDIRECT_URL
	redirect_field_name = 'redirect_to'
	context_object_name = 'prospect_obj'
	template_name = 'prospect/detail.html'
	queryset = Prospect.objects.all()



class GoogleDetailsListView(LoginRequiredMixin, ListView):
	login_url = settings.LOGOUT_REDIRECT_URL
	redirect_field_name = 'redirect_to'
	queryset = RunDetails.objects.all().order_by('-id')
	template_name = 'run_details/google_all.html'
	context_object_name = 'run_details_list'
	paginate_by = 10

	def get_queryset(self):
		query = self.request.GET.get("q")
		if query and query not in ['',' ']:
			comp_logger.info('Prospect search for term: {}.'.format(query))
			run_details_lookup = (Q(prospect__name__icontains=query) | Q(post_process_completed__icontains=query) | \
								Q(date_time__icontains=query) |  Q(file_size__icontains=query))
			return RunDetails.objects.filter(run_details_lookup).distinct().select_related('prospect').order_by('-id')
		else:
			return RunDetails.objects.all().order_by('-id')


class AmazonDetailsListView(LoginRequiredMixin, ListView):
	login_url = settings.LOGOUT_REDIRECT_URL
	redirect_field_name = 'redirect_to'
	queryset = AmazonRunDetails.objects.all().order_by('-id')
	template_name = 'run_details/amazon_all.html'
	context_object_name = 'run_details_list'
	paginate_by = 10

	def get_queryset(self):
		query = self.request.GET.get("q")
		if query and query not in ['',' ']:
			comp_logger.info('Prospect search for term: {}.'.format(query))
			run_details_lookup = (Q(prospect__name__icontains=query) | Q(post_process_completed__icontains=query) | \
								Q(date_time__icontains=query))
			return AmazonRunDetails.objects.filter(run_details_lookup).distinct().select_related('prospect').order_by('-id')
		else:
			return AmazonRunDetails.objects.all().order_by('-id')


def schedule_prospect(requests):
	if not requests.user.is_authenticated:
		return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
	else:
		template = 'prospect/schedule.html'
		form = ProspectForm(initial={'platform': 'Google'})
		prospect_id = None

		if requests.method == 'POST' and requests.FILES:
			form  = ProspectForm(requests.POST or None, requests.FILES or None)
			if form.is_valid():
				
				name = form.cleaned_data['name']
				file_name = form.cleaned_data['file_name']
				email_recipients = form.cleaned_data['email_recipients']
				platform = form.cleaned_data['platform']
				prospect = Prospect(name=name, file_name=file_name, email_recipients=email_recipients, platform=platform)
				prospect.save(force_insert=True)
				prospect_id = prospect.id
				comp_logger.info('Prospect created for id: {}.'.format(prospect_id))


		context = {
			'form':form,
			'prospect_id':prospect_id
		}
		
		return render(requests, template, context)