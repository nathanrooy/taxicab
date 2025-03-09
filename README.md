[![gh-actions-ci](https://img.shields.io/github/workflow/status/nathanrooy/taxicab/ci?style=flat-square)](https://github.com/nathanrooy/taxicab/actions?query=workflow%3Aci)
[![GitHub license](https://img.shields.io/github/license/nathanrooy/taxicab?style=flat-square)](https://github.com/nathanrooy/taxicab/blob/main/LICENSE)
[![codecov](https://img.shields.io/codecov/c/github/nathanrooy/taxicab.svg?style=flat-square)](https://codecov.io/gh/nathanrooy/taxicab)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/taxicab.svg?style=flat-square)](https://pypi.org/pypi/taxicab/)
[![PyPi Version](https://img.shields.io/pypi/v/taxicab.svg?style=flat-square)](https://pypi.org/project/taxicab)

## Taxicab
When routing between two points of longitude and latitude, the built in routing functionality in <a href="https://github.com/gboeing/osmnx">OSMnx</a> will find the nearest network nodes and route between those. This assumption is fine, and works for many applications but when you need routing with a little more accuracy you'll want to consider using Taxicab. Below are a few examples which highlight Taxicab usecases:

<b>When the nearest nodes are not that close:</b>
<img style="padding-top:5em;" src="https://github.com/nathanrooy/taxicab/blob/main/docs/ex_03.jpg">

<b>When routing along a single edge:</b>
<img src="https://github.com/nathanrooy/taxicab/blob/main/docs/ex_01.jpg">

<b>When routing along short routes:</b>
<img src="https://github.com/nathanrooy/taxicab/blob/main/docs/ex_02.jpg">

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
Taxicab is designed to be used as a drop in replacement for the standard routing functionality found on OSMnx. So, like usual, download a portion of the OpenStreetMap graph:

```python
from osmnx import graph_from_bbox
xmin, xmax = -84.323, -84.305
ymin, ymax =  39.084,  39.092
G = graph_from_bbox(ymax, ymin, xmin, xmax, network_type='drive', simplify=True)
```

Now, specify your origin and destination:
```python
orig = (39.08710, -84.31050)
dest = (39.08800, -84.32000) 
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


The returned route tuple is comprised of four elements:
- Route length in meters
```python
>>> route[0]
669.0529395595279
```
- List of node IDs representing the bulk of the route (this is identical to OSMnx).
```python
>>> route[1]
[197546973, 2090608743, 197656382, 197633479]
```
- And two partial edges represented by `shapely.geometry.linestring.LineString` objects. If populated, these represent the first and last segments of the route that extend from the first or last node to some point along that edge.
```python
>>> route[2], route[3]
(<shapely.geometry.linestring.LineString at 0x7f1aa08067c0>,
 <shapely.geometry.linestring.LineString at 0x7f1a3ccbd580>)
```

## User reference
```python
taxicab.distance.shortest_route(G, orig, dest)
```
Parameters:
- G : (networkx.MultiDiGraph) – input graph
- orig : (tuple) – a (lat, lng) or (y, x) point
- dest : (tuple) – a (lat, lng) or (y, x) point

Returns: (tuple)
- route[0] : float – distance in meters of computed route.
- route[1] : path – list of node IDs constituting the shortest path (this is identical to routes found in OSMnx).
- route[2] : `shapely.geometry.linestring.LineString` – a partial edge representing the first non-complete edge in the route.
- route[3] : `shapely.geometry.linestring.LineString` – a partial edge representing the last non-complete edge in the route.
- Note that if a route is successfully computed the distance will always be returned. However, depending on the length of the route and the underlying network, elements 1, 2, or 3 may be `null`.

```python
taxicab.plot.plot_graph_route()
```
Used exactly the same way as `osmnx.plot.plot_graph_route` except that it uses the route produced by Taxicab instead. See OSMnx function reference [<a href="https://osmnx.readthedocs.io/en/stable/osmnx.html#osmnx.plot.plot_graph_route">here</a>] 


## Performance Considerations
Coming soon...
