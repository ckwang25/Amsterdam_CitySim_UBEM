##############
# 1. Define input range for each constant or probabilistic parameter here and run
#    the script to insert these values into DB
# Author: Cheng-Kai Wang, Email: ckwang25@gmail.com
# Date: 13.07.2018
##############

import psycopg2
import os
import numpy as np

cwd = os.getcwd()  # current working directory

def newDB(conn):
    cur = conn.cursor()
    cur.execute(
        """
        -- Table: public."ModelInputs"

        DROP TABLE IF EXISTS public."ModelInputs";

        CREATE TABLE public."ModelInputs"
        (
            "archetype" character varying,
            "yearRange" character varying,
            "caseID" integer,
            "c_WWR" DOUBLE PRECISION,
            "c_WRR" DOUBLE PRECISION,
            "c_SW" DOUBLE PRECISION,
            "c_GSW" DOUBLE PRECISION,
            "c_Ninf" DOUBLE PRECISION,
            "c_WOR" DOUBLE PRECISION,
            "c_Gwindow" DOUBLE PRECISION,
            "c_Tmax" DOUBLE PRECISION,
            "p_Tmin" DOUBLE PRECISION,
            "p_Uroof" DOUBLE PRECISION,
            "p_Uwall" DOUBLE PRECISION,
            "p_Ufloor" DOUBLE PRECISION,
            "p_Uwindow" DOUBLE PRECISION
        )
        WITH (
            OIDS = FALSE
        )
        TABLESPACE pg_default;

        ALTER TABLE public."ModelInputs"
            OWNER to postgres;
        """
    )
    cur.close()
    conn.commit()

def insertInputs(conn, gridSize):
    Archetype = ["SFH_1964", "SFH_65_74", "SFH_75_91", "SFH_92_05", "SFH_06_14", "SFH_2015",
                 "MFH_1964", "MFH_65_74", "MFH_75_91", "MFH_92_05", "MFH_06_14", "MFH_2015",
                 "TH_1964", "TH_65_74", "TH_75_91", "TH_92_05", "TH_06_14", "TH_2015"]
    c_WWR = 0.35
    c_WRR = 0.10
    c_SW = 0.20
    c_GSW = 0.20
    c_Ninf = 0.40
    c_WOR = 0.25
    c_Tmax = 26.0
    c_Gwindow = 0.65
    p_Tmin = np.linspace(15.0, 20.0, num=gridSize)

    cur = conn.cursor()
    for type in Archetype:
        case = 0
        year = type[type.find("_")+1:]
        for idx in range(gridSize):
            p_Uroof, p_Uwall, p_Ufloor, p_Uwindow = definePinputs(year, gridSize, idx)
            for p_temp in p_Tmin:
                case += 1
                cur.execute(
                    """INSERT INTO public."ModelInputs"
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    [type, year, case, c_WWR, c_WRR, c_SW, c_GSW, c_Ninf, c_WOR, c_Gwindow, c_Tmax,
                     p_temp, p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]
                )
    cur.close()
    conn.commit()


def definePinputs(yearRang, gridSize, idx):
    error1 = 0.3
    error2 = 0.15
    if yearRang == "1964":
        p_Uroof = np.linspace(0.17, 2.41 + error1, gridSize)
        p_Uwall = np.linspace(0.22, 2.66 + error1, gridSize)
        p_Ufloor = np.linspace(0.29, 3.14 + error1, gridSize)
        p_Uwindow = np.linspace(1.8, 3.5 + error2, gridSize)
        consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]
    elif yearRang == "65_74":
        p_Uroof = np.linspace(0.17, 1.16 + error1, gridSize)
        p_Uwall = np.linspace(0.22, 2.33 + error1, gridSize)
        p_Ufloor = np.linspace(0.29, 2.88 + error1, gridSize)
        p_Uwindow = np.linspace(1.8, 3.4 + error2, gridSize)
        consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]
    elif yearRang == "75_91":
        p_Uroof = np.linspace(0.17, 0.68 + error1, gridSize)
        p_Uwall = np.linspace(0.22, 0.68 + error1, gridSize)
        p_Ufloor = np.linspace(0.29, 1.15 + error1, gridSize)
        p_Uwindow = np.linspace(1.8, 3.13 + error2, gridSize)
        consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]
    elif yearRang == "92_05":
        p_Uroof = np.linspace(0.17, 0.4 + error1, gridSize)
        p_Uwall = np.linspace(0.22, 0.4 + error1, gridSize)
        p_Ufloor = np.linspace(0.29, 0.4 + error1, gridSize)
        p_Uwindow = np.linspace(1.8, 2.08 + error2, gridSize)
        consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]
    elif yearRang == "06_14":
        p_Uroof = np.linspace(0.17, 0.25 + error1, gridSize)
        p_Uwall = np.linspace(0.22, 0.29 + error1, gridSize)
        p_Ufloor = np.linspace(0.29, 0.29 + error1, gridSize)
        p_Uwindow = np.linspace(1.8, 1.85 + error2, gridSize)
        consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]
    else:
        p_Uroof = np.linspace(0.17, 0.17 + error1, gridSize)
        p_Uwall = np.linspace(0.22, 0.22 + error1, gridSize)
        p_Ufloor = np.linspace(0.29, 0.29 + error1, gridSize)
        p_Uwindow = np.linspace(1.8, 1.8 + error2, gridSize)
        consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]

    p_Uroof = consturctionData[0][idx]
    p_Uwall = consturctionData[1][idx]
    p_Ufloor = consturctionData[2][idx]
    p_Uwindow = consturctionData[3][idx]

    return p_Uroof, p_Uwall, p_Ufloor, p_Uwindow


def main(connPsql = None):
    print "Start inserting model inputs indo DB..."
    if connPsql is not None:
        conn = connPsql
    else:
        conn = psycopg2.connect("host=localhost dbname=AMS user=postgres password=ia09")

    gridSize = 5

    newDB(conn)
    insertInputs(conn, gridSize)

    print "Model inputs successfully inserted into DB"


if __name__ == "__main__":
    main()
