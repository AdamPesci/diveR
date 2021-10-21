"""
:Author(s) Ryan Forster:

This file contains the necessary testing methods used to test all calculations.
"""

from os import replace
import unittest
import Calculations
from pathlib import Path
import datetime
import csv
import rpy2.robjects.packages as rpackages

utils = rpackages.importr('utils')
scuba = rpackages.importr('scuba')

calc = Calculations.Calculations()

class TestCalcs(unittest.TestCase):

    # testing compartment_pressures method for buhlmann model
    def test_compartment_pressures_buhlmann(self):
        file_path = Path(__file__).parent / "resources/dive_1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])
        
        cp = calc.compartment_pressures(dive, 'ZH-L16A')
        file_path = Path(__file__).parent / "resources/dive_1_R_output/buhlmann_cp.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()

        try:
            for i in range (len(test_data)):
                for j in range (len(test_data[0])):
                    self.assertEqual(round(cp[j][i],5), round(float(test_data[i+1][j]), 5))
        except IndexError:
            pass

    # testing compartment_pressures method for haldane model
    def test_compartment_pressures_haldane(self):
        file_path = Path(__file__).parent / "resources/dive_1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])
        
        cp = calc.compartment_pressures(dive, 'Haldane')
        file_path = Path(__file__).parent / "resources/dive_1_R_output/haldane_cp.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()

        try:
            for i in range (len(test_data)):
                for j in range (len(test_data[0])):
                    self.assertEqual(round(cp[j][i],5), round(float(test_data[i+1][j]), 5))
        except IndexError:
            pass    

    # testing compartment_pressures method for dsat model
    def test_compartment_pressures_dsat(self):
        file_path = Path(__file__).parent / "resources/dive_1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])

        cp = calc.compartment_pressures(dive, 'DSAT')
        file_path = Path(__file__).parent / "resources/dive_1_R_output/dsat_cp.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()

        try:
            for i in range (len(test_data)):
                for j in range (len(test_data[0])):
                    self.assertEqual(round(cp[j][i],5), round(float(test_data[i+1][j]), 5))
        except IndexError:
            pass

    # testing compartment_pressures method for workman model
    def test_compartment_pressures_workman(self):
        file_path = Path(__file__).parent / "resources/dive_1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])

        cp = calc.compartment_pressures(dive, 'Workman65')
        file_path = Path(__file__).parent / "resources/dive_1_R_output/workman_cp.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()

        try:
            for i in range (len(test_data)):
                for j in range (len(test_data[0])):
                    self.assertEqual(round(cp[j][i],5), round(float(test_data[i+1][j]), 5))
        except IndexError:
            pass

    # testing nitrogen_inert_pressure method
    def test_nitrogen_inert_pressure(self):
        file_path = Path(__file__).parent / "resources/dive_1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])

        file_path = Path(__file__).parent / "resources/dive_1_R_output/nitrogen_IPP.csv"

        with open(file_path, encoding='utf-8-sig') as f:
            testData = f.readlines()
            testData = [line.rstrip() for line in testData]
        
        ap = calc.ambient_pressures(data)
        nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)

        for i in range(len(testData)):
            self.assertEqual(str(round(nIPP[i], 5)), testData[i])

    # testing helium_inert_pressure method
    def test_helium_inert_pressure(self):
        file_path = Path(__file__).parent / "resources/dive_1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])

        file_path = Path(__file__).parent / "resources/dive_1_R_output/helium_IPP.csv"

        with open(file_path, encoding='utf-8-sig') as f:
            testData = f.readlines()
            testData = [line.rstrip() for line in testData]
        
        ap = calc.ambient_pressures(data)
        heIPP = calc.helium_inert_pressure(ap, gasses, dive)

        for i in range(len(testData)):
            self.assertEqual((round(heIPP[i], 5)), float(testData[i]))

    # testing total_IPP method
    def test_totalIPP(self):
        file_path = Path(__file__).parent / "resources/dive_1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])

        file_path = Path(__file__).parent / "resources/dive_1_R_output/total_IPP.csv"

        with open(file_path, encoding='utf-8-sig') as f:
            testData = f.readlines()
            testData = [line.rstrip() for line in testData]
        
        ap = calc.ambient_pressures(data)
        nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
        heIPP = calc.helium_inert_pressure(ap, gasses, dive)
        totalIPP = calc.totalIPP(nIPP, heIPP)

        for i in range(len(testData)):
            self.assertEqual(str(round(totalIPP[i], 5)), testData[i])

    # testing max_ascent method
    def test_max_ascent(self):
        file_path = Path(__file__).parent / "resources/dive_3.csv"
        data = utils.read_csv(str(file_path))
        result = calc.max_ascent(data)
        self.assertEqual(result, 213.54)

    # testing max_bubble method for buhlmann model
    def test_max_bubble_buhlmann(self):
        file_path = Path(__file__).parent / "resources/dive_series1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])

        file_path = Path(__file__).parent / "resources/dive_series1_R_output/ds1_buhlmann.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()

        ap = calc.ambient_pressures(data)
        cp = calc.compartment_pressures(dive, 'ZH-L16A')
        nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
        heIPP = calc.helium_inert_pressure(ap, gasses, dive)
        totalIPP = calc.totalIPP(nIPP, heIPP)
        
        max_vals = calc.max_values(ap, cp, totalIPP, nIPP, heIPP)
        max_bubs = []

        for i in range(17):
            max_bubs.append(max_vals[i][1])
        
        try:
            for i in range(len(max_bubs)):
                self.assertEqual(round(max_bubs[i],5), round(float(test_data[1][i+18]),5))
        except IndexError:
            pass

    # testing max_bubble method for haldane model
    def test_max_bubble_haldane(self):
        file_path = Path(__file__).parent / "resources/dive_series1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])

        file_path = Path(__file__).parent / "resources/dive_series1_R_output/ds1_haldane.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()

        ap = calc.ambient_pressures(data)
        cp = calc.compartment_pressures(dive, 'Haldane')
        nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
        heIPP = calc.helium_inert_pressure(ap, gasses, dive)
        totalIPP = calc.totalIPP(nIPP, heIPP)
        
        max_vals = calc.max_values(ap, cp, totalIPP, nIPP, heIPP)
        max_bubs = []

        for i in range(5):
            max_bubs.append(max_vals[i][1])

        try:
            for i in range(len(max_bubs)):
                self.assertEqual(round(max_bubs[i],5), round(float(test_data[1][i+6]),5))
        except IndexError:
            pass

    # testing max_bubble method for dsat model
    def test_max_bubble_dsat(self):
        file_path = Path(__file__).parent / "resources/dive_series1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])

        file_path = Path(__file__).parent / "resources/dive_series1_R_output/ds1_dsat.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()

        ap = calc.ambient_pressures(data)
        cp = calc.compartment_pressures(dive, 'DSAT')
        nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
        heIPP = calc.helium_inert_pressure(ap, gasses, dive)
        totalIPP = calc.totalIPP(nIPP, heIPP)
        
        max_vals = calc.max_values(ap, cp, totalIPP, nIPP, heIPP)
        max_bubs = []

        for i in range(8):
            max_bubs.append(max_vals[i][1])
        
        try:
            for i in range(len(max_bubs)):
                self.assertEqual(round(max_bubs[i],5), round(float(test_data[1][i+9]),5))
        except IndexError:
            pass

    # testing max_bubble method for workman model
    def test_max_bubble_workman(self):
        file_path = Path(__file__).parent / "resources/dive_series1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])

        file_path = Path(__file__).parent / "resources/dive_series1_R_output/ds1_workman.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()

        ap = calc.ambient_pressures(data)
        cp = calc.compartment_pressures(dive, 'Workman65')
        nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
        heIPP = calc.helium_inert_pressure(ap, gasses, dive)
        totalIPP = calc.totalIPP(nIPP, heIPP)
        
        max_vals = calc.max_values(ap, cp, totalIPP, nIPP, heIPP)
        max_bubs = []

        for i in range(9):
            max_bubs.append(max_vals[i][1])
        
        try:
            for i in range(len(max_bubs)):
                self.assertEqual(round(max_bubs[i],5), round(float(test_data[1][i+10]),5))
        except IndexError:
            pass

    # testing max_inspired method for haldane model
    def test_max_inspired_buhlmann(self):
        file_path = Path(__file__).parent / "resources/dive_series1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])

        file_path = Path(__file__).parent / "resources/dive_series1_R_output/ds1_buhlmann.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()

        ap = calc.ambient_pressures(data)
        cp = calc.compartment_pressures(dive, 'ZH-L16A')
        nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
        heIPP = calc.helium_inert_pressure(ap, gasses, dive)
        totalIPP = calc.totalIPP(nIPP, heIPP)
        
        max_vals = calc.max_values(ap, cp, totalIPP, nIPP, heIPP)
        max_bubs = []

        for i in range(17):
            max_bubs.append(max_vals[i][0])

        try:
            for i in range(len(max_bubs)):
                self.assertEqual(round(max_bubs[i],5), round(float(test_data[1][i+1]),5))
        except IndexError:
            pass

    # testing max_inspired method for haldane model
    def test_max_inspired_haldane(self):
        file_path = Path(__file__).parent / "resources/dive_series1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])

        file_path = Path(__file__).parent / "resources/dive_series1_R_output/ds1_haldane.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()

        ap = calc.ambient_pressures(data)
        cp = calc.compartment_pressures(dive, 'Haldane')
        nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
        heIPP = calc.helium_inert_pressure(ap, gasses, dive)
        totalIPP = calc.totalIPP(nIPP, heIPP)
        
        max_vals = calc.max_values(ap, cp, totalIPP, nIPP, heIPP)
        max_bubs = []

        for i in range(5):
            max_bubs.append(max_vals[i][0])

        try:
            for i in range(len(max_bubs)):
                self.assertEqual(round(max_bubs[i],5), round(float(test_data[1][i+1]),5))
        except IndexError:
            pass

    # testing max_inspired method for dsat model
    def test_max_inspired_dsat(self):
        file_path = Path(__file__).parent / "resources/dive_series1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])
        file_path = Path(__file__).parent / "resources/dive_series1_R_output/ds1_dsat.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()

        ap = calc.ambient_pressures(data)
        cp = calc.compartment_pressures(dive, 'DSAT')
        nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
        heIPP = calc.helium_inert_pressure(ap, gasses, dive)
        totalIPP = calc.totalIPP(nIPP, heIPP)
        
        max_vals = calc.max_values(ap, cp, totalIPP, nIPP, heIPP)
        max_bubs = []

        for i in range(8):
            max_bubs.append(max_vals[i][0])
        
        try:
            for i in range(len(max_bubs)):
                self.assertEqual(round(max_bubs[i],5), round(float(test_data[1][i+1]),5))
        except IndexError:
            pass

    # testing max_inspired method for workman model
    def test_max_inspired_workman(self):
        file_path = Path(__file__).parent / "resources/dive_series1.csv"
        data = utils.read_csv(str(file_path))
        dive, gasses = calc.initialise_dive(data, [])

        file_path = Path(__file__).parent / "resources/dive_series1_R_output/ds1_workman.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()

        ap = calc.ambient_pressures(data)
        cp = calc.compartment_pressures(dive, 'Workman65')
        nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
        heIPP = calc.helium_inert_pressure(ap, gasses, dive)
        totalIPP = calc.totalIPP(nIPP, heIPP)
        
        max_vals = calc.max_values(ap, cp, totalIPP, nIPP, heIPP)
        max_bubs = []

        for i in range(9):
            max_bubs.append(max_vals[i][0])
        
        try:
            for i in range(len(max_bubs)):
                self.assertEqual(round(max_bubs[i],5), round(float(test_data[1][i+1]),5))
        except IndexError:
            pass

    # testing gradient_factors method
    def test_gradient_factors_air(self):
        file_path = Path(__file__).parent / "resources/Weebubbie.csv"
        data = utils.read_csv(str(file_path))

        file_path = Path(__file__).parent / "resources/Weebubbie_Air_GFL.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()
        
        # dive profile containing the gas mixes
        dive, gasses = calc.initialise_dive(data, [])
        ap = calc.ambient_pressures(data)
        cp = calc.compartment_pressures(dive, 'ZH-L16B')
        nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
        heIPP = calc.helium_inert_pressure(ap, gasses, dive)
        totalIPP = calc.totalIPP(nIPP, heIPP)
        
        max_vals = calc.max_values(ap, cp, totalIPP, nIPP, heIPP)
        
        gfs = calc.gradient_factors(data, cp, 'ZH-L16B', max_vals)
        gf_lows = gfs[0]
        try:
            for i in range(len(gfs)):
                self.assertEqual(round(gf_lows[i],5), round(float(test_data[0][i]), 5))
        except IndexError:
            pass

    # testing gradient_factors method
    def test_gradient_factors_custom(self):
        file_path = Path(__file__).parent / "resources/Weebubbie.csv"
        data = utils.read_csv(str(file_path))

        file_path = Path(__file__).parent / "resources/Weebubbie_custom.csv"

        csv_file = open(file_path, 'r')
        file_reader = csv.reader(csv_file, delimiter=',')
        test_data = []
        for row in file_reader:
            test_data.append(row)

        csv_file.close()
        
        # dive profile containing the gas mixes
        dive, gasses = calc.initialise_dive(data, [[0.5,0,0.5,42.84]])
        ap = calc.ambient_pressures(data)
        cp = calc.compartment_pressures(dive, 'ZH-L16B')
        nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
        heIPP = calc.helium_inert_pressure(ap, gasses, dive)
        totalIPP = calc.totalIPP(nIPP, heIPP)
        
        max_vals = calc.max_values(ap, cp, totalIPP, nIPP, heIPP)
        
        gfs = calc.gradient_factors(data, cp, 'ZH-L16B', max_vals)
        gf_highs = gfs[4]
        try:
            for i in range(len(gfs)):
                self.assertEqual(gf_highs[i], int(test_data[0][i]))
        except IndexError:
            pass
        

if __name__ == '__main__':
    begin_time = datetime.datetime.now()
    unittest.main()
    print("finished script in : " + str(datetime.datetime.now()-begin_time))
