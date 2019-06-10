from core.utils.config import Config
from core.scrapper.scrapper import Scrapper
from core.comparator.comparator import Comparator
from engine.models import ProjectComparator
from core.base.baseTask import BaseTask
from core.reporter.reporter import Reporter
import os


class TaskLoader(BaseTask):

    def __init__(self,logger,project_input_dir,output_dir, process_id, core_call_type,comp_type,max_error_threshold):
        self.logger = logger
        self.project_input_dir = project_input_dir
        self.output_dir = output_dir

        self.config = Config ('core/config.ini')
        project_comparator_obj = ProjectComparator.objects.get(id=process_id)
        # print os.path.join(self.project_input_dir, project_comparator_obj.project_platform_import_file)
        self.process_id = process_id

        if core_call_type == 'core':
            #get input files
            self.platform_import_file = self.config.get_config_value('input_files','platform_import_file')
            self.url_to_scrape_file = self.config.get_config_value('input_files','url_to_scrape_file')
            self.field_to_xpath_file = self.config.get_config_value('input_files','field_to_xpath_file')
            #get output files
            self.scrapped_data_file = self.config.get_config_value('output_files','scrapped_output_csv')
            self.comparision_report_file = self.config.get_config_value('output_files','comparison_report')

        elif core_call_type == 'db':
            try:
                project_comparator_obj = ProjectComparator.objects.get(id=process_id)
                #get input files
                # print project_comparator_obj
                self.platform_import_file = os.path.join(self.project_input_dir, project_comparator_obj.project_platform_import_file)
                self.url_to_scrape_file = os.path.join(self.project_input_dir, project_comparator_obj.project_url_file)
                self.field_to_xpath_file = os.path.join(self.project_input_dir, project_comparator_obj.project_xpath_file)
                #get output files
                self.scrapped_data_file = project_comparator_obj.project_scrapper_output_file
                self.comparision_report_file = project_comparator_obj.project_report_file
                self.comp_type = comp_type
                self.max_error_threshold = max_error_threshold
            except Exception:
                # print '>>>>>>More than one record exists for %s' % process_id, '>>>>>>
                pass

    def start_task(self):
        #Start Scrapping Task

        if (self.comp_type == 1):
            # Immediate comparison Task
            self.reporter = Reporter(self.process_id,self.url_to_scrape_file,self.field_to_xpath_file,self.platform_import_file,self.scrapped_data_file,self.comparision_report_file,self.logger,self.output_dir,self.comp_type,self.max_error_threshold)
            self.reporter.start_task()
            self.reporter.stop_task()
            self.total_error_count = self.max_error_threshold

        else:
            # Bulk comparison Task
            self.scrapper = Scrapper(self.process_id,self.url_to_scrape_file,self.field_to_xpath_file,self.scrapped_data_file,self.logger,self.output_dir,self.comp_type)
            self.logger.info('*****************************')
            self.scrapper.start_task()
            self.scrapper.stop_task()
            self.logger.info('*****************************')


            #Comparison task
            if (os.path.exists(os.path.join(self.output_dir,self.scrapped_data_file))):
                self.comparator = Comparator(self.process_id,self.platform_import_file,self.scrapped_data_file,self.comparision_report_file,self.logger,self.output_dir,self.scrapper)
                self.logger.info( '*****************************')
                self.comparator.start_task()
                self.total_error_count = self.comparator.stop_task()
                self.logger.info('*****************************')
            else:
                self.logger.info('ComparisonId = {} : Output csv missing. Comparison Not performed!!'.format(self.process_id))

    def stop_task(self):
        self.logger.info('*****************************')
        self.logger.info('ComparisonId = {} : Closing Comparator!!!!'.format(self.process_id))
        self.logger.info('*****************************')
        return self.total_error_count