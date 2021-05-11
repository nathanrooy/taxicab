from osmnx.plot import _save_and_show
from osmnx.plot import plot_graph

from shapely.geometry import LineString

from taxicab.constants import BODY
from taxicab.constants import ORIG_PARTIAL_EDGE
from taxicab.constants import DEST_PARTIAL_EDGE

def plot_graph_route(
    G,
    route,
    route_color="darkorange",
    route_linewidth=2,
    route_alpha=1.0,
    orig_dest_size=100,
    orig_color = "lime",
    dest_color = "r",
    ax=None,
    **pg_kwargs,
    ):
    '''
    NOTE: THIS FUNCTION IS A DIRECT CLONE FROM "osmnx.plot_graph_route"
    WITH ONLY SLIGHT MODIFICATIONS TO HANDLE THE PARTIAL EDGES GENERATED
    BY "taxicab.distance.shortest_path". PLEASE REFER TO THE ORIGINAL OSMNX 
    FUNCTION FOR DOCUMENTATION WHICH CAN BE FOUND HERE:
      
    ---> https://github.com/gboeing/osmnx/blob/master/osmnx/plot.py <---
    '''
    
    linestring_error = 'partial edges must be of type: shapely.geometry.linestring.LineString'
    if route[ORIG_PARTIAL_EDGE]:
        assert type(route[ORIG_PARTIAL_EDGE]) == LineString, linestring_error
    if route[DEST_PARTIAL_EDGE]:
        assert type(route[DEST_PARTIAL_EDGE]) == LineString, linestring_error
        
    if ax is None:
        # plot the graph but not the route, and override any user show/close
        # args for now: we'll do that later
        override = {"show", "save", "close"}
        kwargs = {k: v for k, v in pg_kwargs.items() if k not in override}
        fig, ax = plot_graph(G, show=False, save=False, close=False, **kwargs)
    else:
        fig = ax.figure


    # plot main route if available
    if route[BODY]:
        x, y  = [], []
        for u, v in zip(route[BODY][:-1], route[BODY][1:]):
            # if there are parallel edges, select the shortest in length
            data = min(G.get_edge_data(u, v).values(), key=lambda d: d["length"])
            if "geometry" in data:
                # if geometry attribute exists, add all its coords to list
                xs, ys = data["geometry"].xy
                x.extend(xs)
                y.extend(ys)
            else:
                # otherwise, the edge is a straight line from node to node
                x.extend((G.nodes[u]["x"], G.nodes[v]["x"]))
                y.extend((G.nodes[u]["y"], G.nodes[v]["y"]))
        ax.plot(x, y, c=route_color, lw=route_linewidth, alpha=route_alpha)

    # plot partial edge
    if route[ORIG_PARTIAL_EDGE]:
        x, y = zip(*route[ORIG_PARTIAL_EDGE].coords)
        ax.plot(x, y, c=route_color, lw=route_linewidth, alpha=route_alpha)

    # plot partial edge
    if route[DEST_PARTIAL_EDGE]:
        x, y = zip(*route[DEST_PARTIAL_EDGE].coords)
        ax.plot(x, y, c=route_color, lw=route_linewidth, alpha=route_alpha)

    # save and show the figure as specified, passing relevant kwargs
    sas_kwargs = {"save", "show", "close", "filepath", "file_format", "dpi"}
    kwargs = {k: v for k, v in pg_kwargs.items() if k in sas_kwargs}
    fig, ax = _save_and_show(fig, ax, **kwargs)
    return fig, ax
