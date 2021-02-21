from math import atan
from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt
from math import tan

from numpy import argmin
from networkx import shortest_path as nx_shortest_path

from shapely.geometry import Point
from shapely.geometry import LineString

from osmnx.distance import get_nearest_edge
from osmnx.utils_graph import get_route_edge_attributes

from taxicab.constants import R     # haversine
from taxicab.constants import a     # vincenty
from taxicab.constants import f     # vincenty


def haversine(orig, dest):
    '''
    Compute the distance between to (lat,lng) pairs using the haversine method.
    
    Parameters
    ----------
    orig : tuple
        origin point (latitude, longitude)
    dest : tuple
        destination point (latitude, longitude)
    
    Returns
    -------
    float : distance in meters
    '''
    
    lat1, lon1 = orig
    lat2, lon2 = dest

    phi_1 = radians(lat1)
    phi_2 = radians(lat2)

    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = (sin(delta_phi/2.0)**2 + 
    cos(phi_1)*cos(phi_2) * 
    sin(delta_lambda/2.0)**2)

    c=2*atan2(sqrt(a),sqrt(1-a))

    return R * c
    

def vincenty_inverse(orig, dest, maxIter=200, tol=10**-12):
    '''
    Computes the distance between two (lat/lng) points using the iterative 
    inverse vincenty approach.

    Parameters
    ----------
    orig : tuple
        origin point (latitude, longitude)
    dest : tuple
        destination point (latitude, longitude)
        
    Returns
    -------
    dist_m : float
        distance between orig and dest in meters
    '''

    #--- CONSTANTS ------------------------------------+

    b=(1-f)*a

    phi_1, L_1 = orig
    phi_2, L_2 = dest

    u_1=atan((1-f)*tan(radians(phi_1)))
    u_2=atan((1-f)*tan(radians(phi_2)))

    L=radians(L_2-L_1)

    Lambda=L

    sin_u1=sin(u_1)
    cos_u1=cos(u_1)
    sin_u2=sin(u_2)
    cos_u2=cos(u_2)

    #--- BEGIN ITERATIONS -----------------------------+
    for i in range(0, maxIter):
        cos_lambda=cos(Lambda)
        sin_lambda=sin(Lambda)
        sin_sigma=sqrt((cos_u2*sin(Lambda))**2+(cos_u1*sin_u2-sin_u1*cos_u2*cos_lambda)**2)
        cos_sigma=sin_u1*sin_u2+cos_u1*cos_u2*cos_lambda
        sigma=atan2(sin_sigma,cos_sigma)
        sin_alpha=(cos_u1*cos_u2*sin_lambda)/sin_sigma
        cos_sq_alpha=1-sin_alpha**2
        cos2_sigma_m=cos_sigma-((2*sin_u1*sin_u2)/cos_sq_alpha)
        C=(f/16)*cos_sq_alpha*(4+f*(4-3*cos_sq_alpha))
        Lambda_prev=Lambda
        Lambda=L+(1-C)*f*sin_alpha*(sigma+C*sin_sigma*(cos2_sigma_m+C*cos_sigma*(-1+2*cos2_sigma_m**2)))

        # successful convergence
        diff=abs(Lambda_prev-Lambda)
        if diff<=tol:
            break

    u_sq=cos_sq_alpha*((a**2-b**2)/b**2)
    A=1+(u_sq/16384)*(4096+u_sq*(-768+u_sq*(320-175*u_sq)))
    B=(u_sq/1024)*(256+u_sq*(-128+u_sq*(74-47*u_sq)))
    delta_sig=B*sin_sigma*(cos2_sigma_m+0.25*B*(cos_sigma*(-1+2*cos2_sigma_m**2)-(1/6)*B*cos2_sigma_m*(-3+4*sin_sigma**2)*(-3+4*cos2_sigma_m**2)))
    dist_m = b * A * (sigma - delta_sig)
    return dist_m


def compute_partial_edge(G, route, edge, point):
    '''
    
    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    route : list
        route as a list of node IDs
    edge : tuple
        graph edge unique identifier as a tuple: (u, v, key)
    point : tuple
        a point defined as (lat, lng) or (y, x)

    Returns
    -------
    edge_pts : list
        ordered list of (lng, lat) points.
    '''

    # get edge geometry
    edge_pts = get_edge_geometry(G, edge)

    # find the index position on the edge nearest the point
    idx = find_nearest_edge_point(edge_pts, point)
            
    # first node of current edge matches first node of route (GOOD)
    if edge[0] == route[0]:
        if idx != 0: return edge_pts[:idx+1][::-1]

    # last node of current edge matches first node of route (GOOD)
    if edge[1] == route[0]:
        return edge_pts[idx:]

    # first node of current edge matches last node of route (GOOD)
    if edge[0] == route[-1]:
        return edge_pts[:idx+1]

    # last node of current edge matches last node of route (GOOD)
    if edge[1] == route[-1]:
        return edge_pts[idx:][::-1]

    return []


def compute_partial_edge_length(G, pointseq, distfunc=vincenty_inverse):
    '''
    Computes the length of a partial edge
    
    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    pointseq : list
        ordered list of (lng, lat) points.
    dist_func : function
        function used to compute distance between (lat,lng) pairs

    Returns
    -------
    float : partial edge length distance in meters
    '''
    
    dist = 0
    for i in range(0, len(pointseq)-1):
        dist += distfunc(
            (pointseq[i][0], pointseq[i][1]),
            (pointseq[i+1][0], pointseq[i+1][1]))
    return dist


def get_edge_geometry(G, edge):
    '''
    Retrieve the points that make up a given edge.
    
    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    edge : tuple
        graph edge unique identifier as a tuple: (u, v, key)
    
    Returns
    -------
    list :
        ordered list of (lng, lat) points.
    
    Notes
    -----
    In the event that the 'geometry' key does not exist within the
    OSM graph for the edge in question, it is assumed then that 
    the current edge is just a straight line. This results in an
    automatic assignment of edge end points.
    '''
    try: 
        return list(G.edges[edge]['geometry'].coords)
    
    except KeyError:
        print('keyerror')
        return [
            (G.nodes[edge[0]]['x'], G.nodes[edge[0]]['y']),
            (G.nodes[edge[1]]['x'], G.nodes[edge[1]]['y'])]


def remove_overlapping_edge(route, edge):
    '''
    Removes an edge from a route if the route contains the edge in question.
    Returns an updated route without the edge, otherwise returns the original
    route.

    Parameters
    ----------
    route : list
        route as a list of node IDs
    edge : tuple
        graph edge unique identifier as a tuple: (u, v, key)

    Returns
    -------
    route : list
        route as a list of node IDs
    '''
    # first edge of route matches current edge
    if tuple(route[:2]) == edge[:2]:
        route = route[1:][:]

    # first edge of route matches current edge (reverse)
    if tuple(route[:2]) == edge[:2][::-1]:
        pass

    # last edge of route matches current edge
    if tuple(route[-2:]) == edge[:2]:
        pass

    # last edge of route matches current edge (reverse)
    if tuple(route[-2:]) == edge[:2][::-1]:
        route = route[:-1][:]
        
    return route


def find_nearest_edge_point(edge_pts, point, dist_func=vincenty_inverse):
    '''
    Finds the edge index position of which is closest to the provided point.

    Parameters
    ----------
    edge_pts : 
    point : 

    Returns
    -------
    int :
        index value corresponding to nearest point on the edge to the provided 
        point.
    '''

    return argmin(
        [dist_func((point[0], point[1]), (y, x)) for x, y in edge_pts])


def route_across_single_edge(G, edge, orig, dest):
    '''When routing across a single network edge

    Parameters
    ----------

    Returns
    -------

    Notes
    -----
    '''

    # get edge geometry
    edge_pts = get_edge_geometry(G, edge)

    # find nearest edge point
    orig_idx = find_nearest_edge_point(edge_pts, orig)
    dest_idx = find_nearest_edge_point(edge_pts, dest)
    
    # if orig and dest share the same closest node, there is nothing to route.
    if orig_idx == dest_idx:
        print('points are too close together. try interpolating...')
        return [], [], []

    # closest points on edge aling with direction of travel
    if dest_idx > orig_idx:
        return [], edge_pts[orig_idx:dest_idx+1], []

    # closest points on edge are opposite the direction of travel
    if orig_idx > dest_idx:
        return [], edge_pts[dest_idx:orig_idx+1][::-1], []


def route_across_two_edges(G, orig_edge, dest_edge, orig, dest):
    '''ROUTE ACROSS TWO EDGES
    
    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    orig_edge : edge tuple
        edge nearest the origin point
    dest_edge: edge tuple
        edge neatest the destination point
    orig : tuple
        the (lat, lng) or (y, x) point representing the origin of the path
    dest : tuple
        the (lat, lng) or (y, x) point representing the destination of the path
    
    Returns
    -------
    tuple :
        route : empty
        orig_edge_p : partial edge
        dest_edge_p : partial edge
    '''
    
    orig_pts = get_edge_geometry(G, orig_edge)
    dest_pts = get_edge_geometry(G, dest_edge)
    orig_idx = find_nearest_edge_point(orig_pts, orig)
    dest_idx = find_nearest_edge_point(dest_pts, dest)
    
    if orig_edge[0] == dest_edge[0]:
        pass

    if orig_edge[0] == dest_edge[1]:
        pass

    # last node of first edge matches first node of second edge
    if orig_edge[1] == dest_edge[0]:
        orig_edge_p = orig_pts[orig_idx:]
        dest_edge_p = dest_pts[:dest_idx+1]

    if orig_edge[1] == dest_edge[1]:
        pass
                
    return [], orig_edge_p, dest_edge_p


def route_across_multiple_edges(G, orig_edge, dest_edge, orig, dest):
    '''
    When routing iacross three or more edges.

    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    orig_edge : tuple
       graph edge unique identifier as a tuple: (u, v, key)
    dest_edge : tuple
        graph edge unique identifier as a tuple: (u, v, key)
    orig : tuple
        the (lat, lng) or (y, x) point representing the origin of the path
    dest : tuple
        the (lat, lng) or (y, x) point representing the destination of the path

    Returns
    -------
    route :
    orig_edge_p :
    dest_edge_p : 
    '''
        
    # compute initial route using the starting node from both e1 and e2 
    route = nx_shortest_path(G, orig_edge[0], dest_edge[0], 'length')
    
     # eliminate overlapping edges
    route = remove_overlapping_edge(route, orig_edge)
    route = remove_overlapping_edge(route, dest_edge)

    # compute partial edges
    orig_edge_p = compute_partial_edge(G, route, orig_edge, orig)
    dest_edge_p = compute_partial_edge(G, route, dest_edge, dest)
    
    # eliminate partial edges with only a single point
    # >>> TODO: this should probably be fixed within the 
    # >>> function "compute_partial_edge"
    if len(orig_edge_p) == 1: orig_edge_p = []
    if len(dest_edge_p) == 1: dest_edge_p = []
    if len(route) == 1: 
        route = []
        dest_edge_p = dest_edge_p[::-1]
    return route, orig_edge_p, dest_edge_p


def shortest_path(
        G, 
        orig, 
        dest, 
        use_shapely=True):
    '''
    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    orig : tuple
        the (lat, lng) or (y, x) point representing the origin of the path
    dest : tuple
        the (lat, lng) or (y, x) point representing the destination of the path
    
    Returns
    -------
    tuple
        (route_dist, route, orig_edge_p, dest_edge_p)
    '''
    
    # find nearest edges
    orig_edge = get_nearest_edge(G, orig)
    dest_edge = get_nearest_edge(G, dest)

    # routing on same edge ---> produces a single partial edge
    if orig_edge == dest_edge:
        route, orig_edge_p, dest_edge_p = route_across_single_edge(
                G, orig_edge, orig, dest)
        
    # different edges
    if orig_edge != dest_edge:

        # compute initial route 
        route = nx_shortest_path(G, orig_edge[0], dest_edge[0], 'length')

        # annoying edge case: route matches first edge
        if route[0] == orig_edge[0] and route[1] == dest_edge[0]:
            route, orig_edge_p, dest_edge_p = route_across_multiple_edges(
                G, orig_edge, dest_edge, orig, dest)

        # one edge ---> produces two partial edges
        elif len(route) == 2:
            route, orig_edge_p, dest_edge_p = route_across_multiple_edges(
                    G, orig_edge, dest_edge, orig, dest)

        # multiple edges ---> produces a main route + two partial edges
        # else len(route) >= 3:
        else:
            route, orig_edge_p, dest_edge_p = route_across_multiple_edges(
                    G, orig_edge, dest_edge, orig, dest)
        
    # compute final route distance
    edge_lengths = get_route_edge_attributes(G, route, 'length')
    route_dist = sum(edge_lengths)
    route_dist += compute_partial_edge_length(G, orig_edge_p)
    route_dist += compute_partial_edge_length(G, orig_edge_p)

    # convert partial edges to shapely LineString if necessary
    if use_shapely:
        if len(orig_edge_p) >= 2:
            orig_edge_p = LineString([Point(x, y) for x, y in orig_edge_p])
        if len(dest_edge_p) >= 2:
            dest_edge_p = LineString([Point(x, y) for x, y in dest_edge_p])

    return route_dist, route, orig_edge_p, dest_edge_p
