import argparse
import json
import os
from collections import namedtuple
import sys
from math import log, tan, pi, radians

# globals
Pt = namedtuple('Pt', 'x,y')
Edge = namedtuple('Edge', 'a,b')
Poly = namedtuple('Poly', 'id,name,edges')
_eps = 1e-5
_huge = sys.float_info.max
_tiny = sys.float_info.min
# neighborhood_json = "Neighborhoods_2012_polygons.json"
neighborhood_json = "neighborhoods_2018.json"


def load_json():
    file_in = open(os.getcwd() + "/" + neighborhood_json)
    d = json.load(file_in)
    return d


def spherical_mercator_projection(longitude, latitude):
    # http://en.wikipedia.org/wiki/Mercator_projection <- invented in 1569!
    # http://stackoverflow.com/questions/4287780/detecting-whether-a-gps-coordinate-falls-within-a-polygon-on-a-map
    x = -longitude
    y = log(tan(radians(pi / 4 + latitude / 2)))
    return (x, y)


def rayintersectseg(p, edge):
    # http://rosettacode.org/wiki/Ray-casting_algorithm#Python
    # takes a point p=Pt() and an edge of two endpoints a,b=Pt() of a line segment returns boolean
    a, b = edge
    if a.y > b.y:
        a, b = b, a
    if p.y == a.y or p.y == b.y:
        p = Pt(p.x, p.y + _eps)
    intersect = False

    if (p.y > b.y or p.y < a.y) or (
            p.x > max(a.x, b.x)):
        return False

    if p.x < min(a.x, b.x):
        intersect = True
    else:
        if abs(a.x - b.x) > _tiny:
            m_red = (b.y - a.y) / float(b.x - a.x)
        else:
            m_red = _huge
        if abs(a.x - p.x) > _tiny:
            m_blue = (p.y - a.y) / float(p.x - a.x)
        else:
            m_blue = _huge

        intersect = m_blue >= m_red
    return intersect


def is_odd(x):
    return x % 2 == 1


def ispointinside(p, poly):
    ln = len(poly)
    return is_odd(sum(rayintersectseg(p, edge)
                      for edge in poly.edges))


def get_all_neighbourhoods():
    d = load_json()
    shape_list = []
    for shape_idx in range(len(d['features'])):
        name = d['features'][shape_idx]['properties']['community']
        id = d['features'][shape_idx]['properties']['area_numbe']

        edges = []
        neighborhood_coordinates = d['features'][shape_idx]['geometry']['coordinates'][0][0]
        for coordinate_idx in range(len(neighborhood_coordinates) - 1):
            lon_1 = neighborhood_coordinates[coordinate_idx][0]
            lat_1 = neighborhood_coordinates[coordinate_idx][1]

            lon_2 = neighborhood_coordinates[coordinate_idx + 1][0]
            lat_2 = neighborhood_coordinates[coordinate_idx + 1][1]

            x1, y1 = spherical_mercator_projection(lon_1, lat_1)
            x2, y2 = spherical_mercator_projection(lon_2, lat_2)
            edges.append(Edge(a=Pt(x=x1, y=y1), b=Pt(x=x2, y=y2)))

        shape_list.append(Poly(id=id, name=name, edges=tuple(edges)))
    return shape_list


def find_neighbourhood(lat, long, neighborhoods):
    x, y = spherical_mercator_projection(long, lat)
    for neighborhood in neighborhoods:
        correct_neighborhood = ispointinside(Pt(x=x, y=y), neighborhood)
        if correct_neighborhood:
            return neighborhood.id, neighborhood.name
    return None, None


if __name__ == "__main__":
    all_neighborhoods = get_all_neighbourhoods()

    test_long = -87.73269978462665
    test_lat = 41.913654239126494

    neighborhood = find_neighbourhood(test_lat, test_long, all_neighborhoods)
    print(neighborhood)

'''
#example of iterating through a list of neighborhoods
#takes a few minutes to run
#mostly successful -> shows algorithm correct

all_neighborhoods = get_all_neighborhoods()

file_in = open(os.getcwd()+"/community_to_gps.txt",'rt')
file_out = open(os.getcwd()+"/parsed_community_with_polygon.txt",'wt')

header = file_in.readline()
header = header.rstrip()

print(header+'\t'+"Polygon Neighborhood",file=file_out)

for line in file_in:
	line = line.rstrip()
	row = line.split('\t')
	lat = float(row[2])
	lon = float(row[3])
	poly_neighbor = find_neighborhood(lon,lat,all_neighborhoods)
	try:
		print('\t'.join(row)+'\t'+poly_neighbor,file=file_out)
	except:
		print('\t'.join(row)+'\t'+"",file=file_out)
file_in.close()
file_out.close()
'''
