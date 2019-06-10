import ConfigParser
import os
# print os.getcwd()


class Config:
    def __init__(self,config_file_name):
        if os.path.exists(config_file_name):
            self.config = ConfigParser.ConfigParser()
            self.config.read(config_file_name)
        else:
            #print 'no configuration file'
            pass

    def get_config_value(self,section,key):
        return self.config.get(section, key)

