##############
# 1. By changing the globalSetting, this script can execute CitySim simulation for the baseline case or the
#    calibrated case, adjusting validation year, file path and so on
# Author: Cheng-Kai Wang, Email: ckwang25@gmail.com
# Last update: 04.10.2018
##############

import os
from shutil import copy
import csv
import time
from globalSetting import globalParameters


# import global parameter setting
gParameter = globalParameters()
conn = gParameter.conn
cwd = gParameter.cwd
simulationYear = gParameter.validationYear
validationTypes = gParameter.validationTypes


def createDB(conn, DBname):
    cur = conn.cursor()
    cur.execute(
        """
        DROP TABLE IF EXISTS public.""" + DBname + """;
        CREATE TABLE public.""" + DBname + """
        (
            "buildingID" character varying,
            " """ + DBname + """_h_wh" DOUBLE PRECISION
        );
        """
    )
    cur.close()
    conn.commit()


## The funstion retrieve annual heating result from the output file
def retrieveResult(filePath):
    annualBuildingHeating = {}
    with open(filePath, 'rU') as Data:
        reader = csv.reader(Data, delimiter="\t")
        next(reader)
        for row in reader:
            buildingID = row[0][row[0].find('(')+1:-2]
            annualHeating = float(row[1])
            annualBuildingHeating[buildingID] = annualHeating
    return annualBuildingHeating


## The function is usded to write the annual consumption results to DB
def resultToDB(conn, DBname, outputPath):
    cur = conn.cursor()
    annualBuildingHeating = retrieveResult(outputPath)
    for buildingID in annualBuildingHeating.keys():
        cur.execute("""INSERT INTO public.""" + DBname + """VALUES (%s, %s)""",
                    [buildingID, annualBuildingHeating[buildingID]])

    print "Successfully inserting simulation results to DB..."
    cur.close()
    conn.commit()

def runSimulations(CitySimXML, folderName, simulationYear):
    print "Start running CitySim with the input file: ", str(CitySimXML)

    cliPath = 'C:\Users\IA\desktop\CitySim_Pro\projects\AMS_Validation\weatherFiles\Schiphol_' + str(simulationYear) + '.cli'
    horPath = 'C:\Users\IA\desktop\CitySim_Pro\projects\AMS_Validation\weatherFiles\Schiphol.hor'
    srcPath = 'C:\Users\IA\desktop\CitySim_Pro\projects\AMS_Validation\\' + str(folderName) + 'XML\\' + CitySimXML
    dstPath = 'C:\Users\IA\desktop\CitySim_Pro\projects\AMS_Validation\\' + str(folderName) + '_' + str(simulationYear)

    # create a folder for each simulation run
    if not os.path.exists(dstPath):
        os.makedirs(dstPath)
        # copy source XML files to each folder
        copy(srcPath, dstPath)
        # copy cli and hor file to each folder
        copy(cliPath, dstPath)
        copy(horPath, dstPath)

        # let program wait a bit to make sure each simulation run is complete
        time.sleep(0.005)
        # run CitySim: first navigate to CitySim_Pro dir and then execute CitySimPro
        command = 'cd C:\Users\IA\desktop\CitySim_Pro\ && CitySimPro.exe projects\AMS_Validation\\' + str(folderName) + \
                  '_' + str(simulationYear) + '\\' + CitySimXML
        os.system(command)

        # only few output files are needed, the rest will be delete to save storage space
        for the_file in os.listdir(dstPath):
            file_path = os.path.join(dstPath, the_file)
            if os.path.isfile(file_path):
                # keep those files in the folder
                if file_path.endswith('.xml') or \
                        file_path.endswith('YearlyResultsPerBuilding.out') or \
                        file_path.endswith('Area.out') or \
                        file_path.endswith('.log'):
                    continue
                else:
                    os.unlink(file_path)


def main():
    if validationTypes == 'baseline':
        DBname = gParameter.validationBaseline
        CitySimXML = gParameter.baselineXML
        folderName = 'Baseline'
        outputPath = gParameter.baselineOutputPath
    else:
        DBname = gParameter.validationCalibrated
        CitySimXML = gParameter.calibratedXML
        folderName = 'Calibrated'
        outputPath = gParameter.calibratedOutputPath

    createDB(conn, DBname)
    runSimulations(CitySimXML, folderName, simulationYear)
    resultToDB(conn, DBname, outputPath)


if __name__ == "__main__":
    main()




