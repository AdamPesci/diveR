"""
:Author(s) Adam Camer-Pesci:
    
Class for file loading interface
This file contains the various implementations used to load different file types.
"""
from abc import ABC, abstractmethod
import os
import re
from datetime import datetime
import rpy2.robjects.packages as rpackages


class FileLoader(ABC):
    """
Base class for loading different types of files
"""
    @abstractmethod
    def load(self, file_paths):
        pass


class CSVLoader(FileLoader):

    def load(self, file_paths):
        """
    load .csv filetypes
    :param filepaths: list:
    list of 1-n filepath strings.

    :returns:
        :csv_files:
            a list of dataframes representing dive profiles
        :csv_paths:
            a list of strings representing valid filepaths
    """
        # get rpy2 utils
        utils = rpackages.importr('utils')
        csv_files = []
        csv_paths = []
        # if input is single filepath, make it a list
        if not type(file_paths is list):
            file_paths = [file_paths]
        # iterate through list of files appending to list of dataframes
        for path in file_paths:
            valid = False
            # check csv is correct format
            with open(path, 'r', encoding='utf-8-sig') as file:
                first_line = file.readline()
                # first line should start with time and end with depth split by a comma
                if re.search('^TIME,DEPTH$', first_line.upper()):
                    valid = True

            # if file is valid, read it to dataframe and store valid path
            if (path.endswith('.csv') and valid == True):
                dataf = utils.read_csv(str(path))
                csv_files.append(dataf)
                csv_paths.append(path)
            # if given bad filetype, file is skipped and written to log
            else:
                if not os.path.isdir('./logs'):
                    os.mkdir('./logs')
                fw = open('./logs/FileLoader.log', 'a')
                try:
                    fw.write(datetime.now().strftime('%H:%M:%S') +
                             " " + path + " is invalid file. " + "check_of_first_line= " + first_line + '\n')
                except IOError:
                    print("file not accessible")
                finally:
                    fw.close()
        return csv_files, csv_paths


class ANSLoader(FileLoader):

    def load(self, file_paths):
        """
    load .ans filetypes
    """
        # TODO : Implement .ans loading functionality
        return
