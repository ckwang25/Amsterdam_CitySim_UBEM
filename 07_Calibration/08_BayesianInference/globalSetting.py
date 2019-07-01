##############
# 1. Define global parameter setting to perform Bayesian calibration,
#    this includes file path, simulation year, and so on
# Author: Cheng-Kai Wang, Email: ckwang25@gmail.com
# Date: 30.09.2018
##############

import psycopg2
import os
import numpy as np

def globalParameters():
    class GlobalSetting:
        cwd = os.getcwd()  # current working directory

        conn = psycopg2.connect("host=localhost dbname=AMS user=postgres password=ia09")  # Set up DB connection here

        k = 2                                               # number of uncertain parameters
        gridSize = 5                                        # Divided section number of the uncertain parameter
        caseNum = gridSize**k
        simulationYear = '2014'
        trainingYears = ['2012','2013', '2014', '2015']

        # specify simulation result csv path here
        filePrefix = 'AOI_all_semantic_'
        fileDirectory = cwd + '/simulationOutputs/AOI_all/'

        # allow metered data to have 1.5 kWh/m3 deviation threshold to the simulation data
        threshold = 1.5

        # define the key uncertain input ranges
        p_Tmin = np.linspace(15.0, 20.0, num=gridSize)  # Ref: Leidelmeijer
        p_Ninf = np.linspace(0.19, 0.81, num=gridSize)  # Ref: Alfano et al.

    return GlobalSetting

if __name__ == '__main__':
    globalParameters()