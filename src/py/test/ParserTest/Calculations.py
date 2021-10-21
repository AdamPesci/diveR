import sys
import DiveConstants as dc
from rpy2.rinterface import NA
from rpy2.robjects.vectors import IntVector, FloatVector, StrVector
import rpy2.robjects.packages as rpackages
import rpy2.robjects as robjects
import numpy as np
np.set_printoptions(suppress=True)
utils = rpackages.importr('utils')
scuba = rpackages.importr('scuba')


def max_ascent(dive):
    """
    finds the maximum ascent rate

    :param dive: dataframe:
        a dataframe containing columns: time and depth

    :return: float:
        the maximum ascent rate

"""
    max = 0
    # finds maximum positive difference between each time interval
    for i in range(len(dive[1])):
        try:
            temp = dive[1][i+1]
            if (dive[1][i] - temp) > max:
                max = dive[1][i] - temp
        except IndexError:
            pass
    return round(max/10, 3)


def compartment_pressures(data, halftime_set):
    """
    Gets compartment pressures from dive profile based on given half time set.

    :param data: dataframe:
        a dataframe containing columns: time and depth

    :param halftime_set: str:
        the name of the halftime set to be used

    :return: cp a dataframe containing compartment pressures from 1,1b - 16

"""

    # setup R functions
    dive = robjects.r['dive']
    haldane = robjects.r['haldane']
    pickmodel = robjects.r['pickmodel']
    data_frame = robjects.r['data.frame']
    nitrox = robjects.r['nitrox']

    dive_profile = dive(data, gas=nitrox(0.21))
    # check if halftime_set is one of the allowed halftime sets, raise exception if not.
    if(not(halftime_set == 'ZH-L16A' or
       halftime_set == 'Haldane' or
       halftime_set == 'DSAT' or
       halftime_set == 'Workman65' or
       halftime_set == 'Buzzacott')):
        raise ValueError('Invalid halftime-set')
    else:
        # if halftime set is decimate, set up decimate model.
        if(halftime_set == 'Buzzacott'):
            hm = robjects.r['hm']
            decimate_model = hm(HalfT=IntVector((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)), M0=IntVector((
                                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)), dM=IntVector((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)))
            cp = haldane(dive_profile, model=decimate_model, progressive=True)
        # for all other models, set up normally
        else:
            cp = haldane(dive_profile, model=pickmodel(
                halftime_set), progressive=True)
    # return the compartment pressures as dataframe
    return data_frame(cp)


def max_values(ambient_pressures, compartment_pressures, totalIPP):
    """
    merges max_bubble, max_inspired into a single function

    :param ambient_pressures: float[]:
        a list of ambient pressures at each time point

    :param compartment_pressures: float[]:
        a list of compartment pressure values

    :param totalIPP: float[]:
        the total inert gas partial pressure at given time points

    :return: float[]:
        max_values : array containing 4 collumns: maxins, maxbub, the cp where maxbub occured, and surf the cp when the diver surfaces.

    """
    # get compartment pressures and ambient pressure data
    cp = compartment_pressures
    ap = ambient_pressures
    # initialize output array, array is same length as comparment pressures
    max_values = np.zeros((len(cp), 5))
    for i in range(len(cp)):
        maxbub = 0
        maxins = -sys.maxsize
        n2cp = 0
        hecp = 0

        # find the maximum positive difference of inert gas against ambient pressure (pressure @ compartment - ambient pressure @ that depth)
        # find the maximum positive difference of inert gas inside each compartment
        for j in range(len(cp[i])):
            try:
                # nparr does [row,col]
                # dataframe does [col][row]
                tempbub = (cp[i][j] - ap[j, 1])  # cp[i][j]
                tempins = (cp[i][j] - totalIPP[j])
                if(tempbub > maxbub):
                    maxbub = tempbub
                    n2cp = cp[i][j]
                    if(len(cp)>17):
                        hecp = cp[i+17][j]
                if(tempins > maxins):
                    maxins = tempins
            except IndexError:
                pass
        max_values[i][0] = maxins
        max_values[i][1] = maxbub
        max_values[i][2] = n2cp
        max_values[i][3] = hecp
        max_values[i][4] = cp[i][len(cp[i])-1]
    return max_values

 # TODO: allow this to take in raw csv or a dataframe


def ambient_pressures(dive_csv):
    """
    calculates ambient pressures

    :param dive_csv: dataframe:
        a dataframe containing columns: time and depth

    :return: float[]:
        a list of ambient pressures at each time point

    """
    # R function setup
    data_frame = robjects.r['data.frame']
    # get dive data (times/depths)
    df = data_frame(dive_csv)
    # initialize output array
    ap = np.zeros((len(df[0]), len(df)))
    for i in range(len(df[0])):
        # nparr does [row,col]
        # dataframe does [col][row]
        ap[i, 0] = df[0][i]
        ap[i, 1] = df[1][i]/10 + 1
    return ap


def max_inspired(compartment_pressures, totalIPP):
    """
    calculates the maximum positive difference between the inert gas pressure inside each compartment (1-17, but it should be 1-16 with both 1 and 1b included) 
    and the partial pressure of inert gas in the breathing mixture at each respective time and depth.

    :param: compartment_pressures: float[]:
        a list of compartment pressure values

    :param totalIPP: float[]:
        the total inert gas partial pressure at given time points

    :return: float[]:
        the maximum inspired difference for each compartment
        A list containing the maximum positive differences of inert gas against totalIPP (pressure @ compartment - totalIPP @ that depth)

    """
    # get compartment pressures and ambient pressure data
    cp = compartment_pressures
    # initialize output array, array is same length as comparment pressures
    maxins = np.zeros(len(cp))
    for i in range(len(cp)):
        max = -sys.maxsize
        # find the maximum positive difference of inert gas against totalIPP (pressure @ compartment - totalIPP @ that depth)
        for j in range(len(cp[i])):
            try:
                # nparr does [row,col]
                # dataframe does [col][row]
                tempmax = (cp[i][j] - totalIPP[j])  # cp[i][j]
                if(tempmax > max):
                    max = tempmax
                maxins[i] = max
            except IndexError:
                pass
    return maxins


def max_bubble(ambient_pressures, compartment_pressures):
    """
    calculates the maximum positive difference between the inert gas pressure inside each compartment (1-17, but it should be 1-16 with both 1 and 1b included) 

    :param ambient_pressures: float[]:
        a list of ambient pressures at each time point

    :param compartment_pressures: float[]:
        a list of compartment pressure values

    :return: float[]:
        the maximum bubble difference for each compartment

    """
    # get compartment pressures and ambient pressure data
    cp = compartment_pressures
    ap = ambient_pressures
    # initialize output array, array is same length as comparment pressures
    maxbubs = np.zeros((len(cp), 2))
    for i in range(len(cp)):
        max = -sys.maxsize
        n2cp = 0

        # find the maximum positive difference of inert gas against ambient pressure (pressure @ compartment - ambient pressure @ that depth)cls
        for j in range(len(cp[i])):
            try:
                # nparr does [row,col]
                # dataframe does [col][row]
                tempbub = (cp[i][j] - ap[j, 1])  # cp[i][j]
                if(tempbub > max):
                    max = tempbub
                    n2cp = cp[i][j]
                maxbubs[i][0] = max
                maxbubs[i][1] = n2cp
            except IndexError:
                pass
    return maxbubs

# TODO: having dive might be redundant if compartment pressures can be used?
# TODO: Find out how to combine the nitrogen m values with helium m values - when helium and nitrogen is in gas mixture


def gradient_factors(dive, gases, compartment_pressures):
    """
    calculates the maximum percentage of the respective M-value any compartment reaches otherwise known as the gradient factor. 
    Below values are harcoded from Erik C. Baker's “Understanding M-values” from tables 2 & 4

    :param dive: dataframe:
        a dataframe containing columns: time and depth

    :param gasses: str:
        TODO: this will be a list later?

    :param compartment_pressures: dataframe containing compartment pressure values

    :return: float[]:
        list of gradient factor values

    """

    cp = compartment_pressures
    # nitrogen delta slope values in order [1, 1b, 2, ... 16]
    n_delta = dc.N_DELTA

    # nitogen surfacing m-value in order [1, 1b, 2, ... 16]
    n_m_naught = dc.N_M_NAUGHT

    # helium delta slope values in order [1, 1b, 2, ... 16]
    he_delta = dc.HE_DELTA

    # helium surfacing m-value in order [1, 1b, 2, ... 16]
    he_m_naught = dc.HE_M_NAUGHT

    gaugeP = np.zeros(len(dive[0]))

    # nitrogen and helium XDM, calculation = (the respective gas * gauge pressure at each timepoint)
    nXDM = np.zeros((len(gaugeP), 17))
    heXDM = np.zeros((len(gaugeP), 17))

    # nitrogen and helium respective m values
    n_mvalues = np.zeros((len(nXDM), 17))
    he_mvalues = np.zeros((len(heXDM), 17))

    # if a dive has both nitrogen and helium then we need to combine the m values using a weighting
    total_mvalues = np.zeros((len(nXDM), 17))

    GFs = np.zeros((len(n_mvalues), 17))
    maxGF = np.zeros(len(gaugeP))

    for i in range(len(gaugeP)):
        gaugeP[i] = dive[1][i]/10
        for j in range(17):
            nXDM[i][j] = gaugeP[i] * n_delta[j]
            heXDM[i][j] = gaugeP[i] * he_delta[j]
            n_mvalues[i][j] = (n_m_naught[j]/10) + nXDM[i][j]
            he_mvalues[i][j] = (he_m_naught[j]/10) + heXDM[i][j]
            GFs[i][j] = (cp[j][i] / n_mvalues[i][j]) * 100
            maxGF[i] = round(np.max(GFs[i]))

    '''
    print("\ngaugeP")
    print(gaugeP)

    print("\nnXDM")
    print(nXDM)

    print("\nheXDM")
    print(heXDM)

    print("\n n_mvalues")
    print(n_mvalues)

    print("\n gradient factors")
    print(GFs)
    
    print("\nmax GF")
    print(maxGF)
    '''


def helium_inert_pressure(ambient_pressures, gases):
    """
    calculate inert gas partial pressure of helium at each time point

    :param ambient_pressures: float[]:
        a list of ambient pressures at each time point

    :param gasses: str:
        TODO: this will be a list later?

    :return: float[]:
        the inert gas partial pressure of helium at each time point

    """
    # this will need to be changed later to get the actual value of helium
    helium = dc.HELIUM
    ap = ambient_pressures
    heIPP = np.zeros(len(ap))
    for i in range(len(ap)):
        heIPP[i] = ap[i, 1] * helium
    return heIPP


def nitrogen_inert_pressure(ambient_pressures, gases):
    """
    calculate inert gas partial pressure of nitrogen at each time point

    :param ambient_pressures: float[]:
        a list of ambient pressures at each time point

    :param gasses: str: 
        TODO: this will be a list later?

    :return: float[]:
        the inert gas partial pressure of nitrogen at each time point

    """
    nitrogen = dc.NITROGEN
    ap = ambient_pressures
    nIPP = np.zeros(len(ap))
    for i in range(len(ap)):
        nIPP[i] = ap[i, 1] * nitrogen
    return nIPP


def totalIPP(nIPP, heIPP):
    """
    calculate the total inert gas partial pressure

    :param niPP: float[]:
        the inert gas partial pressure of nitrogen at a given time points

    :param heIPP: float[]:
        the inert gas partial pressure of helium at a given time points

    :return: float[]:
        the total inert gas partial pressure at given time points

    """
    total_IPP = np.zeros(len(nIPP))
    for i in range(len(nIPP)):
        total_IPP[i] = nIPP[i] + heIPP[i]
    return total_IPP
