# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth import models as auth_model
from project.models import Project

# Create your models here.

class ProjectComparator(models.Model):
    RUN = 'Running'
    COM = 'Completed'
    ERR = 'FAILURE'

    project = models.ForeignKey(Project, on_delete = models.CASCADE,editable=False)
    user = models.ForeignKey(auth_model.User, on_delete = models.CASCADE,editable=False)
    project_url_file = models.CharField(max_length=1000,editable=False)
    project_xpath_file = models.CharField(max_length=1000,editable=False)
    project_platform_import_file = models.CharField(max_length=1000,editable=False)
    PROJECT_STATUS = (
        (RUN, 'Running'),
        (COM, 'Completed'),
        (ERR, 'FAILURE'),
    )
    project_status = models.CharField(
        max_length=10,
        choices=PROJECT_STATUS,
        # default=1,
    )
    run_priority = models.IntegerField (editable = False)
    start_time = models.DateTimeField (auto_now = True, auto_now_add = False, editable = False)
    error_count = models.IntegerField (default = 0, editable = False)
    project_scrapper_output_file = models.CharField (max_length = 1000, editable = False)
    project_report_file = models.CharField (max_length = 1000, editable = False)

    def __str__(self):
        return str(self.project)

    def comparison_type(self):
        if self.run_priority==2 :
            return ('Bulk Reporter')
        else:
            return ('Immediate Reporter')


class ProjectXpath(models.Model):
    project = models.ForeignKey(Project, on_delete = models.CASCADE,editable=False)
    project_comparator = models.ForeignKey(ProjectComparator, on_delete = models.CASCADE,editable=False)
    xpath = models.CharField(max_length=1000,editable=False)
    field_name = models.CharField(max_length=1000,editable=False)
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.xpath

class ProjectUrl(models.Model):
    project = models.ForeignKey(Project, on_delete= models.CASCADE,editable=False)
    project_comparator = models.ForeignKey(ProjectComparator, on_delete = models.CASCADE,editable=False)
    primary_identifier = models.CharField(max_length=1000,editable=False)
    url = models.CharField(max_length=1000,editable=False)
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.url
