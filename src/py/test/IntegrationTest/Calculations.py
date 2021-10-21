"""
:Author(s) Adam Camer-Pesci, Ryan Forster:

This file contains the methods used to perform calculations on scuba diving profiles.
"""
from rpy2.robjects.vectors import IntVector
import rpy2.robjects as robjects
import numpy as np
import DiveConstants as dc


class Calculations:

    def initialise_dive(self, data, df_gas):
        """
        Creates and initialises the dive_profile object .

        :param data: dataframe:
            a dataframe containing columns: time and depth

        :param halftime_set: str:
            the name of the halftime set to be used

        :returns: cp a dataframe containing compartment pressures from 1,1b - 16

        """
        dive = robjects.r['dive']
        gas_list, tank_times = self.trimix_list(df_gas)
        size = len(gas_list)
        d = dive(data, tanklist=gas_list)
        # Use Imbedded R script to name and swap gas tanks for dive
        custom_gas = robjects.r('''
        customGas <- function(dive_profile, numgas, list_of_times)
        {
            #Applies names to the tanklist in the format c("1":"n") - necessary to select which gas to use at a specific time.
            names(tanklist(dive_profile)) <- c(1:numgas)
  
            #Cuts the dive_profile and switches to the specific gas at the time listed
            d <- cut(times.dive(dive_profile), breaks = c(do.call(c, list_of_times), Inf), include.lowest = TRUE, labels = names(tanklist(dive_profile)))
  
            whichtank(dive_profile) <- cut(times.dive(dive_profile), breaks = c(do.call(c, list_of_times), Inf), include.lowest = TRUE, labels = names(tanklist(dive_profile)))
  
            return(dive_profile)
        }
        ''')
        dive_profile = custom_gas(d, size, tank_times)
        return dive_profile, gas_list

    def trimix_list(self, gas_combinations):
        """
        converts gas_combination string into trimix gas objects

        :param gas_combinations: dataframe:
            a list of strings in the format [[f02 fHe fN2 time][...]]

        :returns tuple:

            :gas_list: a list of trimix gas objects
            :time_list: a list of times to pair with gas_list

    """
        trimix = robjects.r['trimix']
        gas_list = []
        time_list = []
        try:
            # set default gas to air if no gas specified at time 0
            if((len(gas_combinations) < 1 or gas_combinations[0][3] > 1)):
                gas_list.append(trimix(0.21, 0, 0.79))
                time_list.append(-1)
            for gas in gas_combinations:
                gas_list.append(trimix(gas[0], gas[1]))
                time_list.append(gas[len(gas)-1])
        except IndexError:
            pass

        return gas_list, time_list

    def o2_tox(self, dive_profile):
        """
        calculates oxygen toxcity exposure

        :param dive_profile: dive:
            a dive profile to test OTU level

        :returns float:
            value representing pulmonary oxygen toxicity dose for a given dive profile and breathing gas

    """
        oxtox = robjects.r['oxtox']
        otu = oxtox(dive_profile, progressive=False)
        return float(np.asarray(otu))

    def max_ascent(self, dive_csv):
        """
        finds the maximum ascent rate

        :param dive_csv: dataframe:
            a dataframe containing columns: time and depth

        :returns:
            the maximum ascent rate

    """
        data = np.array(dive_csv)
        max = 0
        ascent_rate = 0
        time_interval = data[0][3] - data[0][2]

        for idx, depth in np.ndenumerate(data[1, :]):
            try:

                temp = data[1][idx[0]+1]
                if ((depth - temp) > max):
                    max = depth - temp
            except IndexError:
                pass

            div = 60.0 / time_interval
            ascent_rate = round(max * div, 3)
    
        return ascent_rate

    def compartment_pressures(self, dive_profile, halftime_set):
        """
        Gets compartment pressures from dive profile based on given half time set.

        :param data: dataframe:
            a dataframe containing columns: time and depth

        :param halftime_set: str:
            the name of the halftime set to be used

        :returns: cp a dataframe containing compartment pressures from 1,1b - 16

    """
        # setup R functions
        haldane = robjects.r['haldane']
        pickmodel = robjects.r['pickmodel']
        data_frame = robjects.r['data.frame']

        if(not(halftime_set == 'ZH-L16A' or
               halftime_set == 'ZH-L16B' or
               halftime_set == 'ZH-L16C' or
               halftime_set == 'Haldane' or
               halftime_set == 'DSAT' or
               halftime_set == 'Workman65' or
               halftime_set == 'Buzzacott')):
            raise ValueError('Invalid halftime-set')
        else:
            # if halftime set is decimate, set up decimate model.
            if(halftime_set == 'Buzzacott'):
                hm = robjects.r['hm']
                buzzacott_model = hm(HalfT=IntVector((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)), M0=IntVector((
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)), dM=IntVector((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)))
                cp = haldane(dive_profile, model=buzzacott_model,
                             progressive=True)

            # if halftime set is ZH-L16B or ZH-L16C use ZH-L16A. This is like this in order to use model for different gradient factor calculations
            elif(halftime_set == 'ZH-L16B' or halftime_set == 'ZH-L16C'):
                cp = haldane(dive_profile, model=pickmodel(
                    'ZH-L16A'), progressive=True)
            # for all other models, set up normally
            else:
                cp = haldane(dive_profile, model=pickmodel(
                    halftime_set), progressive=True)
        # return the compartment pressures as dataframe
        return data_frame(cp)

    def max_values(self, ambient_pressures, compartment_pressures, totalIPP, nIPP, heIPP):
        """
        merges max_bubble, max_inspired into a single function

        :param ambient_pressures: float[]:
            a list of ambient pressures at each time point

        :param compartment_pressures: float[]:
            a list of compartment pressure values (cp_value)

        :param totalIPP: float[]:
            the total inert gas partial pressure at given time points

        :returns float[]:

            max_values : array containing the collumns:

            :max_ins: cp_value - totalIPP
            :max_bub: cp_value - ambient_pressure
            :n2_cp: cp_value where maxbub occured
            :he_cp: helium cp_value where maxbub occured
            :surf: the cp when the diver surfaces.
            :he_surf: the helium cp when the diver surfaces



        """
        # get compartment pressures and ambient pressure data
        # cp = [row][col]
        cp = np.array(compartment_pressures, dtype=np.float64).transpose()
        ap = ambient_pressures
        rows = cp.shape[0]
        cols = cp.shape[1]
        if cols > 17:
            cols = 17
        # initialize output array, array is same length as comparment pressures
        max_values = np.zeros((cols, 8))
        # for each column
        for i in range(cols):
            max_bub = 0
            max_ins = -9999
            max_he_ins = -9999
            total_ins = -9999
            n2_cp = 0
            he_cp = 0
            # for each row
            for j, cp_val in np.ndenumerate(cp[:, i]):

                try:
                    # for buhlmann models
                    if(cols == 17):
                        temp_ins = cp_val - nIPP[j]
                        he_ins = cp[j][i+17] - heIPP[j]
                        temp_total = temp_ins + he_ins

                        temp_bub = cp_val + cp[j][i+17] - ap[j]
                        if(he_ins > max_he_ins):
                            max_he_ins = he_ins
                    # for air dives
                    else:
                        temp_bub = cp_val - ap[j]
                        temp_ins = cp_val - totalIPP[j]
                        temp_total = temp_ins

                    if temp_total > total_ins:
                        total_ins = temp_total

                    if(temp_ins > max_ins):
                        max_ins = temp_ins

                    if(temp_bub > max_bub):
                        max_bub = temp_bub
                        n2_cp = cp_val
                        # get he_cp value iff buhlmann model
                        if(cols == 17):
                            he_cp = cp[j][i+17]

                except IndexError:
                    pass
            max_values[i][0] = max_ins
            max_values[i][1] = max_bub
            max_values[i][2] = n2_cp
            max_values[i][3] = he_cp
            max_values[i][4] = cp[rows-1][i]  # N2Surf

            if(cols == 17):
                max_values[i][5] = cp[rows-1][i+17]  # heSurf
                max_values[i][6] = max_he_ins  # helium maxins values
                max_values[i][7] = total_ins
        return max_values

    def ambient_pressures(self, dive):
        """
        calculates ambient pressures

        :param dive: dataframe:
            a dataframe containing columns: time and depth

        :returns float[]:
            a list of ambient pressures at each time point

        """
        # get dive data (times/depths) and convert to np array
        df = np.array(dive, dtype=np.float64)
        # initialize output array
        ap = np.zeros(df.shape[1])
        # enumerate 2nd column of array (depths) and calculate ambient pressure
        for idx, depth in np.ndenumerate(df[1, :]):
            ap[idx] = depth/10 + 1
        return ap

    def gradient_factors(self, data, compartment_pressures, halftime_set, surf_vals):
        """
        Calculates the maximum percentage of the respective M-value any compartment reaches known as the GFHigh and GFLow specific to the user selected halftime set,
        Finds the depth at which any compartment reaches 100% of its m value and finds the first miss according to that depth.

        :param data: dataframe:
            a dataframe containing columns: time and depth

        :param compartment_pressures: dataframe:
            a dataframe containing compartment pressures specific to each halftime set

        :param halftime_set: str:
            the name of the halftime set to be used

        :param surf_vals: array:
            a 2D array containing the surface values for nitrogen and helium needed to calculate the GFHigh values

        :returns list:

            :GF_Lows_final: all final values GFLowNMax
            :GF_Lows_max_max: the maximum value of all GFLowNMax values,
            :gf_100D: an integer representing the depth at which a compartment hits 100% of its m value
            :first_miss: the closest multiple of 3 to gf_100D
            :GF_Highs: all GFHigh values
            :GF_Highs_max: the maximum value of all GFHigh values

        """
        # convert compartment pressures to numpy array, transpose so we have [rows][cols] rather than [cols][rows]
        cp = np.array(compartment_pressures, dtype=np.float64).transpose()
        if halftime_set == 'ZH-L16A' or halftime_set == 'ZH-L16B' or halftime_set == 'ZH-L16C':
            num_compartments = 17
        elif halftime_set == 'DSAT':
            num_compartments = 8
        elif halftime_set == 'Workman65':
            num_compartments = 9
        elif halftime_set == 'Haldane':
            num_compartments = 5

        gaugeP = np.zeros(cp.shape[0])

        # nitrogen and helium XDM, calculation = (the respective gas * gauge pressure at each timepoint)
        nXDM = np.zeros((gaugeP.shape[0], num_compartments))
        heXDM = np.zeros((gaugeP.shape[0], num_compartments))

        # nitrogen and helium respective m values
        n_mvalues = np.zeros((nXDM.shape[0], num_compartments))
        he_mvalues = np.zeros((heXDM.shape[0], num_compartments))
        # if a dive has both nitrogen and helium then we need to combine the m values using a weighting
        total_mvalues = np.zeros((nXDM.shape[0], num_compartments))

        GF_Lows = np.zeros((n_mvalues.shape[0], num_compartments))
        GF_Highs = np.zeros(num_compartments)

        GF_Lows_final = np.zeros(num_compartments)

        # if compartment never hits 100% of its m value then leave value as N/A
        gf_100D = "N/A"
        first_miss = "N/A"
        try:
            for i in range(gaugeP.shape[0]):
                gaugeP[i] = data[1][i]/10
                for j in range(num_compartments):
                    if(halftime_set == 'ZH-L16B'):
                        nXDM[i][j] = gaugeP[i] * dc.ZHL16B_N_DELTA[j]
                        heXDM[i][j] = gaugeP[i] * dc.ZHL16B_HE_DELTA[j]
                        n_mvalues[i][j] = (
                            dc.ZHL16B_N_M_NAUGHT[j]/10) + nXDM[i][j]
                        he_mvalues[i][j] = (
                            dc.ZHL16B_HE_M_NAUGHT[j]/10) + heXDM[i][j]

                        GF_Highs[j] = (surf_vals[j][4] + surf_vals[j]
                                       [5]) * (100 / (dc.ZHL16B_N_M_NAUGHT[j]/10))

                        h_val = cp[i][j+17]
                        n_val = cp[i][j]
                        total_mvalues[i][j] = (
                            (n_mvalues[i][j] * n_val) + (he_mvalues[i][j] * h_val)) / (h_val + n_val)

                    elif(halftime_set == 'ZH-L16A'):
                        nXDM[i][j] = gaugeP[i] * dc.ZHL16A_N_DELTA[j]
                        n_mvalues[i][j] = (
                            dc.ZHL16A_N_M_NAUGHT[j]/10) + nXDM[i][j]
                        GF_Highs[j] = surf_vals[j][4] * \
                            (100 / (dc.ZHL16A_N_M_NAUGHT[j]/10))

                    elif(halftime_set == 'ZH-L16C'):
                        nXDM[i][j] = gaugeP[i] * dc.ZHL16C_N_DELTA[j]
                        n_mvalues[i][j] = (
                            dc.ZHL16C_N_M_NAUGHT[j]/10) + nXDM[i][j]
                        GF_Highs[j] = surf_vals[j][4] * \
                            (100 / (dc.ZHL16C_N_M_NAUGHT[j]/10))

                    elif(halftime_set == 'DSAT'):
                        GF_Highs[j] = surf_vals[j][4] * \
                            (100 / (dc.DSAT_N_M_NAUGHT[j]/10))

                    elif(halftime_set == 'Workman65'):
                        nXDM[i][j] = gaugeP[i] * dc.WORKMAN_N_DELTA[j]
                        n_mvalues[i][j] = (
                            dc.WORKMAN_N_M_NAUGHT[j]/10) + nXDM[i][j]
                        GF_Highs[j] = surf_vals[j][4] * \
                            (100 / (dc.WORKMAN_N_M_NAUGHT[j]/10))

                    elif(halftime_set == 'Haldane'):
                        GF_Highs[j] = surf_vals[j][4] * \
                            (100 / (dc.HALDANE_M_NAUGHT/10))

                    # if buhlman must combine else just use nitrogen m values
                    if (halftime_set == 'ZH-L16B'):
                        # using total_mvalues for buhlman B as need to combine both N and He m-values
                        h_value = cp[i][j+17]
                        n_value = cp[i][j]
                        GF_Lows[i][j] = (h_value + n_value) * \
                            (100/total_mvalues[i][j])
                    elif (halftime_set == 'DSAT' or halftime_set == 'Haldane'):
                        pass
                    else:
                        GF_Lows[i][j] = (cp[i][j] / n_mvalues[i][j]) * 100

                    # compartment has hit 100% of its m value, only want the first occurence of this
                    if ((GF_Lows[i][j] >= 100) and (gf_100D == "N/A")):
                        gf_100D = data[1][i]
                        first_miss = 3 * round(gf_100D / 3)

                    # finds the GFLowMax for each value - must exclude all times when depth = 0
                    if(data[1][i] != 0):
                        if(GF_Lows[i][j] > GF_Lows_final[j]):
                            # the final GFLowNMax values
                            GF_Lows_final[j] = GF_Lows[i][j]

                # GFLowMaxMax
                GF_Lows_max_max = np.max(GF_Lows_final)

                # GFHighMax
                GF_High_max = np.max(GF_Highs)
        except IndexError:
            pass

        # '''
        # stores all necessary data in single array for return
        # in order of GFLowMaxN, GFLowMaxMax, GF100D, FirstMiss, GFHighN, GFHighMax
        # '''

        gf_values = [GF_Lows_final, GF_Lows_max_max,
                     gf_100D, first_miss, GF_Highs, GF_High_max]

        return gf_values

    def helium_inert_pressure(self, ambient_pressures, gasses, dive):
        """
        calculate inert gas partial pressure of helium at each time point

        :param ambient_pressures: float[]:
            a list of ambient pressures at each time point

        :param gasses: array:
            an array containing the gas mix in order [helium, nitrogen, oxygen]

        :returns float[]:
            the inert gas partial pressure of helium at each time point

        """
        # this will need to be changed later to get the actual value of helium
        whichtank = robjects.r['whichtank']

        heIPP = np.zeros(ambient_pressures.shape[0])
        for idx, ap in np.ndenumerate(ambient_pressures):
            if(len(gasses) == 0):
                helium = 0
            else:
                i = idx[0]
                tank_num = whichtank(dive)[i]
                h_val = gasses[tank_num - 1][2]
                helium = h_val[0]
            heIPP[idx] = ap * helium
        return heIPP

    def nitrogen_inert_pressure(self, ambient_pressures, gasses, dive):
        """
        calculate inert gas partial pressure of nitrogen at each time point

        :param ambient_pressures: float[]:
            a list of ambient pressures at each time point

        :param gasses: array:
            an array containing the gas mix in order [helium, nitrogen, oxygen]

        :returns float[]:
            the inert gas partial pressure of nitrogen at each time point
        """
        # this will need to be changed later to get the actual value of nitrogen
        print("HELLO?")
        whichtank = robjects.r['whichtank']
        nIPP = np.zeros(ambient_pressures.shape[0])
        for idx, ap in np.ndenumerate(ambient_pressures):
            if(len(gasses) == 0):
                nitrogen = 0.79
            else:
                i = idx[0]
                tank_num = whichtank(dive)[i]
                n_val = gasses[tank_num - 1][1]
                nitrogen = n_val[0]

            nIPP[idx] = ap * nitrogen
        return nIPP

    def totalIPP(self, nIPP, heIPP):
        """
        calculate the total inert gas partial pressure of nitrogen and helium at each time point

        :param niPP: float[]:
            the inert gas partial pressure of nitrogen at a given time points

        :param heIPP: float[]:
            the inert gas partial pressure of helium at a given time points

        :returns float[]:
            the total inert gas partial pressure at given time points

        """
        total_IPP = np.zeros(nIPP.shape[0])
        for idx, ni in np.ndenumerate(nIPP):
            total_IPP[idx] = ni + heIPP[idx]
        return total_IPP
