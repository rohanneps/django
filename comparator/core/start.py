from core.loader.load import TaskLoader
from core.emailer.emailer import send_email
from core.database_handler.database_handler import DatabaseHandler
import logging
import os
import MySQLdb
from engine.models import ProjectComparator
from django.conf import settings
from django.contrib.auth.models import User
from project.models import Project



def logger_conf():
    log_directory = 'logs'
    output_dir = 'Comparator_Output'

    if not os.path.exists (log_directory):
        os.makedirs (log_directory)

    if not os.path.exists (output_dir):
        os.makedirs (output_dir)

    logging.basicConfig (filemode = 'a')
    logger = logging.getLogger (__name__)
    logger.setLevel (logging.INFO)

    # File handler
    handler = logging.FileHandler (os.path.join (log_directory, 'Comparator_Log.log'))
    handler.setLevel (logging.INFO)

    # Logging Format
    formatter = logging.Formatter ('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter (formatter)

    logger.addHandler (handler)

    return logger, output_dir



def start_core(project_comparison_id):
    logger, output_dir = logger_conf()

    # type = 'core'
    type = 'db'

    project_comparator = ProjectComparator.objects.get(id=project_comparison_id)
    
    project_output_dir = os.path.join (output_dir,str(project_comparator.project))
    
    if not os.path.exists (project_output_dir):
        # print 'dir not created'
        os.makedirs (project_output_dir)

    project_input_dir = os.path.join (settings.MEDIA_ROOT,str(project_comparator.project))
    project_run_type = project_comparator.run_priority
    project_max_error_threshold = project_comparator.error_count

    logger.info('ComparisonId = {} :  max error => {}'.format(project_comparison_id,project_max_error_threshold))
    logger.info('ComparisonId = {} :  project_run_type => {}'.format(project_comparison_id,project_run_type))

    if project_comparator.project_status != ProjectComparator.ERR:
        
        # try:
        task_loader = TaskLoader (logger,project_input_dir,project_output_dir, project_comparison_id, type,project_run_type,project_max_error_threshold)
        #temporarily closing connection since comparison task will make database idle.
        from django.db import connection
        connection.close()
        task_loader.start_task()
        total_error_count = task_loader.stop_task()
        
        #Updating project status as completed
        project_comparator.project_status = ProjectComparator.COM
        project_comparator.error_count = total_error_count
        logger.info('ComparisonId = {} : Completed Comparison  with total error => {} '.format(project_comparison_id,total_error_count))
            


        # except Exception as exception:
        #     #Updating project status as Failed
        #     project_comparator.project_status = ProjectComparator.ERR
        #     logger.info('ComparisonId = {} : Has exception --> {}'.format(project_comparison_id,exception))
        #     logger.info('ComparisonId = {} : Failed comparison '.format(project_comparison_id))
        
        # finally:
        # Saving Project status
        try:
            project_comparator.save()
        except MySQLdb.OperationalError:
            # Handling for sql timeout error.
            logger.info('ComparisonId = {} : Status updated with Database '.format(project_comparison_id))
            db_settings = settings.DATABASES['default']
            databaseHandler = DatabaseHandler(db_settings,project_comparison_id)
            databaseHandler.save_project_status(project_comparator.project_status,project_comparator.error_count)
            databaseHandler.close_database()


        # Sending email for immediate reporting.
        if(project_run_type == 1):
            user_id = project_comparator.user_id
            project_name = Project.objects.get(id = project_comparator.project_id)

            email = User.objects.get(id = user_id).email

            scrapper_report = os.path.join(output_dir, str(project_name), project_comparator.project_scrapper_output_file)
            comparison_report = os.path.join(output_dir, str(project_name), project_comparator.project_report_file)

            try:
                send_email(email, project_max_error_threshold,str(project_name), scrapper_report, comparison_report)
                # logger.info('ComparisonId = {} : Email sent for '.format(project_comparison_id))
            except Exception:
                logger.info('ComparisonId = {} : Email not sent for '.format(project_comparison_id))
    else:
        logger.info('ComparisonId = {} : Comparison not started for project as it contains some file issue.'.format(project_comparison_id))