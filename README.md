[![gh-actions-ci](https://img.shields.io/github/workflow/status/nathanrooy/taxicab/ci?style=flat-square)](https://github.com/nathanrooy/taxicab/actions?query=workflow%3Aci)
[![GitHub license](https://img.shields.io/github/license/nathanrooy/taxicab?style=flat-square)](https://github.com/nathanrooy/taxicab/blob/main/LICENSE)
[![codecov](https://img.shields.io/codecov/c/github/nathanrooy/taxicab.svg?style=flat-square)](https://codecov.io/gh/nathanrooy/taxicab)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/taxicab.svg?style=flat-square)](https://pypi.org/pypi/taxicab/)
[![PyPi Version](https://img.shields.io/pypi/v/taxicab.svg?style=flat-square)](https://pypi.org/project/taxicab)

## Taxicab
When routing between two points of longitude and latitude, the built in routing functionality in <a href="https://github.com/gboeing/osmnx">OSMnx</a> will find the nearest network nodes and route between those. This assumption is fine, and works for many applications but when you need routing with a little more accuracy you'll want to consider using Taxicab. Below are a few examples which highlight Taxicab usecases:

When the nearest nodes are not that close
<img src="https://github.com/nathanrooy/taxicab/blob/main/docs/ex_03.jpg">

When routing along a single edge:
<img src="https://github.com/nathanrooy/taxicab/blob/main/docs/ex_01.jpg">

When routing along short routes:
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
Taxicab is designed to be used as a drop in replacement for the standard routing functionality found on OSMnx. So, like usual, download a portion of the OpenStreetMap network graph:

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

And the route is generated via the following:
```python
import taxicab as tc
route = tc.distance.shortest_path(G, orig, dest)
```

Which can then be plotted:
```python
tc.plot.plot_graph_route(G, route)
```

Should yield the following:
<img src="https://github.com/nathanrooy/taxicab/blob/main/docs/readme.png">>

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
