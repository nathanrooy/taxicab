from collections import namedtuple
from itertools import compress

from networkx import shortest_path as nx_shortest_path
from osmnx.distance import great_circle, nearest_edges
from osmnx.routing import route_to_gdf
from shapely.geometry import LineString, Point
from shapely.ops import substring


taxi_route = namedtuple('route', ['length', 'nodes', 'orig_edge', 'dest_edge'])


def l2_dist(p1, p2):
    return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**0.5


def compute_linestring_length(ls):
    '''
    Computes the length of a partial edge (shapely linesting)
    
    Parameters
    ----------
    ls : shapely.geometry.linestring.LineString

    Returns
    -------
    float : partial edge length distance in meters
    '''

    if type(ls) == LineString:
        x, y = zip(*ls.coords)
    
        dist = 0
        for i in range(0, len(x)-1):
            dist += great_circle(y[i], x[i], y[i+1], x[i+1])
        return dist
    else: return None


def compute_taxi_length(G, nx_route, orig_partial_edge, dest_partial_edge):
    '''
    Computes the route complete taxi route length
    '''

    dist = 0
    if len(nx_route) > 1:
        dist += float(route_to_gdf(G, nx_route)['length'].sum())
    if orig_partial_edge:
        dist += compute_linestring_length(orig_partial_edge)
    if dest_partial_edge:
        dist += compute_linestring_length(dest_partial_edge)
    return dist


def create_partial_edge(route_terminus_pt, anchor_pt, edge, mode) -> LineString:
    '''
    Creates a partial edge if it exits
    
    Parameters
    ----------
    route_terminus_pt : shapely.geometry.Point
        The point along the route for which the partial edge should connect to.
    anchor_pt : shapely.geometry.Point
        The origin or destination point.
    mode : string
        "orig" -> partial edge coordiantes are moving towards the route_terminus_pt
        "dest" -> partial edge coordiantes are moving away from the route_terminus_pt

    Returns
    -------
    shapely.geometry.linestring.LineString or None
    '''

    # compute partial edge length
    partial_edge_length = edge.project(anchor_pt, normalized=True)

    # when the anchor point is closer to the first or last nodes in the edge
    # rather than some midway point along the edge, then there is no partial
    # edge to compute.
    if partial_edge_length == 0 or partial_edge_length == 1:
        return None

    # construct partial edges
    partial_edges = [
        substring(edge, partial_edge_length, 1, normalized=True),
        substring(edge, 0, partial_edge_length, normalized=True)
    ]

    # compute distances from each partial edge node to the route terminus
    dists = [
        [
            l2_dist(route_terminus_pt, Point(partial_edges[0].coords[ 0])),
            l2_dist(route_terminus_pt, Point(partial_edges[0].coords[-1]))
        ],
        [
            l2_dist(route_terminus_pt, Point(partial_edges[1].coords[ 0])),
            l2_dist(route_terminus_pt, Point(partial_edges[1].coords[-1]))
        ]
    ]

    # determine which partial edge is closer to the route terminus
    correct_partial_edge = 0
    if min(dists[0]) > min(dists[1]):
        correct_partial_edge = 1

    # determine the ordering of the partial edge
    reverse = False
    if dists[correct_partial_edge][0] < dists[correct_partial_edge][1] and mode == "orig":
        reverse = True

    elif dists[correct_partial_edge][0] > dists[correct_partial_edge][1] and mode == "dest":
        reverse = True

    # return the partial edge with correct coordinate ordering
    if reverse:
        return partial_edges[correct_partial_edge].reverse()
    else:
        return partial_edges[correct_partial_edge]


def shortest_path(G, orig_yx, dest_yx):
    '''
    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    orig_yx : tuple
        the (lat, lng) or (y, x) point representing the origin of the path
    dest_yx : tuple
        the (lat, lng) or (y, x) point representing the destination of the path
    
    Returns
    -------
    named tuple
        (route_dist, route, orig_edge_p, dest_edge_p)
    '''

    p_orig = Point(orig_yx[::-1])
    p_dest = Point(dest_yx[::-1])

    # determine nearest edges
    orig_edge, dest_edge = (
        nearest_edges(
            G, [orig_yx[1], dest_yx[1]], [orig_yx[0], dest_yx[0]]
        )
    )
    
    # routing along the same edge
    if sorted(orig_edge) == sorted(dest_edge):
        edge_geo = G.edges[orig_edge]['geometry']
        orig_clip = edge_geo.project(p_orig, normalized=True)
        dest_clip = edge_geo.project(p_dest, normalized=True)
        orig_partial_edge = substring(edge_geo, orig_clip, dest_clip, normalized=True)  
        dest_partial_edge = None
        shortest_common_path = []

    # routing across multiple edges
    else:

        # compute the shortest common route
        r1 = nx_shortest_path(G, orig_edge[0], dest_edge[1], 'length')
        r2 = nx_shortest_path(G, orig_edge[1], dest_edge[0], 'length')
        shortest_common_path = list(compress(r1, map(lambda x: x in r2, r1)))
        
        # determine the partial edges
        orig_partial_edge = create_partial_edge(
            Point([G.nodes[shortest_common_path[0]]['x'], G.nodes[shortest_common_path[0]]['y']]),
            p_orig,
            G.edges[orig_edge]['geometry'],
            mode="orig"
        )

        dest_partial_edge = create_partial_edge(
            Point([G.nodes[shortest_common_path[-1]]['x'], G.nodes[shortest_common_path[-1]]['y']]),
            p_dest,
            G.edges[dest_edge]['geometry'],
            mode="dest"
        )

    # compute final route distance and return
    route_dist = compute_taxi_length(G, shortest_common_path, orig_partial_edge, dest_partial_edge)    
    return taxi_route(route_dist, shortest_common_path, orig_partial_edge, dest_partial_edge)

