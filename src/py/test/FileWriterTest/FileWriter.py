"""
:Author(s) Adam Camer-Pesci, Augustine Italiano:
    
Class for file loading interface
This file contains the various implementations used to load different file types.
"""
from abc import ABC, abstractmethod
import csv
import traceback


class FileWriter(ABC):
    """
Base class for writing different types of files
"""
    @abstractmethod
    def write(self, file_path, json_list):
        pass


class CSVWriter(FileWriter):
    def write(self, file_path, json_list):
        '''
        write structured JSON dictionary to csv file

        :param file_path: str: the output file path

        :param json_list: dict: A JSON object as python dictionary

        '''

        # sanity check
        if(not (file_path.endswith('.csv'))):
            file_path += '_diveR.csv'

        try:
            # Check if dives is empty (if empty, don't start writing a file)
            if len(json_list.get("dives")) > 0:
                with open(file_path, "w", newline='') as file:
                    writer = csv.writer(file)
                    list_headers = json_list.get("headers")
                    list_specials = json_list.get("special")
                    list_row = []
                    list_data = []
                    list_dives = json_list.get("dives")

                    # get model
                    model = json_list.get("dives")[0].get("model")
                    list_row.clear()
                    list_data.clear()

                    # add column for file names
                    list_row.append("File")
                    # if model buhlman, adjust headers (appending numbers to headers)
                    if(model == "ZH-L16A" or model == 'ZH-L16B' or model == 'ZH-L16C'):
                        row = ""
                        for header in list_headers:
                            # Buhlman headers 1-17
                            for i in range(17):
                                if(i == 0):
                                    row = header + str(1)
                                elif (i == 1):
                                    row = header + str(i) + "b"
                                else:
                                    row = header + str(i)
                                list_row.append(row)
                                # janky solution to get special headers correct order
                                # if the header GFflowmax has been written for the last time, append special headers
                                # TODO: Alternate way of doing this might be ideal

                                if header == 'GFLowMax' and i == 16:
                                    list_row.append(list_specials[0])
                                    list_row.append(list_specials[1])
                                    list_row.append(list_specials[2])

                    # default headers if not buhlman
                    else:
                        for header in list_headers:
                            for i in range((len(json_list.get("dives")[0].get("results")[0]))):
                                row = header + str(i+1)
                                if header == 'GFHigh' and i == 0:
                                    if(not (model == 'DSAT' or model == 'Haldane')):
                                        list_row.append(list_specials[0])
                                        list_row.append(list_specials[1])
                                        list_row.append(list_specials[2])
                                list_row.append(row)
                    # for models other than buzzacott, append special headers
                    if not(model == 'Buzzacott'):

                        if model == 'DSAT' or model == 'Haldane':
                            list_row.append(list_specials[0])
                            list_row.append(list_specials[1])
                            list_row.append(list_specials[2])
                        else:
                            list_row.append(list_specials[3])
                            list_row.append(list_specials[4])
                            list_row.append(list_specials[5])
                    else:
                        list_row.append(list_specials[0])
                        list_row.append(list_specials[1])
                    # write headers
                    writer.writerow(list_row)

                    # for each dive summary, write row data
                    for dive in list_dives:
                        list_row.clear()
                        list_data.clear()
                        # print dive profile filename
                        list_data.append(dive.get("profile"))
                        # print all results
                        list_results = dive.get("results")

                        for list_vals in list_results:
                            # try catch block in case object is not iterable, we then just want the object value
                            try:
                                # dont iterate strings
                                if type(list_vals) == str:
                                    list_data.append(list_vals)
                                else:
                                    for item in list_vals:
                                        row = str(item)
                                        list_data.append(row)
                                        i += 1
                            except TypeError:
                                list_data.append(list_vals)

                        writer.writerow(list_data)
        except IndexError:
            traceback.print_exc()
            print("dive profile empty")
        except IOError:
            print("Could not access file, file open")
