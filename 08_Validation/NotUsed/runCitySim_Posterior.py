import os
import psycopg2
from shutil import copy
import csv
import time
from globalSetting import globalParameters


# import global parameter setting
gParameter = globalParameters()
conn = gParameter.conn
cwd = gParameter.cwd
simulationYear = gParameter.validationYear
saveToCloud = gParameter.saveToCloud
calibratedOutputPath = gParameter.calibratedOutputPath

def createDB(conn, simulationYear):
    cur = conn.cursor()
    cur.execute(
        """
        DROP TABLE IF EXISTS public."Posterior_""" + str(simulationYear) + """results";
        CREATE TABLE public."Posterior_""" + str(simulationYear) + """results"
        (
            "buildingID" character varying,
            "Posterior_""" + str(simulationYear) + """_h_wh" DOUBLE PRECISION
        )
        WITH (OIDS = FALSE)
        TABLESPACE pg_default;
        ALTER TABLE public."Posterior_""" + str(simulationYear) + """results"
            OWNER to postgres;
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
def resultToDB(conn, calibratedOutputPath, simulationYear):
    cur = conn.cursor()
    annualBuildingHeating = retrieveResult(calibratedOutputPath)
    for buildingID in annualBuildingHeating.keys():
        cur.execute("""INSERT INTO public."Posterior_""" + str(simulationYear) + """results"
                       VALUES (%s, %s)""",
                    [buildingID, annualBuildingHeating[buildingID]])
    print "Sucessfully inserting results to DB..."
    cur.close()
    conn.commit()

def runSimulations(N, fileName, simulationYear):
    print "Start runing CitySim..."
    # perform N simulation runs
    for i in range(N):
        i += 1
        cliPath = 'C:\Users\IA\desktop\CitySim_Pro\projects\AMS_Validation\weatherFiles\Schiphol_' + str(simulationYear) + '.cli'
        horPath = 'C:\Users\IA\desktop\CitySim_Pro\projects\AMS_Validation\weatherFiles\Schiphol.hor'
        srcPath = 'C:\Users\IA\desktop\CitySim_Pro\projects\AMS_Validation\PosteriorXML\\' + str(fileName) + '_updated_' + str(simulationYear) + '_posterior.xml'
        dstPath = 'C:\Users\IA\desktop\CitySim_Pro\projects\AMS_Validation\\Posterior_' + str(simulationYear)

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
            command = 'cd C:\Users\IA\desktop\CitySim_Pro\ && CitySimPro.exe projects\AMS_Validation\\Posterior_' + str(
                simulationYear) + '\\' + str(fileName) + '_updated_' + str(simulationYear) + '_posterior.xml'
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


def main(N):
    simulationYear = '2017'
    fileName = 'AMS_Small'
    conn = psycopg2.connect("host=localhost dbname=AMS user=postgres password=ia09")

    createDB(conn, simulationYear)
    runSimulations(N, fileName, simulationYear)
    resultToDB(conn, fileName, simulationYear)


if __name__ == "__main__":
    main()




