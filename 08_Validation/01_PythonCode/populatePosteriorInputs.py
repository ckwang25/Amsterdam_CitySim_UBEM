##############
# 1. Define input values based on the posterior peak values obtained from the training phase
# Author: Cheng-Kai Wang, Email: ckwang25@gmail.com
# Date: 06.08.2018
##############

import psycopg2
import os
import numpy as np

cwd = os.getcwd()  # current working directory

def newDB(conn):
    cur = conn.cursor()
    cur.execute(
        """
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
            "c_WOR" DOUBLE PRECISION,
            "c_Gwindow" DOUBLE PRECISION,
            "c_Tmax" DOUBLE PRECISION,
            "c_Uroof" DOUBLE PRECISION,
            "c_Uwall" DOUBLE PRECISION,
            "c_Ufloor" DOUBLE PRECISION,
            "c_Uwindow" DOUBLE PRECISION,
            "p_Tmin" DOUBLE PRECISION,
            "p_Ninf" DOUBLE PRECISION
        );
        """
    )
    cur.close()
    conn.commit()

def insertInputs(conn, gridSize):
    Archetype = ["SFH_1964", "SFH_65_74", "SFH_75_91", "SFH_92_05", "SFH_06_14", "SFH_2015",
                 "MFH_1964", "MFH_65_74", "MFH_75_91", "MFH_92_05", "MFH_06_14", "MFH_2015",
                 "TH_1964", "TH_65_74", "TH_75_91", "TH_92_05", "TH_06_14", "TH_2015"]
    c_WWR = 0.21        # Ecofys
    c_WRR = 0.00        # CS default
    c_SW = 0.20         # CS default
    c_GSW = 0.20        # CS default
    c_WOR = 0.25        # guess
    c_Tmax = 26.0       # doesn't matter
    c_Gwindow = 0.76    # Ecofys
    p_Tmin = np.linspace(15.0, 20.0, num=gridSize)  # Leidelmeijer
    p_Ninf = np.linspace(0.19, 0.81, num=gridSize)  # Alfano et al.

    cur = conn.cursor()
    for type in Archetype:
        case = 0
        yearRange = type[type.find("_")+1:]
        c_Uroof, c_Uwall, c_Ufloor, c_Uwindow = envelopeInputs(yearRange)
        for p_temp in p_Tmin:
            for p_inf in p_Ninf:
                case += 1
                cur.execute(
                    """INSERT INTO public."ModelInputs"
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    [type, yearRange, case, c_WWR, c_WRR, c_SW, c_GSW, c_WOR, c_Gwindow, c_Tmax,
                     c_Uroof, c_Uwall, c_Ufloor, c_Uwindow, p_temp, p_inf]
                )
    cur.close()
    conn.commit()


def envelopeInputs(yearRang):
    if yearRang == "1964":
        c_Uroof = 1.675
        c_Uwall = 1.7625
        c_Ufloor = 1.755
        c_Uwindow = 2.9
    elif yearRang == "65_74":
        c_Uroof = 0.89
        c_Uwall = 1.45
        c_Ufloor = 2.09
        c_Uwindow = 2.9
    elif yearRang == "75_91":
        c_Uroof = 0.64
        c_Uwall = 0.64
        c_Ufloor = 0.935
        c_Uwindow = 2.9
    elif yearRang == "92_05":
        c_Uroof = 0.36
        c_Uwall = 0.36
        c_Ufloor = 0.35
        c_Uwindow = 1.8
    elif yearRang == "06_14":
        c_Uroof = 0.23
        c_Uwall = 0.27
        c_Ufloor = 0.265
        c_Uwindow = 1.8
    else:
        c_Uroof = 0.16
        c_Uwall = 0.21
        c_Ufloor = 0.265
        c_Uwindow = 1.8

    return c_Uroof, c_Uwall, c_Ufloor, c_Uwindow


def main(connPsql = None):
    print "Start inserting calibrated model inputs indo DB..."

    conn = psycopg2.connect("host=localhost dbname=AMS user=postgres password=ia09")

    gridSize = 5

    newDB(conn)
    insertInputs(conn, gridSize)

    print "Calibrated model inputs successfully inserted into DB"


if __name__ == "__main__":
    main()
