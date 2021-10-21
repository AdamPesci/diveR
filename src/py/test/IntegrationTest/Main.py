"""
Authors: Augustine Italiano, Ryan Forster, Adam Camer-Pesci

This class will act as the control centre for the backend components:
    Calculations.py
    FileLoader.py
"""

import os
import sys
import csv
from datetime import datetime
import json
import rpy2.robjects.packages as rpackages
from rpy2.robjects.vectors import StrVector
import FileLoader
import FileWriter
import Calculations
import Parser
from rpy2 import robjects


def main():
    # rpy2 setup
    # print(rpy2.__version__)
    # needs comma as list. all function in sanity check will iterate characters otherwise.
    package_names = ('scuba',)
    utils = rpackages.importr('utils')
    # sanity check -> see if package is already installed
    if all(rpackages.isinstalled(x) for x in package_names):
        have_package = True
    else:
        have_package = False
    # install uninstalled packages from list
    if not have_package:
        utils.chooseCRANmirror(ind=1)
        packnames_to_install = [
            x for x in package_names if not rpackages.isinstalled(x)]
        if len(packnames_to_install) > 0:
            utils.install_packages(StrVector(packnames_to_install))

    scuba = rpackages.importr('scuba')

    json_string = "{\"filePaths\":[\"./resources/s_1076_leh.ans\"],\"halfTimeSet\":\"ZH-L16B\",\"gasCombinations\":[[0.2,0.2,0.6,0],[0.5,0,0.5,42.84]],\"outputFilePath\":\"./zhB\",\"gfToggle\":\"True\",\"cpToggle\":\"True\"}"
    settings = json.loads(json_string)

    halftime_set = settings['halfTimeSet']
    file_paths = settings['filePaths']
    out_path = settings['outputFilePath']
    gas_list = settings['gasCombinations']
    cp_toggle = settings['cpToggle']
    toggle = settings['gfToggle'].upper()
    if(toggle == 'FALSE'):
        gf_toggle = False
    else:
        gf_toggle = True

    if(halftime_set == 'Buzzacott'):
        gf_toggle = False
    # gasCode = 6.812134
    # print(round(gasCode - 6,6)) #full
    # print(round(round(gasCode - 6,6),2)) #oxygen
    # print(round(round(gasCode - 6,6),5)) #oxygen

    # initialize classes
    csv_loader = FileLoader.CSVLoader()
    ans_loader = FileLoader.ANSLoader()
    # # #gasList = [4.81,0.0]
    calc = Calculations.Calculations()
    # ans_path = ['./resources/s_34_leh.ans']
    # ans_dive_profile, ans_gas_list = ans_loader.load(ans_path)
    parser = {'Haldane': Parser.HaldaneParser('Haldane', toggle=gf_toggle),
              'DSAT': Parser.HaldaneParser('Haldane', toggle=gf_toggle),
              'ZH-L16A': Parser.BuhlmannParser('ZH-L16A', toggle=gf_toggle),
              'ZH-L16B': Parser.BuhlmannParser('ZH-L16A', toggle=gf_toggle),
              'ZH-L16C': Parser.BuhlmannParser('ZH-L16A', toggle=gf_toggle),
              'Workman65': Parser.WorkmanParser('Workman65', toggle=gf_toggle),
              'Buzzacott': Parser.BuzzacotParser('Buzzacott')
              }

    fw = FileWriter.CSVWriter()
    extra_list_ans = None
    file_paths = list(file_paths)
    file_paths.append('./resources/s_33_leh.ans')

    if(file_paths[0].endswith('.ans') or file_paths[0].endswith('.txt')):
        dives, filtered_paths, gas_codes, extra_list_ans = ans_loader.load(
            file_paths)
        gas_list = list()

    else:
        dives, filtered_paths = csv_loader.load(file_paths)
    # initialize file counter
    i = 0
    # iterate over each file and perform calculations
    for dive_profile in dives:
        try:
            
            ##for each ans dive, convert codes for that dive into gaslist to pass to initialize dive
            if(filtered_paths[0].endswith('.ans') or filtered_paths[0].endswith('.txt')):
                gas_list.clear()
                gas_list = ans_loader.generate_gas_list(gas_codes[i])
            # convert gas_codes into gas_list
            # dive profile containing the gas mixes
            try:
                dive, gasses = calc.initialise_dive(dive_profile, gas_list) #ans files will have iterable gaslist
            except IndexError:
                dive, gasses = calc.initialise_dive(dive_profile, gas_list) #csv files will not
    
            tanklist = robjects.r['tanklist']
            print(tanklist(dive))
            cp = calc.compartment_pressures(
                dive, halftime_set)
            ap = calc.ambient_pressures(dive_profile)
            nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
            heIPP = calc.helium_inert_pressure(ap, gasses, dive)
            totalIPP = calc.totalIPP(nIPP, heIPP)
            max_ascent = calc.max_ascent(dive_profile)
            otu = calc.o2_tox(dive)
            begin_time = datetime.now()
            values = calc.max_values(ap, cp, totalIPP, nIPP, heIPP)
            print("finished max_values in: " + str(datetime.now()-begin_time))
            gfs = []
            begin_time = datetime.now()
            if(gf_toggle):
                gfs = calc.gradient_factors(
                    dive_profile, cp, halftime_set, values)

            parser[halftime_set].parse_json(
                values, gfs, otu, max_ascent, os.path.basename(filtered_paths[i]), halftime_set, toggle=gf_toggle)
            print("finished gf's in : " + str(datetime.now()-begin_time))

            # write cp values if toggled
            if(cp_toggle):
                path = out_path
                basename = os.path.basename(path)
                replace = filtered_paths[i].replace('.csv', '')
                replace += '_compartment-vals.csv'
                new_basename = os.path.basename(replace)
                cp_path = path.replace(basename, new_basename)
                utils.write_csv(cp, cp_path)
        except ValueError as err:
            sys.stderr.write(repr(err))
        i = i + 1
    parsed_json = parser[halftime_set].get_list_json()
    dump = json.dumps(parsed_json, indent=4)
    # print(dump)
    if(file_paths[0].endswith('.ans')):
        fw.write(out_path, parsed_json, gf_toggle, extra_list=extra_list_ans)
    else:
        fw.write(out_path, parsed_json, gf_toggle)


if __name__ == '__main__':
    begin_time = datetime.now()
    main()
    print("finished script in : " + str(datetime.now()-begin_time))
