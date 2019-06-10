from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProjectComparator, ProjectUrl, ProjectXpath
import pandas as pd
import os
import logging
# from core.start import main
from engine.async_comparator_task import comparator_comparision
from django.contrib import messages
from django.http import request

comp_logger = logging.getLogger(__name__)


# Project urls entry reciever 
# Will be triggered after Project Comparator instance is saved

@receiver(post_save, sender=ProjectComparator,dispatch_uid='my_unique_url_reciever_identifier')
def enter_project_comparator_url_details(sender, instance, created, **kwargs):
    def parse_url_file(row):
            primary_id = row[row.index.tolist()[0]]
            row_url = row[row.index.tolist()[1]]
            new_project_url = ProjectUrl(project=project,project_comparator=project_comparator,primary_identifier=primary_id,url=row_url)
            project_url_object_list.append(new_project_url)
            # new_project_url.save()
    if created:
        # getting project comparator onject from sender
        global project_url_object_list
        project_url_object_list = []
        project_comparator = instance
        project = project_comparator.project
        project_name = project.project_name
        project_url_file = project_comparator.project_url_file

        url_df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,project_name,project_url_file))
        url_df.fillna('',inplace=True)
        #Handling for issue in url file
        try:
            url_df.apply(parse_url_file, axis=1)

            # bulk insert into database
            ProjectUrl.objects.bulk_create(project_url_object_list)
            comp_logger.info('Project:[{}]  --> Url details inserted'.format(project_comparator.id))
        except Exception:
            comp_logger.info('Project:[{}]  --> Issue in URL File'.format(project_comparator.id))
            project_comparator.project_status = ProjectComparator.ERR
            project_comparator.save()




# Project xpaths entry reciever
# Will be triggered after Project Comparator instance is saved
@receiver(post_save, sender=ProjectComparator,dispatch_uid='my_unique_xpath_reciever_identifier')
def enter_project_comparator_xpath_details(sender, instance, created, **kwargs):
    def parse_xpath_file (row):
        field_name = row[row.index.tolist()[0]]
        xpath = row[row.index.tolist()[1]]
        new_project_xpath = ProjectXpath (project = project,project_comparator=project_comparator, field_name = field_name, xpath = xpath)
        # new_project_xpath.save()
        project_xpath_object_list.append (new_project_xpath)

    if created:
        # getting project comparator onject from sender
        global project_xpath_object_list
        project_xpath_object_list = []
        project_comparator = instance
        project = project_comparator.project
        project_name = project.project_name
        project_xpath_file = project_comparator.project_xpath_file

        xpath_df = pd.read_csv (os.path.join (settings.MEDIA_ROOT,project_name, project_xpath_file))
        xpath_df.fillna('',inplace=True)
        # Inserting xpaths and starting comparison where URL file doesn't have issue.
        #Handling for issue in xpath file
        try:
            xpath_df.apply(parse_xpath_file, axis = 1)
            # bulk insert into database
            ProjectXpath.objects.bulk_create(project_xpath_object_list)
            comp_logger.info('Project:[{}]  --> Xpath details inserted'.format(project_comparator.id))
            
            # comparator core start
            #Async comparator task called from here
            comparator_comparision.delay(project_comparator.id)
        except Exception:
            comp_logger.info('Project:[{}]  --> Issue in Xpath File'.format(project_comparator.id))
            project_comparator.project_status = ProjectComparator.ERR
            project_comparator.save()
        
