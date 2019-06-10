from core.base.baseTask import BaseTask
from requests.exceptions import MissingSchema,ConnectionError
import pandas as pd
from selenium import webdriver
import os
import csv
import logging
from lxml import html
import requests
from selenium.common.exceptions import WebDriverException,TimeoutException,NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import collections

class Scrapper(BaseTask):

    def __init__(self,process_id,url_to_scrape_file,field_to_xpath_file,output_file,logger,output_dir,comp_type):
        self.process_id = process_id
        self.url_to_scrape_file_df = pd.read_csv(url_to_scrape_file,dtype=object)
        self.field_identifier_file_df = pd.read_csv(field_to_xpath_file,dtype=object)
        self.output_file = output_file
        self.file_xpath_col_list = self.field_identifier_file_df.columns.tolist()
        self.logger = logger
        self.output_dir = output_dir
        self.comp_type = comp_type
        
        # get dictionary from field and xpath
        # Unordered dictionary
        # self.field_identifier_dict = self.field_identifier_file_df.set_index(self.file_xpath_col_list[0])[self.file_xpath_col_list[1]].to_dict()
        #Ordered Dictionary
        self.field_identifier_dict = collections.OrderedDict(zip(list(self.field_identifier_file_df[self.file_xpath_col_list[0]]),list(self.field_identifier_file_df[self.file_xpath_col_list[1]])))
        

        # self.driver = webdriver.Firefox()
        self.driver = webdriver.PhantomJS()
        # self.scrapped_data_file = pd.DataFrame(columns = [self.url_to_scrape_file_df.columns.tolist()[0]]+list(self.field_identifier_dict.keys()))
        #Extracting only Field names and not tags
        self.scrapped_data_file = pd.DataFrame(columns = [self.url_to_scrape_file_df.columns.tolist()[0]]+map(lambda x:x.split('|')[0],self.field_identifier_dict.keys()))
        self.page_not_found_list = []
        self.invalid_url_list = []
        self.connection_issue_list = []

    def start_task(self):
        self.logger.info('ComparisonId = {} : Starting Scrapping task!!'.format(self.process_id))

        try:
            self.url_to_scrape_file_df.fillna('', inplace=True)
            self.url_to_scrape_file_df.apply(self.scrape_url,axis =1)    
        except Exception:
            # Incase srapping is halted somewhere, the scrapped details upto that point is published.
            self.stop_task()

    def stop_task(self):
        self.logger.info('ComparisonId = {} : Scrapping task completed!!'.format(self.process_id))
        self.logger.info('ComparisonId = {} : Scrapping details written to file --> {}'.format(self.process_id,os.path.join(self.output_dir,self.output_file)))
        self.scrapped_data_file.to_csv(os.path.join(self.output_dir,self.output_file),index=False,quoting=csv.QUOTE_ALL)
        try:
            self.driver.quit()
        except Exception as driverClosed:
            pass

    def check_url(self,url):
        if 'http://' not in url and 'https://' not in url:
            url = 'http://'+url
        return url

    # For each url provided
    def scrape_url(self,row):
        primary_id = row[row.index.tolist()[0]]
        url = row[row.index.tolist()[1]]
        # Data is stored in list for each row
        row_data_list = [primary_id]
        bypass_row = False

        # self.logger.info('SKU: {} '.format(primary_id))
        #checking if url is correct
        url = self.check_url(url)
        # self.logger.info('For url: {} '.format(url))
        bypass_row = False
        #Checking to see if page doesn't exist
        try:
            self.page_request = requests.get(url)

        #handling of connection issue
        except ConnectionError as e:
            row_data_not_found_list = ['Error!! Connection Issue.' for x in range(1,len(self.scrapped_data_file.columns.tolist()))]
            self.logger.info('Connection issue for id {} with url {} '.format(primary_id,url))
            row_data_list = row_data_list + row_data_not_found_list
            self.connection_issue_list.append(primary_id)
            bypass_row = True

        #handling of invalid url
        except Exception:
            # print url
            row_data_not_found_list = ['Error!! Invalid url.' for x in range(1,len(self.scrapped_data_file.columns.tolist()))]
            self.logger.info('Invalid url for id {} with url {} '.format(primary_id,url))
            row_data_list = row_data_list + row_data_not_found_list
            self.invalid_url_list.append(primary_id)
            bypass_row = True

        if not bypass_row:
            if self.page_request.status_code == 404:
                # print url
                row_data_not_found_list = ['404 Error!! Page Not Found.' for x in range(1,len(self.scrapped_data_file.columns.tolist()))]
                row_data_list = row_data_list + row_data_not_found_list
                self.page_not_found_list.append(primary_id)
            else:
                try:
                    self.driver.get(url)
                    wait = WebDriverWait(self.driver, 30)
                    # Waiting maximum of 30 seconds fro ajax, javascipt calls to be executed.
                    wait.until(lambda driver: self.driver.execute_script("return jQuery.active == 0"))
                except WebDriverException as e:
                    if 'Reached error page' in e.message:
                        pass
                #Iterating over the field names
                for field_name in self.field_identifier_dict:
                    #Getting xpath for field
                    element_extraction_identifier = self.field_identifier_dict[field_name]

                    #Checking if any flag exists
                    requires_html_tag = None
                    if '|' in field_name:
                        requires_html_tag = field_name.split('|')[1]

                    try:
                        scrapped_data = self.find_element(element_extraction_identifier,'xpath',requires_html_tag)
                    except:
                        scrapped_data = 'Xpath Not matched'
                        self.logger.info('ComparisonId = {} : [{}]--- has error for field --> {} with xpath ---> {}'.format(self.process_id,primary_id,field_name,element_extraction_identifier))
                    row_data_list.append(scrapped_data)
        # print row_data_list
        # self.logger.info('row_data_list-->'.format(row_data_list))
        if self.comp_type == 1:
            return row_data_list
        else:
            self.scrapped_data_file = self.scrapped_data_file.append(pd.Series(row_data_list,index = self.scrapped_data_file.columns.tolist()),ignore_index=True)


    def find_element(self,element_extraction_identifier, type,requires_html_tag):
        if type =='xpath':

            try:
                page_element = self.driver.find_element_by_xpath(element_extraction_identifier)
                # self.logger.info(element_extraction_identifier)
                # self.logger.info('inside try for xpath')
            except NoSuchElementException:

                # Waiting for elements to be found
                # self.logger.info('no such element')
                try:
                    page_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, element_extraction_identifier)))
                    # self.logger.info('inside 2nd try for xpath')
                except TimeoutException:
                    # self.logger.info('Timeout for xpath')
                    raise Exception('Xpath not found!!')

            if str(page_element.tag_name) == 'select':
                option_list = []
                for option in page_element.find_elements_by_tag_name("option"):
                    option_list.append(option.text)
                xpath_scrapped_data = ';;'.join(option_list)
                
            elif str(page_element.tag_name) == 'img':
                image_src_name = page_element.get_attribute('src')
                image_name = str(image_src_name.rsplit('/')[-1])
                xpath_scrapped_data = str('/'+image_name)

            else:

                #Getting inner html when flag is set
                if requires_html_tag=='requires_html_tag':
                    xpath_scrapped_data = page_element.get_attribute('innerHTML').encode('utf8')

                else:
                    #Handling for special characters.
                    try:
                        xpath_scrapped_data = str(page_element.text)
                    except UnicodeEncodeError:
                        xpath_scrapped_data = page_element.text.encode('utf8')
                # self.logger.info('xpath_scrapped_data-->' +xpath_scrapped_data)

                # For cases, where PhantomJS doesn't catch the hidden element
                if xpath_scrapped_data =='':
                    xpath_scrapped_data = page_element.get_attribute('textContent').strip().replace('  ','\n')
                    #If still no found then we will use request, lxml modules
                    if xpath_scrapped_data =='':
                        xpath_scrapped_data = self.find_element_from_request(element_extraction_identifier)

                #Checking for attribute options
                if "\n" in xpath_scrapped_data:
                    xpath_scrapped_data = self.check_for_additional_attributes(xpath_scrapped_data)
                
                    
            return xpath_scrapped_data

    
    def check_for_additional_attributes(self,xpath_scrapped_data):
        option_list = []
        for option in xpath_scrapped_data.splitlines():
            option_list.append(str(option))
        xpath_scrapped_data = ';;'.join(option_list)
        return xpath_scrapped_data
     

    def find_element_from_request(self, element_extraction_identifier):
        xml_tree = html.fromstring(self.page_request.content)
        xpath_tree_element = xml_tree.xpath(element_extraction_identifier)
        if len(xpath_tree_element) != 0 :
            return xpath_tree_element[0].text
        else: 
            return ''
