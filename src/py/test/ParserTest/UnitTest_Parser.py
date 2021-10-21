import unittest
import Parser
import Calculations
import csv
import json
from pathlib import Path
import rpy2.robjects.packages as rpackages

utils = rpackages.importr('utils')

class test_parser(unittest.TestCase):
    def __init__(self): 
        self._fileData
        self._maxValues

    def test_max_values(self):
        # check that the json is the correct format: LENGTH
        # can create a Parser object 
        # read in file data
        file_path = Path(__file__).parent / "resources/dive_series1.csv"
        data = utils.read_csv(str(file_path))
        try:
            cp = Calculations.get_compartment_pressures(data, 'ZH-L16A')
            ap = Calculations.get_ambient_pressures(data)
        except TypeError:
            print("invalid halftime-set error caught")
        
        nIPP = Calculations.nitrogen_inert_pressure(ap, "gases")
        heIPP = Calculations.helium_inert_pressure(ap, "gases")
        totalIPP = Calculations.get_totalIPP(nIPP, heIPP)

        Calculations.gradient_factors(data, "gases", cp)
        self._maxValues = Calculations.max_values(ap, cp, totalIPP)
        print(self._maxValues)

    def test_json_field(self): 
        parser = Parser.Parser()
        parser.parse_json(self._maxValues, "dive_series1", 'ZH-L16A')
        json_list = parser.get_list_json()
        
        if(json_list.get("headers") != None):
            self.assertTrue(True)

        

    if __name__ == '__main__': 
        unittest.main() 
