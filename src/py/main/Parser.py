"""
:Author(s) Adam Camer-Pesci, Augustine Italiano:

V2 of Parser module.
V2 created by Adam Camer-pesci
V1 created by Adam Camer-Pesci & Augustine Italiano

Class for Parsing raw data to JSON format

"""

from abc import ABC, abstractmethod


class Parser(ABC):
    """
    Base class for parsing different diving models to JSON format
    
"""

    @abstractmethod
    def __init__(self, model, **kwargs):
        """
    default constructor for Parser object

    :param model: The halftime set used to model data

    :param kwargs:
        optional keyword arguments - used to toggle gradient factor output (kwargs as some models wont require a toggle)

    """
        pass

    def get_list_json(self):
        """
    return the list of json objects (dive profiles)

        :returns dictionary:
            JSON object list
    """
        return self._structure_dict

    @abstractmethod
    def parse_json(self, summary, gf_data, otu, max_ascent, fileName, model, **kwargs):
        """
    interface for converting the dive profile to a json object

    :param summary: dataframe:
        a dataframe containing columns: MaxIns, MaxBub, N2CP, Surf

    :param gf_data: list:
        a list containing gradient factor calculation results

    :param fileName: string:
        a string containing the file name for the dive

    :param model: string:
        a string containing the model chosen for the dive

    :param kwargs:
        optional keyword arguments - used to toggle gradient factor output (kwargs as some models wont require a toggle)

    """
        pass


class BuzzacotParser(Parser):

    def __init__(self, model, **kwargs):
        """
    alt constructor for Buzzacott parser object

    """
        self.model = model
        self._structure_dict = {'headers': [
            'MaxIns', 'MaxBub', 'N2CP', 'Surf'], 'special': ['OTU', 'MaxAscent'], 'dives': []}

    def parse_json(self, summary, gf_data, otu, max_ascent, fileName, model, **kwargs):
        """
    implementation of Parser parse_json method for decompression model:

    Buzzacott

    """

        jsonObject = {
            'profile': fileName,
            'model': model,
            'results': [summary[:, 0].tolist(), summary[:, 1].tolist(), summary[:, 2].tolist(), summary[:, 4].tolist(), otu, max_ascent]
        }
        self._structure_dict["dives"].append(jsonObject)


class WorkmanParser(Parser):

    def __init__(self, model, **kwargs):
        """
    alt constructor for Workman parser object

    """
        toggle = kwargs.get('toggle', None)
        self.model = model
        self._structure_dict = {'headers': ['MaxIns', 'MaxBub', "N2CP", 'Surf', 'GFLowMax', 'GFHigh'], 'special': [
            'GFLowMaxMax', 'GF100D', 'FirstMiss', 'GFHighMax', 'OTU', 'MaxAscent'], 'dives': []}

        if(toggle == False):
            self._structure_dict = {'headers': ['MaxIns', 'MaxBub', 'N2CP', 'Surf'], 'special': [
                "OTU", "MaxAscent"], "dives": []}

    def parse_json(self, summary, gf_data, otu, max_ascent, fileName, model, **kwargs):
        """
    implementation of Parser parse_json method for decompression model:

    Workman65

    """
        toggle = kwargs.get('toggle', None)
        if(toggle == False):
            jsonObject = {
                'profile': fileName,
                'model': model,
                'results': [summary[:, 0].tolist(), summary[:, 1].tolist(), summary[:, 2].tolist(), summary[:, 4].tolist(), otu, max_ascent]
            }
        else:
            jsonObject = {
                'profile': fileName,
                'model': model,
                'results': [summary[:, 0].tolist(), summary[:, 1].tolist(), summary[:, 2].tolist(), summary[:, 4].tolist(),
                            gf_data[0].tolist(), gf_data[1], gf_data[2], gf_data[3], gf_data[4].tolist(), gf_data[5], otu, max_ascent]
            }
        self._structure_dict['dives'].append(jsonObject)


class HaldaneParser(Parser):

    def __init__(self, model, **kwargs):
        """
    alt constructor for Haldane parser object

    """
        toggle = kwargs.get('toggle', None)
        self.model = model
        self._structure_dict = {'headers': [
            'MaxIns', 'MaxBub', 'N2CP', 'Surf', 'GFHigh'], 'special': ['GFHighMax', 'OTU', 'MaxAscent'], 'dives': []}

        if(toggle == False):
            self._structure_dict = {'headers': ['MaxIns', 'MaxBub', 'N2CP', 'Surf'], 'special': [
                'OTU', 'MaxAscent'], 'dives': []}

    def parse_json(self, summary, gf_data, otu, max_ascent, fileName, model, **kwargs):
        """
    implementation of Parser parse_json method for decompression models:

    Haldane

    """
        toggle = kwargs.get('toggle', None)
        if(toggle == False):
            jsonObject = {
                'profile': fileName,
                'model': model,
                'results': [summary[:, 0].tolist(), summary[:, 1].tolist(), summary[:, 2].tolist(), summary[:, 4].tolist(), otu, max_ascent]
            }
        else:

            jsonObject = {
                'profile': fileName,
                'model': model,
                'results': [summary[:, 0].tolist(), summary[:, 1].tolist(), summary[:, 2].tolist(), summary[:, 4].tolist(),
                            gf_data[4].tolist(), gf_data[5], otu, max_ascent]
            }
        self._structure_dict['dives'].append(jsonObject)


class BuhlmannParser(Parser):

    def __init__(self, model, **kwargs):
        """
    alt constructor for buhlmann parser object

    """
        toggle = kwargs.get('toggle', None)
        self.model = model
        self._structure_dict = {'headers': ['N2Ins', 'HeIns', 'TotalIns', 'MaxBub', 'N2CP', 'HeCP', 'N2Surf', 'HeSurf', 'GFLowMax', 'GFHigh'], 'special': [
            'GFLowMaxMax', 'GF100D', 'FirstMiss', 'GFHighMax', 'OTU', 'MaxAscent'], 'dives': []}

        if(toggle == False):
            self._structure_dict = {'headers': [
                'N2Ins', 'HeIns', 'TotalIns', 'MaxBub', 'N2CP', 'HeCP', 'N2Surf', 'HeSurf'], 'special': ['OTU', 'MaxAscent'], 'dives': []}

    def parse_json(self, summary, gf_data, otu, max_ascent, fileName, model, **kwargs):
        """
    implementation of Parser parse_json method for decompression models:

    ZH-L16A,
    ZH-L16B,
    ZH-L16C

    """
        toggle = kwargs.get('toggle', None)
        if(toggle == False):
            jsonObject = {
                'profile': fileName,
                'model': model,
                'results': [summary[:, 0].tolist(), summary[:, 6].tolist(), summary[:, 7].tolist(), summary[:, 1].tolist(), summary[:, 2].tolist(), summary[:, 3].tolist(), summary[:, 4].tolist(), summary[:, 5].tolist(), otu, max_ascent]
            }
        else:
            jsonObject = {
                'profile': fileName,
                'model': model,
                'results': [summary[:, 0].tolist(), summary[:, 6].tolist(), summary[:, 7].tolist(), summary[:, 1].tolist(), summary[:, 2].tolist(), summary[:, 3].tolist(), summary[:, 4].tolist(), summary[:, 5].tolist(),
                            gf_data[0].tolist(), gf_data[1], gf_data[2], gf_data[3], gf_data[4].tolist(), gf_data[5], otu, max_ascent]
            }

        self._structure_dict['dives'].append(jsonObject)
