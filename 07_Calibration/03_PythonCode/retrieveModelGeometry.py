import psycopg2
import os

###### Set up DB connection here #####
conn = psycopg2.connect("host=localhost dbname=AMS user=postgres password=ia09")
# current working directory
cwd = os.getcwd()


def createVolumeDB(conn):
    cur = conn.cursor()
    cur.execute(
        """
        DROP TABLE IF EXISTS public."CS_geometry";

        CREATE TABLE public."CS_geometry"
        (
            "buildingID" character varying,
            "volume_CitySim" DOUBLE PRECISION
        )
        WITH (
            OIDS = FALSE
        )
        TABLESPACE pg_default;
        ALTER TABLE public."CS_geometry"
            OWNER to postgres;
        """
    )
    cur.close()
    conn.commit()

def retrieveVolumes(xmlRoot):
    buildingID = []
    buildingVolume = []
    for buildingRoot in xmlRoot.iter('Building'):
        ID = int(buildingRoot.get('key'))
        volume = float(buildingRoot.get('Vi'))
        buildingID.append(ID)
        buildingVolume.append(volume)

    return buildingID, buildingVolume

def insertVtoDB(xmlRoot):
    buildingID, buildingVolume = retrieveVolumes(xmlRoot)
    cur = conn.cursor()
    for i in range(len(buildingID)):
        cur.execute(
            """ INSERT INTO public."CS_geometry"
                VALUES (%s, %s)""", [buildingID[i], buildingVolume[i]]
        )
    cur.close()
    conn.commit()

def main(xmlRoot):
    createVolumeDB(conn)
    insertVtoDB(xmlRoot)

if __name__ == "__main__":
    main()