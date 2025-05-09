![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/nathanrooy/taxicab/ci.yml?style=flat-square)
[![GitHub license](https://img.shields.io/github/license/nathanrooy/taxicab?style=flat-square)](https://github.com/nathanrooy/taxicab/blob/main/LICENSE)
[![codecov](https://img.shields.io/codecov/c/github/nathanrooy/taxicab.svg?style=flat-square)](https://codecov.io/gh/nathanrooy/taxicab)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/taxicab.svg?style=flat-square)](https://pypi.org/pypi/taxicab/)
[![PyPi Version](https://img.shields.io/pypi/v/taxicab.svg?style=flat-square)](https://pypi.org/project/taxicab)

## Taxicab
When routing between two points of longitude and latitude, the built in routing functionality in <a href="https://github.com/gboeing/osmnx">OSMnx</a> will find the nearest network nodes and route between those. This assumption is fine, and works for many applications but when you need routing with a little more accuracy you'll want to consider using Taxicab. Below are a few examples which highlight Taxicab use cases:

<b>When the nearest nodes are not that close:</b>
<img style="padding-top:5em;" src="https://github.com/nathanrooy/taxicab/blob/main/docs/ex_03.jpg">

<b>When routing along a single edge:</b>
<img src="https://github.com/nathanrooy/taxicab/blob/main/docs/ex_01.jpg">

<b>When routing along short routes:</b>
<img src="https://github.com/nathanrooy/taxicab/blob/main/docs/ex_02.jpg">

<b>When the nearest nodes are the same:</b>
<img src="https://github.com/nathanrooy/taxicab/blob/main/docs/ex_04.jpg">

## Installation
The easiest way to use Taxicab is probably via a PyPi install:
```sh
pip install taxicab
```
You can also install directly from this repo:
```sh
pip install git+https://github.com/nathanrooy/taxicab
```

## Example usage
Taxicab is designed to be used as a drop-in replacement for the standard routing functionality found on OSMnx. So, like usual, download a portion of the OpenStreetMap graph:

```python
from osmnx import graph_from_bbox
xmin, xmax = -84.323, -84.305
ymin, ymax =  39.084,  39.092
G = graph_from_bbox([xmin, ymin, xmax, ymax], network_type='drive', simplify=True)
```

Now, specify your origin and destination:
```python
orig = (39.0871, -84.3105)
dest = (39.0880, -84.3200) 
```

Compute the route via the following:
```python
import taxicab as tc
route = tc.distance.shortest_path(G, orig, dest)
```

Which can then be plotted:
```python
tc.plot.plot_graph_route(G, route)
```
<img src="https://github.com/nathanrooy/taxicab/blob/main/docs/readme.png">


The returned route is a named tuple comprised of four elements:
- Route length in meters (or whatever your graph units are).
```python
>>> route.length
669.0529395595279
```

- List of node IDs representing the bulk of the route (this is identical to OSMnx).
```python
>>> route.nodes
[197546973, 2090608743, 197656382, 197633479]
```

- And two partial edges represented by `shapely.geometry.linestring.LineString` objects. If populated, these represent the first and last segments of the route that extend from the first or last node to some point along that edge.
```python
>>> route.orig_edge, route.dest_edge
(<shapely.geometry.linestring.LineString at 0x7f1aa08067c0>,
 <shapely.geometry.linestring.LineString at 0x7f1a3ccbd580>)
```

## User reference
```python
taxicab.distance.shortest_route(G, orig, dest)
```
Parameters:
- G : (networkx.MultiDiGraph) - input graph
- orig : (tuple) - a (lat, lng) or (y, x) point
- dest : (tuple) - a (lat, lng) or (y, x) point

Returns: (named tuple)
- route.length : float - distance in meters of computed route.
- route.nodes : path - list of node IDs constituting the shortest path (this is identical to routes found in OSMnx).
- route.orig_edge : `shapely.geometry.linestring.LineString` - a partial edge representing the first non-complete edge in the route.
- route.dest_edge : `shapely.geometry.linestring.LineString` - a partial edge representing the last non-complete edge in the route.
- Note that if a route is successfully computed the distance will always be returned. However, depending on the length of the route and the underlying network, route.nodes, route.orig_edge, or route.dest_edge, may be `null`.

```python
taxicab.plot.plot_graph_route()
```
Used exactly the same way as `osmnx.plot.plot_graph_route` except that it uses the route (named tuple) produced by Taxicab instead. See OSMnx function reference [<a href="https://osmnx.readthedocs.io/en/stable/osmnx.html#osmnx.plot.plot_graph_route">here</a>] 
