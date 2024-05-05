import math
import re

from pykml import parser
from bin.PlaceMark import PlaceMark
from bin.figure.type.Line import Line


def getDistance(lon1, lat1, lon2, lat2):
    fi1 = lat1 * math.pi / 180
    fi2 = lat2 * math.pi / 180
    dfi = abs(lat2 - lat1) * math.pi / 180
    dlaymda = abs(lon2 - lon1) * math.pi / 180
    a = math.sin(dfi/2)**2 + math.sin(dlaymda/2)**2 * math.cos(fi1) * math.cos(fi2)
    return 6371*10**3 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def getCoordsOnPicture(coordinates, lon_lat_left_up, lon_lat_right_down):
    data = []
    for coord in coordinates:
        if lon_lat_left_up[0] <= coord[0] <= lon_lat_right_down[0] and lon_lat_right_down[1] <= coord[1] <= lon_lat_left_up[1]:
            data.append(coord)
    return data

def searchCoordinates(child):
    coord = ""
    try:
        coord = child.Polygon.outerBoundaryIs.LinearRing.coordinates.text
    except:
        pass
    try:
        coord = child.Point.coordinates.text
    except:
        pass
    try:
        coord = child.LineString.coordinates.text
    except:
        pass

    coord = coord.split(' ')
    coords = []
    for i in range(len(coord)):
        coords.append([float(coord[i].split(",")[0]), float(coord[i].split(",")[1])])
    return coords

def parseXml(kml):
    data = []
    styles = {}
    with open(kml, 'r') as f:
        root = parser.parse(f).getroot()

    try:
        for child in root.Document.Style:
            styles[child.get('id')] = child.IconStyle.Icon.href.text
    except:
        pass

    try: main = root.Document.Placemark
    except: pass
    try: main = root.Document.Folder.Placemark
    except: pass
    for child in main:
        try: name = child.name.text
        except: name = "Без имени"
        placeMark = PlaceMark(name)
        placeMark.setFigure(Line(searchCoordinates(child)))
        try:
            if child.styleUrl.text[1:] in styles.keys():
                placeMark.setIconHref(styles.get(child.styleUrl.text[1:]))
        except: pass
        try:
            if child.description.text != None:
                pichref = re.findall(r'src="(.+?)"', child.description.text)
                placeMark.setPicHref(pichref[0])
        except: pass
        try:
            placeMark.setIconHref(child.Style.IconStyle.Icon.href.text)
        except: pass
        data.append(placeMark)
    return data
