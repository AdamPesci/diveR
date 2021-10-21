"""
:Author(s) Adam Camer-Pesci:

This class acts as the control centre for the backend components.

"""

import sys
import os
import json
from datetime import datetime
from rpy2.rinterface_lib.embedded import RRuntimeError
import rpy2.robjects.packages as rpackages
from rpy2.robjects.vectors import StrVector
import FileLoader
import FileWriter
import Calculations
import Parser


def write_log(path, message):
    """
    error log writing method

    :param path: path of associated file

    :param message: message to write to log

    """
    if not os.path.isdir('./logs'):
        os.mkdir('./logs')

    fw = open('./logs/Main.log', 'a')
    try:
        fw.write(datetime.today().strftime('%Y-%M-%d') + ' ' + datetime.now().strftime('%H:%M:%S') + '-' + path + ': '
                 + message + "\n")
    except IOError:
        sys.stderr.write('Could not access log file/folder')
    finally:
        fw.close()


def main():
    """
    Executes calculations for each dive profile provided by user and pipes result to front-end for display
"""
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

    # required to use scuba
    scuba = rpackages.importr('scuba')

    # get settings
    json_string = sys.argv[1]
    settings = json.loads(json_string)
    halftime_set = settings['halfTimeSet']
    file_dir = settings['filePathsDirectory']
    file_paths = settings['filePaths']
    out_path = settings['outputFilePath']
    gf_toggle = False
    gf_toggle = settings['gfToggle']
    cp_toggle = settings['cpToggle']
    gas_list = settings['gasCombinations']

    # force set for buzzacott model
    if(halftime_set == 'Buzzacott'):
        gf_toggle = False

    is_ans = True
    try:
        # figure out what type of file we are processing
        if(file_paths[0].endswith('.csv')):
            is_ans = False
    except IndexError as err:
        write_log('', 'File at index[0] not uploaded ' + repr(err))

    # initialize loader calcs parser, and filewriter
    csv_loader = FileLoader.CSVLoader()
    ans_loader = FileLoader.ANSLoader()
    fw = FileWriter.CSVWriter()
    calc = Calculations.Calculations()
    parser = {'Haldane': Parser.HaldaneParser('Haldane', toggle=gf_toggle),
              'DSAT': Parser.HaldaneParser('Haldane', toggle=gf_toggle),
              'ZH-L16A': Parser.BuhlmannParser('ZH-L16A', toggle=gf_toggle),
              'ZH-L16B': Parser.BuhlmannParser('ZH-L16A', toggle=gf_toggle),
              'ZH-L16C': Parser.BuhlmannParser('ZH-L16A', toggle=gf_toggle),
              'Workman65': Parser.WorkmanParser('Workman65', toggle=gf_toggle),
              'Buzzacott': Parser.BuzzacotParser('Buzzacott')
              }

    # load .ans files
    extra_list_ans = list()
    dives = list()

    if(is_ans):
        dives, filtered_paths, gas_data, extra_list_ans = ans_loader.load(
            file_dir,
            file_paths)
        gas_list = list()
    else:
        # load .csv files
        dives, filtered_paths = csv_loader.load(file_dir, file_paths)

        # iterate over each file and perform calculations
    for i, dive_profile in enumerate(dives):
        try:
            # if processing ans files, generate gas_list from data inside file
            if(is_ans):
                gas_list.clear()
                gas_list = ans_loader.generate_gas_list(gas_data[i])

            try:
                # dive profile containing the gas mixes
                dive, gasses = calc.initialise_dive(dive_profile, gas_list)

                # get compartment pressures
                cp = calc.compartment_pressures(
                    dive, halftime_set)

                # calc ambient pressure
                ap = calc.ambient_pressures(dive_profile)

                # calc inert partial pressures
                nIPP = calc.nitrogen_inert_pressure(ap, gasses, dive)
                heIPP = calc.helium_inert_pressure(ap, gasses, dive)
                totalIPP = calc.totalIPP(nIPP, heIPP)

                # calc maxIns,maxBub, etc...
                values = calc.max_values(ap, cp, totalIPP, nIPP, heIPP)

                # special calcs
                otu = calc.o2_tox(dive)
                max_ascent = calc.max_ascent(dive_profile)

                # calc gradient factors
                gfs = []
                if(gf_toggle):
                    gfs = calc.gradient_factors(
                        dive_profile, cp, halftime_set, values)
                parser[halftime_set].parse_json(
                    values, gfs, otu, max_ascent, os.path.basename(filtered_paths[i]), halftime_set, toggle=gf_toggle)

                # write cp values if toggled -> writes to wherever the user is writing output file
                if(cp_toggle):
                    path = out_path
                    basename = os.path.basename(path)
                    if(is_ans):
                        replace = filtered_paths[i].replace('.ans', '_ans')
                    else:
                        replace = filtered_paths[i].replace('.csv', '_csv')
                    replace += '_cpvals.csv'
                    new_basename = os.path.basename(replace)
                    cp_path = path.replace(basename, new_basename)
                    utils.write_csv(cp, cp_path)
            except RRuntimeError as err:
                write_log(
                    filtered_paths[i], 'Unable to parse file. R Runtime Error see: ' + repr(err))
            except IndexError as err:
                write_log(filtered_paths[i],
                          'Error in IPP function ' + repr(err))
        except ValueError as err:
            write_log('', 'Error in main calculations loop. ' + repr(err))

    # parse data to json string
    parsed_json = parser[halftime_set].get_list_json()
    # print data for front-end to see
    dump = json.dumps(parsed_json, indent=4)
    print(dump)

    # write files
    if(is_ans):
        fw.write(out_path, parsed_json, gf_toggle, extra_list=extra_list_ans)
    else:
        fw.write(out_path, parsed_json, gf_toggle)


if __name__ == "__main__":
    main()
