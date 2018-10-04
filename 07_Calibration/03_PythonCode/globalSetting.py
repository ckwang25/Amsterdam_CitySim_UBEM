##############
# 1. Define global setting of running calibration scripts, this includes file path, simulation year, and so on
# Author: Cheng-Kai Wang, Email: ckwang25@gmail.com
# Date: 22.09.2018
##############

import xml.etree.ElementTree as ET
import psycopg2

def globalParameters():
    cwd = 'C:\\Users\\IA\\Google Drive\\Master Studies\\03. TU Delft\\09. Graduation\\spatio-temporal-analysis\\09_Calibration' # current working directory

    class globalSetting:
        #### General setting ####
        conn = psycopg2.connect("host=localhost dbname=AMS user=postgres password=ia09")  # Set up DB connection here

        k = 2                                               # number of uncertain parameters
        gridSize = 5                                        # Divided section number of the uncertain parameter
        caseNum = gridSize**k
        simulationYear = '2014'

        #### XML updating setting ####
        localFilePath = 'C:\Users\IA/Desktop\CitySim_Pro\projects\AMS_Calibration\XMLoutputs\\'
        cloudFilePath = cwd + '\\08_CalibrationModels\\output\\'
        inputCityModelName = 'AOI_large_nonpolygon_cleaned_mUpdated.xml'
        outputCityModelPrefix = 'AOI_large_semantic_case'   # + case ID
        saveToCloud = False

        inputXMLpath = cwd + '\\08_CalibrationModels\\input\\'+ inputCityModelName
        treePath = ET.parse(inputXMLpath)
        xmlRoot = treePath.getroot()

        workingPath = cwd


        #### Model input setting ####

        #### Construction input setting ####

    return globalSetting

if __name__ == '__main__':
    globalParameters()