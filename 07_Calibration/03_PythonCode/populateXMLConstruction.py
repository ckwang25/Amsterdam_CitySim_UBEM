import psycopg2
import pandas as pd
import os
import xml.etree.ElementTree as ET


###### Set up DB connection here #####
conn = psycopg2.connect("host=localhost dbname=AMS user=postgres password=ia09")
cwd = os.getcwd()


def queryBuildingInfo():
    cur = conn.cursor()
    cur.execute(
        """
        select distinct "yearRange", "caseID", "c_Uroof", "c_Uwall", "c_Ufloor"
        from "ModelInputs"
        where "caseID" = 1
		order by "c_Uroof"
        """
    )
    data = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    retrieved = pd.DataFrame(data, columns=colnames)
    cur.close()
    conn.commit()

    return retrieved

def createComposite(xmlRoot):
    constructionData = queryBuildingInfo()
    # composite counts for each material
    compositeCounts = len(constructionData)
    id = 0

    for district in xmlRoot.iter('District'):
        for material in ['roof', 'wall', 'floor']:
            if material == 'wall':
                for i in range(compositeCounts):
                    id += 1
                    yearRange = constructionData['yearRange'][i]
                    uMaterial = constructionData['c_U' + material][i]
                    name = str(material) + '_' + str(yearRange)

                    composite = ET.SubElement(district, 'Composite')
                    composite.set('id', str(id))
                    composite.set('name', str(name))
                    composite.set('category', str(material))

                    layer = ET.SubElement(composite, 'Layer')
                    # apply adjust equation learned from experience to Uwall
                    Uwall = 0.3369 * (uMaterial ** 2) + 0.8064 * uMaterial + 0.0371
                    layer.set('Thickness', str(1))
                    layer.set('Conductivity', str(Uwall))
                    layer.set('Cp', str(1101.59998))
                    layer.set('Density', str(1800))
                    layer.set('nre', str(0))
                    layer.set('gwp', str(0))
                    layer.set('ubp', str(0))
            else:
                for i in range(compositeCounts):
                    id += 1
                    yearRange = constructionData['yearRange'][i]
                    uMaterial = constructionData['c_U' + material][i]
                    name = str(material) + '_' + str(yearRange)

                    composite = ET.SubElement(district, 'Composite')
                    composite.set('id', str(id))
                    composite.set('Uvalue', str(uMaterial))
                    composite.set('name', str(name))
                    #composite.set('category', str(material))

    # This function allows pretty print in XML
    indent(district)


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def main(xmlRoot):
    createComposite(xmlRoot)

if __name__ == "__main__":
    main()