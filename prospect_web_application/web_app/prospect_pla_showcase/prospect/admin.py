from django.contrib import admin
from .models import Prospect, RunDetails, AmazonRunDetails
# Register your models here.


class ProspectAdmin(admin.ModelAdmin):
	list_display = ['id','name', 'file_name','email_recipients','start_date','last_updated_date',\
					'status','run_count','platform']
					
	list_filter = ['status','start_date','name','platform']
	search_fields = ['id','name', 'file_name','email_recipients','start_date','status','platform']

	readonly_fields = ['start_date','run_count','platform']

	fieldsets=[
				('Basic Info',{'fields':['name','file_name','start_date','run_count','platform']}),

				('Active Status', {'fields': ('status',)}),

				('Notification', {'fields': ('email_recipients',)}),
				
				]	


	class Meta:
		model = Prospect
		
admin.site.register(Prospect, ProspectAdmin)


class GoogleRunDetailsAdmin(admin.ModelAdmin):
	list_display = ['id','prospect', 'date_time','file_size','total_pla_records','total_showcase_records',\
					'batch_email_sent', 'post_process_completed']
					
	list_filter = ['date_time','file_size','total_pla_records','total_showcase_records','batch_email_sent','post_process_completed']

	search_fields = ['id','prospect', 'file_size','total_pla_records','total_showcase_records','batch_email_sent']

	readonly_fields = ['prospect','date_time', 'file_size','total_pla_records','total_showcase_records','batch_email_sent']

	fieldsets=[
				('Basic Info',{'fields':['prospect','file_size',]}),
				('Run Date Time',{'fields':['date_time']}),

				('Count Status', {'fields': ('total_pla_records','total_showcase_records')}),

				('Notification', {'fields': ('batch_email_sent','post_process_completed',)}),
				
				]	


	class Meta:
		model = RunDetails
		
admin.site.register(RunDetails, GoogleRunDetailsAdmin)


class AmazonRunDetailsAdmin(admin.ModelAdmin):
	list_display = ['id','prospect', 'date_time','total_amazon_choices_records','total_brands_related_records','total_editorial_recommendations_records',\
					'total_organic_records','total_sponsored_records','total_today_deals_records','batch_email_sent', 'post_process_completed']
					
	list_filter = ['date_time','total_amazon_choices_records','total_brands_related_records','total_editorial_recommendations_records',\
				   'total_organic_records','total_sponsored_records','total_today_deals_records','batch_email_sent', 'post_process_completed']

	search_fields = ['id','prospect', 'total_amazon_choices_records','total_brands_related_records','total_editorial_recommendations_records',\
				   'total_organic_records','total_sponsored_records','total_today_deals_records','batch_email_sent', 'post_process_completed']

	readonly_fields = ['prospect','date_time', 'total_amazon_choices_records','total_brands_related_records','total_editorial_recommendations_records',\
				   'total_organic_records','total_sponsored_records','total_today_deals_records','batch_email_sent', 'post_process_completed']

	fieldsets=[
				('Basic Info',{'fields':['prospect',]}),
				('Run Date Time',{'fields':['date_time']}),

				('Count Status', {'fields': ('total_amazon_choices_records','total_brands_related_records','total_editorial_recommendations_records','total_organic_records','total_sponsored_records','total_today_deals_records')}),

				('Notification', {'fields': ('batch_email_sent','post_process_completed',)}),
				
				]	


	class Meta:
		model = AmazonRunDetails
		
admin.site.register(AmazonRunDetails, AmazonRunDetailsAdmin)