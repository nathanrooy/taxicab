"""Plot taxicab routes across an OSMnx graph."""

from __future__ import annotations

from operator import itemgetter
from typing import TYPE_CHECKING, Any

from osmnx.plot import _save_and_show, plot_graph
from shapely.geometry import LineString

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from networkx import MultiDiGraph

    from .distance import TaxiRoute


def plot_graph_route(  # noqa: PLR0913
    G: MultiDiGraph,
    route: TaxiRoute,
    route_color: str = "darkorange",
    route_linewidth: float = 2,
    route_alpha: float = 1.0,
    orig_dest_size: float = 100,  # noqa: ARG001
    orig_color: str = "lime",  # noqa: ARG001
    dest_color: str = "r",  # noqa: ARG001
    ax: Axes | None = None,
    **pg_kwargs: Any,  # noqa: ANN401
) -> tuple[Figure, Axes]:
    """
    Plot a taxicab route along a graph, including partial origin and destination edges.

    NOTE: THIS FUNCTION IS A DIRECT CLONE FROM "osmnx.plot_graph_route"
    WITH ONLY SLIGHT MODIFICATIONS TO HANDLE THE PARTIAL EDGES GENERATED
    BY "taxicab.distance.shortest_path". PLEASE REFER TO THE ORIGINAL OSMNX
    FUNCTION FOR DOCUMENTATION WHICH CAN BE FOUND HERE:

    ---> https://github.com/gboeing/osmnx/blob/master/osmnx/plot.py <---

    Parameters
    ----------
    G : networkx.MultiDiGraph
        Input graph.
    route : TaxiRoute
        Taxicab route named tuple returned by `taxicab.distance.shortest_path`.
    route_color : str
        Color of the route line.
    route_linewidth : float
        Width of the route line.
    route_alpha : float
        Opacity of the route line.
    orig_dest_size : float
        Size of the origin and destination nodes.
    orig_color : str
        Color of the origin node.
    dest_color : str
        Color of the destination node.
    ax : matplotlib.axes.Axes or None
        If not None, plot route on this preexisting axis instead of creating a new one.
    **pg_kwargs : Any
        Keyword arguments passed to `osmnx.plot.plot_graph`.

    Returns
    -------
    tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]
        The resulting matplotlib figure and axes objects.

    Raises
    ------
    TypeError
        If `route.orig_edge` or `route.dest_edge` is not a `shapely.geometry.LineString`.
    """
    linestring_error = "partial edges must be of type: shapely.geometry.linestring.LineString"
    if route.orig_edge is not None and not isinstance(route.orig_edge, LineString):
        raise TypeError(linestring_error)
    if route.dest_edge is not None and not isinstance(route.dest_edge, LineString):
        raise TypeError(linestring_error)

    if ax is None:
        # plot the graph but not the route, and override any user show/close
        # args for now: we'll do that later
        override = {"show", "save", "close"}
        kwargs = {k: v for k, v in pg_kwargs.items() if k not in override}
        fig, ax = plot_graph(G, show=False, save=False, close=False, **kwargs)
    else:
        fig = ax.figure

    # plot main route if available
    if len(route.nodes) > 0:
        x, y = [], []
        for u, v in zip(route.nodes[:-1], route.nodes[1:]):
            # if there are parallel edges, select the shortest in length
            data = min(G.get_edge_data(u, v).values(), key=itemgetter("length"))
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
    if route.orig_edge:
        x, y = zip(*route.orig_edge.coords)
        ax.plot(x, y, c=route_color, lw=route_linewidth, alpha=route_alpha)

    # plot partial edge
    if route.dest_edge:
        x, y = zip(*route.dest_edge.coords)
        ax.plot(x, y, c=route_color, lw=route_linewidth, alpha=route_alpha)

    # save and show the figure as specified, passing relevant kwargs
    sas_kwargs = {"save", "show", "close", "filepath", "file_format", "dpi"}
    kwargs = {k: v for k, v in pg_kwargs.items() if k in sas_kwargs}
    fig, ax = _save_and_show(fig, ax, **kwargs)
    return fig, ax
