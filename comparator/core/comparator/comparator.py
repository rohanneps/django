from core.base.baseTask import BaseTask
import pandas as pd
import os
import csv
import logging

class Comparator(BaseTask):

    def __init__(self,process_id,platform_import_file,scrapped_data_file,comparision_report_file,logger,output_dir,scrapper_object):
        self.process_id = process_id
        self.logger = logger
        self.output_dir = output_dir
        self.platform_import_file = pd.read_csv(platform_import_file,dtype=object)
        self.platform_import_file.fillna(value='', inplace=True)
        self.scrapped_data_file = pd.read_csv(os.path.join(self.output_dir,scrapped_data_file),dtype=object)

        self.logger = logger
        self.output_dir = output_dir

        self.report_csv = pd.DataFrame(columns = self.platform_import_file.columns.tolist())
        self.comparision_report_file = comparision_report_file
        self.page_not_found_list = scrapper_object.page_not_found_list
        self.invalid_url_list = scrapper_object.invalid_url_list
        self.connection_issue_list = scrapper_object.connection_issue_list
        self.comp_type = scrapper_object.comp_type
        self.total_error_count = 0

    def start_task(self):
        try:
            self.logger.info('ComparisonId = {} : Starting comparision task'.format(self.process_id))
            self.platform_import_file.fillna('',inplace=True)
            self.platform_import_file.apply(self.compare_data,axis=1)
                # getting extra scrapped row details
            self.get_extra_scrapped_rows()
        except Exception:
            # Incase comparison is halted somewhere, the comparison details upto that point is published.
            self.stop_task()


    def stop_task(self):
        self.logger.info('ComparisonId = {} : Comparision task completed'.format(self.process_id))
        report_file_name = os.path.join(self.output_dir,self.comparision_report_file)
        self.report_csv.to_csv(report_file_name,index=False,quoting=csv.QUOTE_ALL)
        self.logger.debug('ComparisonId = {} : Report generated to file {}'.format(self.process_id,report_file_name))
        return self.total_error_count

    # Data comparison for each row
    def compare_data(self,row):
        primary_id_column = str(row.index.tolist()[0])
        primary_id = row[primary_id_column]
        # Report is stored in list for each row
        row_report = [primary_id]

        # self.logger.setLevel(logging.DEBUG)
        self.logger.info('ComparisonId = {} : Comparing for {}'.format(self.process_id,primary_id))
        # self.logger.setLevel(logging.INFO)
        if primary_id in self.page_not_found_list:
            self.logger.info('ComparisonId = {} : [{}] has url 404 error'.format(self.process_id,primary_id))
            row_data_not_found_list = ['404 Error!! Page Not Found.' for x in range(1,len(self.platform_import_file.columns.tolist()))]
            row_report = row_report + row_data_not_found_list
            self.report_csv = self.report_csv.append(pd.Series(row_report,index = self.platform_import_file.columns.tolist()),ignore_index=True)
            self.total_error_count += 1

        elif primary_id in self.connection_issue_list:
            self.logger.info('ComparisonId = {} : [{}] has connection issue'.format(self.process_id,primary_id))
            row_data_not_found_list = ['Error!! Connection Issue.' for x in range(1,len(self.platform_import_file.columns.tolist()))]
            row_report = row_report + row_data_not_found_list
            self.report_csv = self.report_csv.append(pd.Series(row_report,index = self.platform_import_file.columns.tolist()),ignore_index=True)
            self.total_error_count += 1
            
        elif primary_id in self.invalid_url_list:
            self.logger.info('ComparisonId = {} : [{}] has invalid URL error'.format(self.process_id,primary_id))
            row_data_not_found_list = ['Error!! Invalid url.' for x in range(1,len(self.platform_import_file.columns.tolist()))]
            row_report = row_report + row_data_not_found_list
            self.report_csv = self.report_csv.append(pd.Series(row_report,index = self.platform_import_file.columns.tolist()),ignore_index=True)
            self.total_error_count += 1
        else:
            try:
                scrapped_data_row = self.scrapped_data_file[self.scrapped_data_file[self.scrapped_data_file.columns.tolist()[0]] == primary_id].iloc[0]
                if len(scrapped_data_row)>0:
                    for column in self.platform_import_file.columns.tolist():
                        if column != primary_id_column:
                            # Stripping value only incase of String
                            try:
                                platform_column_value = row[column].strip()
                            except Exception:
                                platform_column_value = row[column]
                            try:
                                scrapped_column_data = scrapped_data_row[column]

                                if scrapped_column_data:
                                    # Comparison for attribute option data
                                    if ';;' in scrapped_column_data:
                                        row_report = self.compare_attribute_options(scrapped_column_data,row_report,platform_column_value)
                                    else:
                                        if type(scrapped_column_data) == str:
                                            scrapped_column_data = scrapped_column_data.strip()
                                        if platform_column_value == scrapped_column_data:
                                            row_report.append('Pass!! Data is same.')
                                        else:
                                            if platform_column_value=='' and scrapped_column_data=='Xpath Not matched':
                                                row_report.append('Data field is empty.')
                                            else:
                                                row_report.append('Error!! Data not matched.')
                                                self.total_error_count +=1
                                else:
                                    row_report.append('Data is not scrapped!')
                                    self.total_error_count +=1
                            except KeyError:
                                row_report.append('Column missing in provided fields to scrape')
                                self.total_error_count +=1
                else:
                    self.total_error_count +=1
                    row_report.append('Row missing scrapped data')                    
            except IndexError:
                missing_report = ['Product not present in provided url' for x in range(1,len(self.platform_import_file.columns.tolist()))]
                row_report = row_report+(missing_report)
                self.total_error_count +=1
            # print row_report
            if self.comp_type == 1:
                return row_report
            else:
                self.report_csv = self.report_csv.append(pd.Series(row_report,index = self.platform_import_file.columns.tolist()),ignore_index=True)

    #Appending additional scrapped url
    def get_extra_scrapped_rows(self):
        all_scraped_primary_identifier = set(self.scrapped_data_file.ix[:,0].tolist())
        all_splatform_primary_identifier = set(self.platform_import_file.ix[:,0].tolist())
        extra_scrapped_primary_ids = all_scraped_primary_identifier - all_splatform_primary_identifier
        for extra_primary_id in extra_scrapped_primary_ids:
            extra_row_data_all_columns = [extra_primary_id]
            if extra_primary_id in self.page_not_found_list:
                self.logger.info('ComparisonId = {} : [{}] has url error'.format(self.process_id,extra_primary_id))
                extra_row_data = ['404 Error!! Page Not Found., Row not present in platform file' for x in range(1,len(self.platform_import_file.columns.tolist()))]
            else:
                extra_row_data = ['Row not present in platform file' for x in range(1,len(self.platform_import_file.columns.tolist()))]
            extra_row_data_all_columns = extra_row_data_all_columns + extra_row_data
            self.total_error_count +=1
            self.report_csv = self.report_csv.append(pd.Series(extra_row_data_all_columns,index = self.platform_import_file.columns.tolist()),ignore_index=True)            

    # Comparison for attribute options
    def compare_attribute_options(self,scrapped_column_data,row_report,column_value):
        scrapped_column_data_list = scrapped_column_data.split(';;')
        column_value_list = column_value.split(';;')
        extra_options_in_scrapped_data = list(set(scrapped_column_data_list)-set(column_value_list))
        # print extra_options_in_scrapped_data
        extra_options_in_platform_data = list(set(column_value_list)-set(scrapped_column_data_list))
        # print extra_options_in_platform_data
        total_additional_option_list = set(extra_options_in_scrapped_data+extra_options_in_platform_data)
        if len(total_additional_option_list) ==0:
            row_report.append('Pass!! Data is same.')
        else:
            additional_option = ';;'.join(total_additional_option_list)
            row_report.append('Data option mismatch. Options not present in both file -'+additional_option)
            self.total_error_count +=1
        return row_report