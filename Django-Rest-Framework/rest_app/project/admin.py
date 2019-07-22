from django.contrib import admin
from .models import Project, ProjectStatus
# Register your models here.


class ProjectAdmin(admin.ModelAdmin):
	list_display = ['id','client_name','file_name','start_date','status','failed_log','total_records','total_unique_products']
	list_filter = ['status','start_date']
	search_fields = ['id','client_name','file_name','status','failed_log']
	readonly_fields = ['total_records','total_unique_products','start_date']
	fieldsets=[
				('Project Info',{'fields':['client_name','file_name','start_date']}),

				('Project Progress Status', {'fields': ('status','failed_log'),}),
				
				('Project File Info', {
					# 'classes': ('collapse',),
					'fields': ('total_records','total_unique_products',),
				}),
				]	


	class Meta:
		model = Project
		
admin.site.register(Project, ProjectAdmin)



class ProjectStatusAdmin(admin.ModelAdmin):
	list_display = ['id','project','project_id','start_datetime','last_updated_date','project_phase','project_completion_percentage','asynctask_id']
	list_filter = ['project_phase','start_datetime','project_completion_percentage']
	search_fields = ['id','project__client_name','project_phase','project_completion_percentage','asynctask_id','project__id']
	readonly_fields = ['project_id','project_completion_percentage','project_phase','asynctask_id','project','start_datetime','last_updated_date']

	fieldsets=[
				('ProjectStatus Info',{'fields':['project','project_id','start_datetime','last_updated_date']}),

				('Project Phase Status', {'fields': ('project_phase','project_completion_percentage'),}),
				
				('Async Task Info', {
					# 'classes': ('collapse',),
					'fields': ('asynctask_id',),
				}),
				]		

	class Meta:
		model = ProjectStatus
		
	def project_id(self, obj):
		return obj.project.id
admin.site.register(ProjectStatus, ProjectStatusAdmin)