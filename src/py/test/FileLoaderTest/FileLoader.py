"""
:Author(s) Adam Camer-Pesci:
    
Class for file loading interface
This file contains the various implementations used to load different file types.
"""
from abc import ABC, abstractmethod
import os
import re
# import py.main.Calculations
import rpy2.robjects.packages as rpackages
import numpy as np
from rpy2 import robjects


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
                if re.search('^time,depth$', first_line):
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
                             " " + path + " is invalid file.\n" + "check_of_first_line= " + first_line)
                except IOError:
                    print("file not accessible")
                finally:
                    fw.close()
        return csv_files, csv_paths


class ANSLoader(FileLoader):

    def load(self):#, #file_paths):
        # TODO : Implement .ans loading functionality
        # TODO : This will work as a normal csv, user will select half time set after processing
        ans = open('./resources/s_33_leh.ans', 'r')
        fileAns = open("write.csv", 'w')
        utils = rpackages.importr('utils')
        rows = ans.readlines()
        # data_frame = np.array([np.arange(len(rows)), np.arange(3)])
        data_frame = np.zeros((len(rows), 3), dtype=np.float32)
        time = 0.0
        depth = 0.0
        gas_code = 0.0
        i = 0
        ii = 0
        for line in rows: 
            elements = line.split(",")
            if (len(elements)-1 == 4): # gas switch 
                # print(line + ": CHANGE THE GAS")
                mnt = elements[0]
                data_frame[i][0] = mnt
                depth = elements[1]
                data_frame[i][1] = depth
                gas_code = elements[2]
                data_frame[i][2] = gas_code
                i = i + 1
            elif (len(elements)-1 == 3): # Gas code, dcs hit, probability 
                print(line)
            elif (len(elements)-1 == 2): #time and depth 
                # print(line + " my float value is: " + str(type(float(elements[0]))))
                mnt = elements[0]
                data_frame[i][0] = mnt
                depth = elements[1]
                data_frame[i][1] = depth
                i = i + 1
            elif (len(elements) -1 == 1): #!EOD !ND 
                print(line)
                # break # just testing one dive at the moment 
            
        # data_frame[1][0] = 1.20
        print(data_frame[1][0])
        print(data_frame[1][1])
        print(data_frame)
        np.savetxt("temp.csv",data_frame, delimiter=',', fmt="%.6f") #6 decimal spaces because of tri mix 
        dataf = utils.read_csv("temp.csv")

        return dataf


        


    def createGas(self, gasCode):
        nitrox = robjects.r['nitrox']
        
        if(int(gasCode) == 1): #AIR CONSTANT 21% OXYGEN 
            gas = nitrox(0.21)
        elif(int(gasCode) == 2): #OXYGEN % IN NITROX 
            percentage = round(gasCode%2)
            gas = nitrox(percentage)
        elif(int(gasCode) == 4): #OXYGEN % IN HELIOX 
            percentage = round(gasCode%2)
            gas = nitrox(percentage)
        elif(int(gasCode) == 6): #OXYGEN % IN TRI MIX 
            gas = nitrox(percentage)

