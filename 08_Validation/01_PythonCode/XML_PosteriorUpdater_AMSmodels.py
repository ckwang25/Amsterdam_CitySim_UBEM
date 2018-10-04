import pandas as pd
import retrieveModelGeometry
import populateXMLConstruction
from globalSetting import globalParameters

# import global parameter setting
gParameter = globalParameters()
conn = gParameter.conn
cwd = gParameter.cwd
inputXML = gParameter.inputXML
calibratedXML = gParameter.calibratedXML
simulationYear = gParameter.validationYear
saveToCloud = gParameter.saveToCloud
xmlRoot = gParameter.xmlRoot
treePath = gParameter.treePath


def queryBuildingInfo(buildingID):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT base.*, posterior."post_Tmin", posterior."post_Ninf", posterior."trainingTimes"
        FROM
            (select tb1.*, tb2.*
            from "BuildingBaselayer" as tb1 join "BaselineInputs" as tb2
            on tb1."archetype" = tb2."archetype"
            where tb1."datacomplete" = '1' 
            and tb2."caseID" = 1) 
            as base
        LEFT JOIN
            (select *
            from "PC6_PosteriorInputs")
            as posterior
        ON base."postcodes" = posterior."postcode"
        
        WHERE base."buildingid" = '""" + str(buildingID) + """'
        """
    )
    data = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    retrieved = pd.DataFrame(data, columns=colnames)
    cur.close()
    conn.commit()

    return retrieved

# update building specific parameters
def updateBuildingData(buildingRoot, buildingInfo, constructionIDs, Tmin, Ninf):
    WWR = float(buildingInfo['c_WWR'])
    WRR = float(buildingInfo['c_WRR'])
    Gwindow = float(buildingInfo['c_Gwindow'])
    Uwindow = float(buildingInfo['c_Uwindow'])
    WOR = float(buildingInfo['c_WOR'])
    Tmax = float(buildingInfo['c_Tmax'])
    SW = float(buildingInfo['c_SW'])
    Num_occupants = int(buildingInfo['est_b_occupants'])
    roofType = constructionIDs['r']
    wallType = constructionIDs['w']
    floorType = constructionIDs['f']

    ### update building level data ###
    buildingRoot.set('Ninf', str(Ninf))

    ### update zoon level data ###
    for zone in buildingRoot.iter('Zone'):
        zone.set('Tmin', str(Tmin))
        zone.set('Tmax', str(Tmax))
        for occupancy in zone.iter('Occupants'):
            occupancy.set('n', str(Num_occupants))
            occupancy.set('type', str(0))
        for wall in zone.iter('Wall'):
            wall.set('type', str(wallType))
            wall.set('ShortWaveReflectance', str(SW))
            wall.set('GlazingRatio', str(WWR))
            wall.set('GlazingGValue', str(Gwindow))
            wall.set('GlazingUValue', str(Uwindow))
            wall.set('OpenableRatio', str(WOR))
        for roof in zone.iter('Roof'):
            roof.set('type', str(roofType))
            roof.set('ShortWaveReflectance', str(SW))
            roof.set('GlazingRatio', str(WRR))
            roof.set('GlazingGValue', str(Gwindow))
            roof.set('GlazingUValue', str(Uwindow))
            roof.set('OpenableRatio', str(WOR))
        for floor in zone.iter('Floor'):
            floor.set('type', str(floorType))
            floor.set('ShortWaveReflectance', str(SW))
            floor.set('GlazingGValue', str(Gwindow))
            floor.set('GlazingUValue', str(Uwindow))
            floor.set('GlazingRatio', str(0))
            floor.set('OpenableRatio', str(0))


# update CitySim XML global parameters
def updateGlobalXMLparameters(xmlRoot, simulationYear):
    # create construction composite
    populateXMLConstruction.main(xmlRoot)

    # add climate file to XML
    for Climate in xmlRoot.iter('Climate'):
        Climate.set('location', 'Schiphol_' + str(simulationYear) + '.cli')

    # update ground level information, set GSW to be constant: 0.2
    for groundSurfaceRoot in xmlRoot.iter('GroundSurface'):
        groundSurfaceRoot.set('ShortWaveReflectance', str(0.2))
        for ground in groundSurfaceRoot.iter('Ground'):
            ground.set('ShortWaveReflectance', str(0.2))

    # temporarily update construction type of all buildings (simulated, or non-simulated)
    # according to construction year majority in the baselayer. Correct types for simulated buildings
    # will be updated in the end
    for building in xmlRoot.iter('Building'):
        for zone in building.iter('Zone'):
            for roof in zone.iter('Roof'):
                roof.set('type', str(4))
            for floor in zone.iter('Floor'):
                floor.set('type', str(16))
            for wall in zone.iter('Wall'):
                wall.set('type', str(10))

def getBuildingConstructionType(xmlRoot, buildingInfo):
    constructionIDs = {}
    yearRange = str(buildingInfo['yearRange'][0])
    for composite in xmlRoot.iter('Composite'):
        compositeName = composite.get('name')
        if yearRange in compositeName:
            material = compositeName[0]
            typeID = composite.get('id')
            constructionIDs[material] = typeID
        else:
            continue
    return constructionIDs


def updateAllinOneXML(treePath, simulationYear, saveToCloud = False):

    xmlRoot = treePath.getroot()

    # These are like climate, construction data, independent from building specific data
    updateGlobalXMLparameters(xmlRoot, simulationYear)

    # Update individual building parameters
    for buildingRoot in xmlRoot.iter('Building'):
        buildingID = buildingRoot.get('key')
        # retrieve building parameter values from input space by buildingID
        buildingInfo = queryBuildingInfo(buildingID)

        # only if building data in DB and is to be simulated will be updated
        if len(buildingInfo) == 1:
            if buildingInfo['post_Tmin'].any():
                Tmin = float(buildingInfo['post_Tmin'])
                Ninf = float(buildingInfo['post_Ninf'])
            else:
                Tmin = float(buildingInfo['c_Tmin'])
                Ninf = float(buildingInfo['c_Ninf'])
            # get building construction type id according to year range
            constructionIDs = getBuildingConstructionType(xmlRoot, buildingInfo)
            updateBuildingData(buildingRoot, buildingInfo, constructionIDs, Tmin, Ninf)
        else:
            continue

    if saveToCloud == True:
        outputPath = globalParameters().cloudDirectory + calibratedXML
    else:
        outputPath = globalParameters().localCalibratedDirectory + calibratedXML

    treePath.write(outputPath)


def main():
    retrieveModelGeometry.main(xmlRoot)
    updateAllinOneXML(treePath, simulationYear, saveToCloud)


if __name__ == "__main__":
    main()