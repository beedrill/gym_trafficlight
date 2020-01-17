import xml.etree.ElementTree as ET

filename = 'traffic-14.rou.xml'
outputname = 'traffic-14-1.rou.xml'
factor = 1.1

tree = ET.parse(filename)
root = tree.getroot()
for child in root.findall('flow'):
    prob = float(child.attrib['probability'])
    prob *= factor
    #print(dt)
    child.attrib['probability'] = str(prob)

tree.write(outputname)
print('done ... !')
