# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import ProjectXpath, ProjectUrl, ProjectComparator
# Register your models here.


class ProjectComparatorAdmin(admin.ModelAdmin):
	list_display = ('id','project','user','start_time','comparison_type','project_status','error_count')
	readonly_fields = ('project','user','start_time','comparison_type','project_status','error_count','project_url_file','project_xpath_file','project_platform_import_file','project_scrapper_output_file','project_report_file')
	list_filter = ('project','user','start_time','run_priority','project_status','error_count' )
	search_fields = ('project__project_name','user__username','start_time','run_priority','project_status', )
	fieldsets=[
				('Project details',{'fields':['project','user','start_time','comparison_type','project_status','error_count']}),
				('Input Files',{'fields':['project_url_file','project_xpath_file','project_platform_import_file']}),
				('Output Files',{'fields':['project_scrapper_output_file','project_report_file']}),
				]			

class ProjectXpathAdmin(admin.ModelAdmin):
	list_display = ('project','project_comparator_id','field_name','xpath','timestamp')
	readonly_fields = ('project','project_comparator_id','field_name','xpath','timestamp')
	list_filter = ('project',)
	search_fields = ('project__project_name',)
	

class ProjectUrlAdmin(admin.ModelAdmin):
	list_display = ('project','project_comparator_id','url','primary_identifier','timestamp')	
	readonly_fields = ('project','project_comparator_id','url','primary_identifier','timestamp')	
	list_filter = ('project',)
	search_fields = ('project__project_name',)


admin.site.register(ProjectComparator, ProjectComparatorAdmin)
admin.site.register(ProjectUrl, ProjectUrlAdmin)
admin.site.register(ProjectXpath, ProjectXpathAdmin)
