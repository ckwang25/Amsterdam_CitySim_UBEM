##############
# 1. Define global parameter setting to perform validation simulation and analysis,
# Author: Cheng-Kai Wang, Email: ckwang25@gmail.com
# Last update: 03.10.2018
##############

import psycopg2
import os
import xml.etree.ElementTree as ET

def globalParameters():
    class GlobalSetting:
        cwd = os.getcwd()  # current working directory

        ###### Specify the most general information here ######
        conn = psycopg2.connect("host=localhost dbname=AMS user=postgres password=ia09")  # Set up DB connection here
        validationTypes = 'calibrated'
        validationYear = '2016'
        filePrefix = 'AOI_large_'
        inputXML = filePrefix + 'nonpolygon_cleaned_mUpdated.xml'
        saveToCloud = True

        # specify XML input directory
        inputDirectory = cwd + '/../02_CityModels/input/'


        ###### Specify input XML file path here ######
        treePath = ET.parse(inputDirectory + inputXML)
        xmlRoot = treePath.getroot()

        # specify XML output directory
        cloudDirectory = cwd + '/../02_CityModels/output/'
        localBaselineDirectory = 'C:\Users\IA\Desktop\CitySim_Pro\projects\AMS_Validation\BaselineXML\\'
        localCalibratedDirectory = 'C:\Users\IA\Desktop\CitySim_Pro\projects\AMS_Validation\CalibratedXML\\'

        # specify baseline, calibrated updated xml name here
        baselineXML = filePrefix + 'baseline_updated_' + str(validationYear) + '.xml'
        calibratedXML = filePrefix + 'calibrated_updated_' + str(validationYear) + '.xml'


        ##### Related to runCitySim_Validation script #####
        # specify CitySim simulation output file path
        baselineOutputPath = 'C:\Users\IA\desktop\CitySim_Pro\projects\AMS_Validation\\Baseline_' + str(validationYear) + '\\' \
                     + filePrefix + 'baseline_updated_' + str(validationYear) + '_YearlyResultsPerBuilding.out'
        calibratedOutputPath = 'C:\Users\IA\desktop\CitySim_Pro\projects\AMS_Validation\\Posterior_' + str(validationYear) + '\\' \
                               + filePrefix + 'calibrated_updated_' + str(validationYear) + '_YearlyResultsPerBuilding.out'

        # specify DB name to store CitySim simulation result
        validationBaseline = "Validation_Baseline_" + str(validationYear)
        validationCalibrated = "Validation_Calibrated_" + str(validationYear)


        ##### Related to resultCleaning script #####
        csvBaselinePath = cwd + '/../04_Results/Validation_Baseline_' + str(validationYear) +'.csv'
        csvCalibratedPath = cwd + '/../04_Results/Validation_Calibrated_' + str(validationYear) + '.csv'


    return GlobalSetting

if __name__ == '__main__':
    globalParameters()