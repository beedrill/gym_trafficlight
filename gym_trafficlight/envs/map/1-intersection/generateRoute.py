# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET

def create_route(col,row,name, end = 3600, ns_p = 0.2, sn_p = 0.2, ew_p = 0.2, we_p = 0.6):
    ns_routes = []
    sn_routes = []
    ew_routes = []
    we_routes = []
    routes = ET.Element('routes')
    vtype = ET.SubElement(routes,'vType', decel="4.5",accel="2", id="Car", maxSpeed="100.0", sigma="0.5", length="5.0")
    for c in range(2,col):
        route_string = ''
        for r in range(1,row):
            route_string += 'e_{}_{}_{}_{} '.format(c,r,c,r+1)

        route_string = route_string.strip()
        vars()['routesn{}'.format(c)] = ET.SubElement(routes,'route', id="route_sn_{}".format(c), edges = route_string)
        sn_routes.append("route_sn_{}".format(c))
        
        route_string = ''
        for r in range(row,1,-1):
            route_string += 'e_{}_{}_{}_{} '.format(c,r,c,r-1)
        route_string = route_string.strip()
        vars()['routens{}'.format(c)] = ET.SubElement(routes,'route', id="route_ns_{}".format(c), edges = route_string)
        ns_routes.append("route_ns_{}".format(c))
        
    for r in range(2,row):
        route_string = ''
        for c in range(1,col):
            route_string += 'e_{}_{}_{}_{} '.format(c,r,c+1,r)
        route_string = route_string.strip()
        vars()['routewe{}'.format(r)] = ET.SubElement(routes,'route', id="route_we_{}".format(r), edges = route_string)
        we_routes.append("route_we_{}".format(r))
        
        route_string = ''
        for c in range(col,1,-1):
            route_string += 'e_{}_{}_{}_{} '.format(c,r,c-1,r)
        route_string = route_string.strip()
        vars()['routeew{}'.format(r)] = ET.SubElement(routes,'route', id="route_ew_{}".format(r), edges = route_string)
        ew_routes.append("route_ew_{}".format(r))
    
    for rid in ns_routes:
        fname = rid.replace('route','flow')
        vars()[fname] = ET.SubElement(routes,'flow', id = fname, depart = "1",begin = '0', end = str(end), type = "Car", route = rid, probability = str(ns_p))
        
    for rid in sn_routes:
        fname = rid.replace('route','flow')
        vars()[fname] = ET.SubElement(routes,'flow', id = fname, depart = "1",begin = '0', end = str(end), type = "Car", route = rid, probability = str(sn_p))
        
    for rid in ew_routes:
        fname = rid.replace('route','flow')
        vars()[fname] = ET.SubElement(routes,'flow', id = fname, depart = "1",begin = '0', end = str(end), type = "Car", route = rid, probability = str(ew_p))
        
    for rid in we_routes:
        fname = rid.replace('route','flow')
        vars()[fname] = ET.SubElement(routes,'flow', id = fname, depart = "1",begin = '0', end = str(end), type = "Car", route = rid, probability = str(we_p))
    
    tree = ET.ElementTree(routes)
    tree.write("{}.rou.xml".format(name))
    
if __name__=="__main__":
    #this will create for 5x1 mahattan grid
    col = 3
    row = 3
    name = 'traffic'
    create_route(col,row,name, ns_p = 0.2, sn_p = 0.2, ew_p = 0.2, we_p = 0.6)

