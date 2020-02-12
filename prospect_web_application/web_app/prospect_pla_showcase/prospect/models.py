from django.db import models
from django.db.models.signals import pre_save
from django.conf import settings

# Create your models here.


class Prospect(models.Model):
	
	class Meta:
		verbose_name_plural = 'Prospects'
	
	name = models.CharField(max_length=200)
	# file_name = models.CharField(max_length=200, blank=False,null=False)
	file_name = models.FileField(upload_to='prospect_input', blank=False, null=False)
	email_recipients = models.CharField(max_length=300, null=True)
	start_date = models.DateTimeField(auto_now=False, auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True, auto_now_add=False)
	status = models.BooleanField(default=True)
	run_count = models.IntegerField(default=0)
	
	platform = models.CharField(max_length=20, choices=settings.PLATFORM_LIST, blank=False, null=False)

	def __str__(self):
		return str(self.name)

	def get_email_recipient_list(self):
		return self.email_recipients.split(',')

	def get_other_column_header_list(self):
		return self.other_column_header_list.split(',')



class RunDetails(models.Model):
	"""
	Google Run Details
	"""
	class Meta:
		verbose_name_plural = 'Google_Run_Details'

	prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE)
	date_time = models.DateTimeField(auto_now=False, auto_now_add=True)
	file_size = models.CharField(max_length=50, default='0 KB')
	total_pla_records = models.IntegerField(default=0)
	total_showcase_records = models.IntegerField(default=0)
	post_process_completed = models.BooleanField(default=False)
	batch_email_sent = models.BooleanField(default=False)

class AmazonRunDetails(models.Model):
	class Meta:
		verbose_name_plural = 'Amazon_Run_Details'

	prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE)
	date_time = models.DateTimeField(auto_now=False, auto_now_add=True)
	total_amazon_choices_records = models.IntegerField(default=0)
	total_brands_related_records = models.IntegerField(default=0)
	total_editorial_recommendations_records = models.IntegerField(default=0)
	total_organic_records = models.IntegerField(default=0)
	total_sponsored_records = models.IntegerField(default=0)
	total_today_deals_records = models.IntegerField(default=0)
	post_process_completed = models.BooleanField(default=False)
	batch_email_sent = models.BooleanField(default=False)

