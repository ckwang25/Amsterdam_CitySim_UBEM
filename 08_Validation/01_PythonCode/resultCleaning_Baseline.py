import os
import pandas as pd
import psycopg2
from globalSetting import globalParameters


# import global parameter setting
gParameter = globalParameters()
conn = gParameter.conn
cwd = gParameter.cwd
simulationYear = gParameter.validationYear
validationTypes = gParameter.validationTypes

def normalizedLianderPC6consumption(year):
    cur = conn.cursor()
    cur.execute(
        """
            DROP TABLE IF EXISTS public."PC6_"""+ str(year) + """";

            CREATE TABLE public."PC6_"""+ str(year) + """"
                (postcode character varying(30) COLLATE pg_catalog."default",
                 pc6_vsum double precision,
                 L_pc6_consumption_kwh_m3 double precision);
                
            INSERT INTO public."PC6_"""+ str(year) + """" 
            SELECT tb3."postcodes", tb3."pc6_vsum", tb3."pc6_consumption_kwh_m3"
            FROM
                        
            (SELECT 
            *, 
            lianderData."avg_annual_consumption"*baselayer."addressnumsum"*1.02264*39.2/(3.6*baselayer."pc6_vsum") as pc6_consumption_kwh_m3
            
            FROM
            (SELECT "postcodes", sum("address_num"::decimal) as addressnumSum, 
            sum("b_area"::decimal) as PC6_areaSum, sum("volume"::decimal) as PC6_vSum,
            string_agg("archetype", ', ') as archetypes
             
            FROM "BuildingBaselayer"
            WHERE "datacomplete" = '1'
            GROUP BY "postcodes") as baselayer
            
            JOIN
            
            (SELECT "postcode_to", "connections_num", "avg_annual_consumption"
            FROM "liander""" + str(year) + """"
            WHERE "postcode_from" = "postcode_to"
            AND "deliver_direction_perc" = 100
            AND "physical_status_perc" = 100) as lianderData 
            
            ON baselayer."postcodes" = lianderData."postcode_to"
            
            WHERE 
            baselayer."addressnumsum" = lianderData."connections_num" or 
            abs(baselayer."addressnumsum"-lianderData."connections_num") = 1
            ) as tb3
           """
    )
    cur.close()
    conn.commit()


def normalizeSimuPC6consumption(year):
    cur = conn.cursor()
    cur.execute(
        """
            SELECT 
            max(PC6list."postcode") as postcode, 
            max(PC6list."mainarchetype") as archetype,
            avg(PC6list."l_pc6_consumption_kwh_m3") as l_pc6_consumption_kwh_m3, 
            sum(simu."Baseline_""" + str(year) + """_h_wh")/(1000*avg(PC6list."pc6_vsum")) as Baseline_""" + str(year) + """_kWh_m3
            
            FROM
            (
                select tb1.*, tb2."mainarchetype"
                from "PC6_""" + str(year) + """" as tb1 join "PC6_Archetype" as tb2
                on tb1."postcode" = tb2."postcode"
            ) as PC6list
            
            JOIN
            (
                select tb2."postcodes", tb1.*
                from "Baseline_""" + str(year) + """results" as tb1
                join "BuildingBaselayer" as tb2
                on tb1."buildingID" = tb2."buildingid"
                where tb2."datacomplete" = '1'
            ) as simu
           
            ON simu."postcodes" = PC6list."postcode"
            GROUP BY simu."postcodes"
       """
    )
    data = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    retrieved = pd.DataFrame(data, columns=colnames)
    cur.close()
    conn.commit()

    return retrieved


def computePC6archetype():
    cur = conn.cursor()
    # Create new table to store pc6 main archetype
    cur.execute(
        """
            DROP TABLE IF EXISTS public."PC6_Archetype";

            CREATE TABLE public."PC6_Archetype"
                (postcode character varying(30) COLLATE pg_catalog."default",
                 mainArchetype character varying(30) COLLATE pg_catalog."default");
        """
    )
    # Retrieve data from existing table
    cur.execute(
        """
            select distinct "postcodes", string_agg("volume",',') as volumes, string_agg("archetype", ',') as archetypes
            from "BuildingBaselayer"
            where "datacomplete" = '1'
            group by "postcodes"
        """
    )
    data = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    retrieved = pd.DataFrame(data, columns=colnames)

    for i in range(len(retrieved)):
        postcode = retrieved.loc[i, 'postcodes']
        archetypeList = retrieved.loc[i, 'archetypes'].split(',')
        mainArchetype = max(archetypeList, key=archetypeList.count)
        cur.execute(
            """
                INSERT INTO public."PC6_Archetype"
                VALUES (%s,%s)""",
                [postcode, mainArchetype]
        )
    cur.close()
    conn.commit()


def main():
    if validationTypes == 'baseline':
        csvPath = gParameter.csvBaselinePath
    else:
        csvPath = gParameter.csvCalibratedPath

    computePC6archetype()
    normalizedLianderPC6consumption(simulationYear)
    normalizeSimuPC6consumption(simulationYear).to_csv(csvPath)

main()

