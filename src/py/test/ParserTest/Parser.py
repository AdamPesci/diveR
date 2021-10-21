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

    def __init__(self, model):
        """
    default constructor for Parser object

    :param model: The halftime set used to model data
    """
        self.model = model
        self._structure_dict = {}

    def get_list_json(cls):
        """
    return the list of json objects (dive profiles)

        :returns list:
            json object list
    """
        return cls._structure_dict

    @abstractmethod
    def parse_json(cls, summary, gf_data, otu, max_ascent, fileName, model):
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
    """
        pass


class BuzzacotParser(Parser):
    def parse_json(cls, summary, gf_data, otu, max_ascent, fileName, model):
        """
    implementation of Parser parse_json method for Buzzacott decompression model

    """
        cls._structure_dict = {"headers": [
            "MaxIns", "MaxBub", "N2CP", "Surf"], "special": ["OTU", "MaxAscent"], "dives": []}
        jsonObject = {
            "profile": fileName,
            "model": model,
            "results": [summary[:, 0].tolist(), summary[:, 1].tolist(), summary[:, 2].tolist(), summary[:, 4].tolist(), otu, max_ascent]
        }
        cls._structure_dict["dives"].append(jsonObject)


class WorkmanParser(Parser):
    def parse_json(cls, summary, gf_data, otu, max_ascent, fileName, model):
        """
    implementation of Parser parse_json method for Workman65 decompression model

    """
        cls._structure_dict = {"headers": ["MaxIns", "MaxBub", "N2CP", "Surf", "GFLowMax", "GFHigh"], "special": [
            "GFLowMaxMax", "GF100D", "FirstMiss", "GFHighMax", "OTU", "MaxAscent"], "dives": []}
        jsonObject = {
            "profile": fileName,
            "model": model,
            "results": [summary[:, 0].tolist(), summary[:, 1].tolist(), summary[:, 2].tolist(), summary[:, 4].tolist(),
                        gf_data[0].tolist(), gf_data[1], gf_data[2], gf_data[3], gf_data[4].tolist(), gf_data[5], otu, max_ascent]
        }
        cls._structure_dict["dives"].append(jsonObject)


class HaldaneParser(Parser):
    def parse_json(cls, summary, gf_data, otu, max_ascent, fileName, model):
        """
    implementation of Parser parse_json method for Haldane decompression model

    """
        cls._structure_dict = {"headers": [
            "MaxIns", "MaxBub", "N2CP", "Surf", "GFHigh"], "special": ["GFHighMax", "OTU", "MaxAscent"], "dives": []}
        jsonObject = {
            "profile": fileName,
            "model": model,
            "results": [summary[:, 0].tolist(), summary[:, 1].tolist(), summary[:, 2].tolist(), summary[:, 4].tolist(),
                        gf_data[4].tolist(), gf_data[5], otu, max_ascent]
        }
        cls._structure_dict["dives"].append(jsonObject)


class BuhlmannParser(Parser):
    def parse_json(cls, summary, gf_data, otu, max_ascent, fileName, model):
        """
    implementation of Parser parse_json method for Buhlmann decompression models (ZH-L16A, ZH-L16B , and ZH-L16C)

    """
        cls._structure_dict = {"headers": ["MaxIns", "MaxBub", "N2CP", "HeCP", "Surf", "HeSurf", "GFLowMax", "GFHigh"], "special": [
            "GFLowMaxMax", "GF100D", "FirstMiss", "GFHighMax", "OTU", "MaxAscent"], "dives": []}
        jsonObject = {
            "profile": fileName,
            "model": model,
            "results": [summary[:, 0].tolist(), summary[:, 1].tolist(), summary[:, 2].tolist(), summary[:, 3].tolist(), summary[:, 4].tolist(), summary[:, 5].tolist(),
                        gf_data[0].tolist(), gf_data[1], gf_data[2], gf_data[3], gf_data[4].tolist(), gf_data[5], otu, max_ascent]
        }
        cls._structure_dict["dives"].append(jsonObject)
