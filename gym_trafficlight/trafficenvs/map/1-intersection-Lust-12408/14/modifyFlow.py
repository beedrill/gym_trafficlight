import xml.etree.ElementTree as ET

filename = 'traffic.rou.xml'
tree = ET.parse(filename)
root = tree.getroot()
for c in root.findall('flow'):
    c.set('departLane','best')
tree.write('a.rou.xml')
