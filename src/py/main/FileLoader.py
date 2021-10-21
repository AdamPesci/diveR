"""
:Author(s) Adam Camer-Pesci, Augustine Italiano:
    
Class for file loading interface
This file contains the various implementations used to load different file types.

"""
from abc import ABC, abstractmethod
import os
import re
import sys
from datetime import datetime
import rpy2.robjects.packages as rpackages
from rpy2.robjects.vectors import FloatVector
import numpy as np
from rpy2 import robjects
from rpy2.robjects import FloatVector


class FileLoader(ABC):
    """
Base class for loading different types of files
"""
    @abstractmethod
    def load(self, file_dir, file_paths):
        pass

    def write_log(self, path, message):
        """
        error log writing method

        :param path: str: path of associated file
        :param message: str: message to write to log

    """
        if not os.path.isdir('./logs'):
            os.mkdir('./logs')

        fw = open('./logs/FileLoader.log', 'a')
        try:
            fw.write(datetime.today().strftime('%Y-%M-%d') + ' ' + datetime.now().strftime('%H:%M:%S') +
                     ' - ' + path + ': is invalid file. ' + message)
        except IOError:
            sys.stderr.write('Could not access log file/folder')
        finally:
            fw.close()


class CSVLoader(FileLoader):

    def load(self, file_dir, file_paths):
        """
    load .csv filetypes

    :param filepaths: list: list of 1-n filepath strings.

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
            path = file_dir + path
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
                self.write_log(path, 'check-first-line: ' + str(first_line))

        return csv_files, csv_paths


class ANSLoader(FileLoader):

    def load(self, file_dir, file_paths):
        """
    load .ans filetypes

    :param file_paths: list: list of 1-n filepath strings.

    :returns:
        :r_fames_list:
            a list of dataframes representing just the ans files time and depth time stamps (R compatiable)
        :frames_path_list:
            a list of paths that were valid and used in creating dataframes 
        :gas_list:
            a list of gas codes and depths containing the gas changes during the dive 
        :extra_calc_list:
            a list of Strings for each dive that have the dcs incident report and comments about it

    """
        valid = False
        frames_path_list = []  # valid file names
        r_frames_list = []  # time (mins), depth
        gas_list = []  # Gas code, time
        extra_calc_list = []  # Gas code, dcs hit, probability [t1, t2, !comment]
        for path in file_paths:
            # if file is valid, read it to dataframe and store valid path
            r_frame = robjects.r['data.frame']
            if (path.endswith('.ans') or path.endswith('.txt')):
                ans = open(file_dir + path)
                # get the 3rd line
                line = ans.readline()
                second_line = ans.readline()
                third_line = ans.readline()
                ans.close()
                if re.search('^0.00', third_line.upper()):
                    valid = True
                if(valid):
                    ans = open(file_dir + path)
                    frames_path_list.append(path)
                    rows = ans.readlines()
                    # define the two numpy matrix
                    data_frame = np.zeros((len(rows)-3, 2), dtype=np.float32)
                    gas_frame = np.zeros((len(rows)-3, 2), dtype=np.float32)
                    # keeping track of the file line for the extra calc info
                    file_line = -1
                    # keeping track of the rows that are written for time and depth
                    i = 0
                    for line in rows:
                        elements = line.split(",")
                        file_line = file_line + 1
                        # Gas code, dcs hit, probability [t1, t2, !comment]
                        if (file_line == 1):
                            # this will be dynamic in size, and simply can be appended to the end of the dive profile output
                            # sometimes the formatting of the ans will have a comma with no text, thus get ride of it
                            if ' \n' in elements:
                                elements.remove(' \n')

                            # stuff to get diver ID from file
                            diver_info = rows[0].split(',')
                            diver_info = str(diver_info).split(' ')
                            # clean the string
                            diver_info[0] = diver_info[0].replace('[', '')
                            diver_info[0] = diver_info[0].replace('\'', '')
                            # only send over the two elements
                            diver_ids = [diver_info[0], diver_info[1]]
                            extra_dic = {
                                'headers': ['GasCode', 'DCSExposures', 'Outcome', 'T1', 'T2', 'Comment', 'DiveID', 'DiverID'],
                                'values': elements, 'diver_ids': diver_ids}
                            extra_calc_list.append(extra_dic)
                        elif ((len(elements)-1 == 4 or (len(elements)-1 == 5) and (file_line != 0 or file_line != 1 or file_line != -1))):  # gas switch
                            # time stamp in the dive, without the gas change
                            data_frame[i][0] = float(elements[0])*60
                            data_frame[i][1] = str(
                                (float(elements[1]) * 0.3048))
                            # time in the dive with the gas code
                            gas_frame[i][0] = float(elements[0])
                            gas_frame[i][1] = elements[2]
                            i = i + 1
                        # time and depth
                        elif (len(elements)-1 == 2 and '!ND:' not in elements[0] and '!EOD:' not in elements[0] and file_line != 0):
                            # the syntax is: data_frame[time(mins), depth(metres)]
                            data_frame[i][0] = float(elements[0])*60
                            data_frame[i][1] = str(
                                (float(elements[1]) * 0.3048))
                            # add one to the i counter to note we have appended a valid line to the data_frame
                            i = i + 1
                        # End of the actual file and not the start of the file
                        elif (len(elements) - 1 == 1 and i != 0):
                            # remove any 0's
                            data_frame = data_frame[~np.all(
                                data_frame == 0, axis=1)]
                            gas_frame = gas_frame[~np.all(
                                gas_frame == 0, axis=1)]

                            # create a frame and append it to the list
                            r_frames_list.append(r_frame(time=FloatVector(data_frame[:, 0].tolist()),
                                                         depth=FloatVector(data_frame[:, 1].tolist())))
                            gas_list.append(r_frame(time=FloatVector(gas_frame[:, 0].tolist()),
                                                    code=FloatVector(gas_frame[:, 1].tolist())))
                    ans.close()
                else:
                    self.write_log(
                        path, 'check-first-lines:\n' + line + second_line + third_line)
        return r_frames_list, frames_path_list, gas_list, extra_calc_list

    def generate_gas_list(self, gas_data):
        """
    generate gas list from .ans file gas codes

    :param gas_data: dataframe: dataframe created by ans_loader.load. Dataframe contains times and gas codes

    :returns:
        :gas_list: list:
            list in format [fO2, fHe, fN2, time] representing gas in trimix format

    """
        times = gas_data[0]
        gas_codes = gas_data[1]
        gas_list = []

        for i, code in enumerate(gas_codes):
            list_entry = [0, 0, 0, 0]
            code = int(round(code, 6))
            fO2 = 0.0
            fN2 = 0.0
            fHe = 0.0
            # Air
            # Following the gas code: 1.mn
            if(code == 1):
                fO2 = 0.21
                fN2 = 0.79
            # Nitrox
            # Following the gas code: 2.mn
            elif(code == 2):
                fO2 = round(gas_codes[i] - 2, 2)
                fN2 = round(1.0 - fO2, 2)
            # Heliox
            # Following the gas code: 4.mn
            elif(code == 4):
                fO2 = round(gas_codes[i] - 4, 2)
                fHe = round(1.0 - fO2, 2)
            # Trimix
            # Following the gas code: 6.mnoqpr
            elif(code == 6):
                fO2 = round(gas_codes[i] - 6, 2)
                index = str(gas_codes[i])
                nitrogen = index[5] + index[6]
                fN2 = float(nitrogen)/100
                fHe = 1.0 - (fO2 + fN2)
            # rebreather -> currently repreather func is not implemented so just use air.
            # Anything that includes a constant PIO2
            else:
                fO2 = 0.21
                fN2 = 0.79

            list_entry = [fO2, fHe, fN2, round(times[i], 2)]
            gas_list.append(list_entry)

        return gas_list
