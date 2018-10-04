##############
# 1. Given CBS statistic at postcode 6 level (currently year 2008-10)
#    the script automatically creates table and imports data into database.
# 2. Be noted that the defined database schema here is only valid for this project.
# 3. If encounter any encoding problem, open the data with notepad, change the encoding to "UTF-8" and save as csv.
# 4. Before using CBS data, be noted that in order to smoothly insert CBS data into database,
#    the table was cleaned up a bit and different from raw file.
# Author: Cheng-Kai Wang, Email: ckwang25@gmail.com
# Date: 09.07.2018
##############

import psycopg2
import os
import csv

cwd = os.getcwd()  # current working directory

def importData(filePath, conn):
    cur = conn.cursor()
    cur.execute(
        """
        -- Table: public."EnergyData_pc6"

        DROP TABLE IF EXISTS public."CBS_pc6_08_10";

        CREATE TABLE public."CBS_pc6_08_10"
        (
            "postcode" character varying,
            "gemeentecode" integer,
            "Oad2010" integer,
            "Sted" integer,
            "aantal_inwoners" integer,
            "aantal_mannen" integer,
            "aantal_vrouwen" integer,
            "perc_00_14" integer,
            "perc_15_24" integer,
            "perc_25_44" integer,
            "perc_45_64" integer,
            "perc_65_74" integer,
            "perc_75_ouder" integer,
            "nietwestersallochtoon" integer,
            "eenpersoonshuishouden_perc" integer,
            "eenouderhuishouden_perc" integer,
            "meerpzonderkinderen_perc" integer,
            "tweeouderhuishouden_perc" integer,
            "woningvrd" integer,
            "gemwoningwaarde" integer,
            "aantal_parthh" integer
        )
        WITH (
            OIDS = FALSE
        )
        TABLESPACE pg_default;

        ALTER TABLE public."CBS_pc6_08_10"
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
                """INSERT INTO public."CBS_pc6_08_10"
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                row
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
        filePath = cwd + '/../../01_Datasets/03_Statistics/CBS_pc6_08_10/EindbestandDemRenV.csv'
        conn = psycopg2.connect("host=localhost dbname=AMS user=postgres password=ia09")

    importData(filePath, conn)


if __name__ == "__main__":
    main()
