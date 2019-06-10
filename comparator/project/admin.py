# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Project,  ProjectUser


# Register your models here.
class ProjectAdmin(admin.ModelAdmin):
	list_display = ('project_name','start_date','end_date','last_updated_date','is_active')
	list_filter = ('project_name',)
	search_fields = ['project_name']

class ProjectUserAdmin(admin.ModelAdmin):
	list_display = ('project','user','last_updated_date')
	list_filter = ('project','user')
	search_fields = ['project__project_name','user__username']


# Registering Modules to the admin panel
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectUser,ProjectUserAdmin)
