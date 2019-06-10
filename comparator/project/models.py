# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import *
from django.utils import timezone
from django.db import models
from django.contrib.auth import models as auth_model

# Create your models here.

class Project(models.Model):
	project_name = models.CharField(max_length=1000)
	creation_date =models.DateField(auto_now=False, auto_now_add=True)
	last_updated_date = models.DateTimeField(auto_now=True, auto_now_add=False)
	start_date = models.DateField('Project start date')
	end_date = models.DateField('Project end date')

	def __str__(self):
		return self.project_name

	def is_active(self):
		date_today = date.today()
		return date_today < self.end_date


class ProjectUser(models.Model):
	project = models.ForeignKey(Project, on_delete = models.CASCADE)
	user = models.ForeignKey(auth_model.User, on_delete = models.CASCADE)
	creation_date =models.DateField(auto_now=False, auto_now_add=True)
	last_updated_date = models.DateField(auto_now=True, auto_now_add=False)