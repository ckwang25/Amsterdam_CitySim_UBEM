##############
# Given Liander energy data
# the script automatically creates table and imports data into database.
# Be noted that the defined database schema here is only valid for this project.
# If encounter any encoding problem, open the data with notepad, change the encoding to "UTF-8" and save as csv.
# Author: Cheng-Kai Wang, Email: ckwang25@gmail.com
# Date: 08.07.2018
##############

import psycopg2
import os
import csv

cwd = os.getcwd()  # current working directory

fileName = 'Liander_KV_01012010'
dbName = 'Liander2009'

def importData(filePath, conn):
    cur = conn.cursor()
    cur.execute(
        """
        DROP TABLE IF EXISTS public.""" + str(dbName) + """;

        CREATE TABLE public.""" + str(dbName) + """
        (
            responsible character varying(30) COLLATE pg_catalog."default",
            grid_operator character varying(30) COLLATE pg_catalog."default",
            grid_area character varying(40) COLLATE pg_catalog."default",
            street character varying(50) COLLATE pg_catalog."default",
            postcode_from character varying(6) COLLATE pg_catalog."default",
            postcode_to character varying(6) COLLATE pg_catalog."default",
            residence character varying(25) COLLATE pg_catalog."default",
            landcode character varying(5) COLLATE pg_catalog."default",
            product_type character varying(5) COLLATE pg_catalog."default",
            consumption_segment character varying(5) COLLATE pg_catalog."default",
            connections_num integer,
            deliver_direction_perc double precision,
            physical_status_perc double precision,
            final_connection_perc double precision,
            type_connection_perc double precision,
            connection_type character varying(6) COLLATE pg_catalog."default",
            avg_annual_consumption integer,
            sjv_low_rate double precision,
            smart_meter_perc double precision,
            avg_counting_wheels double precision
        )
        WITH (
            OIDS = FALSE
        )
        TABLESPACE pg_default;

        ALTER TABLE public.""" + str(dbName) + """
            OWNER to postgres;
        """
    )

    # due to permission issue, using "INSERT" query instead of commonly used "COPY"
    with open(filePath, 'rU') as Data:
        reader = csv.reader(Data, delimiter=";")
        next(reader)  # skip first row
        for row in reader:
            emptyIndices = [i for i, x in enumerate(row) if x == '']
            for index in emptyIndices:
                row[index] = None
            cur.execute(
                """INSERT INTO public.""" + str(dbName) + """
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                row
            )

    # Delete unnecessary electricity records to speed up processing time
    cur.execute(
    """ DELETE FROM """ + str(dbName) + """
        WHERE "product_type" = 'ELK';
    """
    )

    cur.close()
    conn.commit()


# If run individual script with individual connection and file path setting, specify inside the function.
# Otherwise, it will run with the given path and connection setting specified in importAll()
def main(filePath_Statistic = None, connPsql = None):
    if filePath_Statistic and connPsql is not None:
        filePath = filePath_Statistic
        conn = connPsql
    else:
        # default file path and database connection setting
        filePath = cwd + '/../../09_Calibration/01_EnergyData/' + str(fileName) + '.csv'
        conn = psycopg2.connect("host=localhost dbname=AMS user=postgres password=ia09")

    importData(filePath, conn)


if __name__ == "__main__":
    main()


