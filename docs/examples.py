from taxicab import shortest_path as tc_shortest_path
from taxicab import plot_graph_route as tc_plot_graph_route
from matplotlib import pyplot as plt

from osmnx.distance import nearest_nodes
from osmnx.io import load_graphml
from osmnx.plot import plot_graph_route as osmnx_plot_graph_route
from osmnx.routing import shortest_path as osmnx_shortest_path

from PIL import Image
import io

# -- FUNCTIONS ----------------------------------------------------------------+


def plot_osmnx(G, orig, dest, padding):
    orig_node = nearest_nodes(G, orig[1], orig[0])
    dest_node = nearest_nodes(G, dest[1], dest[0])
    lp, rp, tp, bp = padding

    osmnx_route = osmnx_shortest_path(G, orig_node, dest_node)

    ox_buf = io.BytesIO()
    fig, ax = osmnx_plot_graph_route(G, osmnx_route, node_size=30, show=False, close=False)
    ax.scatter(orig[1], orig[0], c='lime', s=200, label='orig', marker='x')
    ax.scatter(dest[1], dest[0], c='red', s=200, label='dest', marker='x')
    ax.set_ylim([min([orig[0] dest[0]])-bp, max([orig[0], dest[0]])+tp])
    ax.set_xlim([min([orig[1], dest[1]])-lp, max([orig[1], dest[1]])+rp])
    ax.lines[-1].set_label('route')
    plt.legend()
    plt.savefig(ox_buf, format='png', dpi=500, bbox_inches='tight', pad_inches=0)
    ox_buf.seek(0)
    
    return ox_buf
    
    
def plot_taxi(G, orig, dest, padding):
    taxi_route = tc_shortest_path(G, orig, dest)
    lp, rp, tp, bp = padding
    
    print('TC DIST:', taxi_route[0])
        
    tc_buf = io.BytesIO()
    fig, ax = tc_plot_graph_route(G, taxi_route, node_size=30, show=False, close=False)
    ax.scatter(orig[1], orig[0], c='lime', s=200, label='orig', marker='x')
    ax.scatter(dest[1], dest[0], c='red', s=200, label='dest', marker='x')
    ax.set_ylim([min([orig[0],dest[0]])-bp, max([orig[0],dest[0]])+tp])
    ax.set_xlim([min([orig[1],dest[1]])-lp, max([orig[1],dest[1]])+rp])
    plt.legend()
    plt.savefig(tc_buf, format='png', dpi=500, bbox_inches='tight', pad_inches=0)
    tc_buf.seek(0)
    
    return tc_buf
    
    
def plot_compare(orig, dest, padding, filename):
    tc_buf = plot_taxi(G, orig, dest, padding)
    ox_buf = plot_osmnx(G, orig, dest, padding)

    fig, [ax1, ax2] = plt.subplots(1, 2, figsize=(15,15))
    img1 = Image.open(tc_buf)
    img2 = Image.open(ox_buf)
    ax1.imshow(img1)
    ax1.set_title('Taxicab', fontsize=16)
    ax1.axes.xaxis.set_visible(False)
    ax1.axes.yaxis.set_visible(False)
    ax2.imshow(img2)
    ax2.set_title('OSMnx', fontsize=16)
    ax2.axes.xaxis.set_visible(False)
    ax2.axes.yaxis.set_visible(False)
    plt.savefig(filename, dpi=100, bbox_inches='tight', pad_inches=0.25)


#--- GENERATE EXAMPLES --------------------------------------------------------+

G = load_graphml("tests/data/test_graph.osm")

# SAME EDGE
orig = (39.0884, -84.3232)
dest = (39.08843038088047, -84.32261113356783)
padding = [0.002, 0.0015, 0.001, 0.001] # left, right, top, bottom
plot_compare(orig, dest, padding, 'ex_01.jpg')

# SHORT ROUTES
orig = (39.08734, -84.32400)
dest = (39.08840, -84.32307)
padding = [0.001, 0.0015, 0.0002, 0.0006] # left, right, top, bottom
plot_compare(orig, dest, padding, 'ex_02.jpg')

# NEAREST NODE IS FAR AWAY
orig = (39.08710, -84.31050)
dest = (39.08800, -84.32000)
padding = [0.0025, 0.001, 0.004, 0.001] # left, right, top, bottom
plot_compare(orig, dest, padding, 'ex_03.jpg')

# NEAREST NODES ARE THE SAME
orig = (39.089, -84.319)
dest = (39.088, -84.320)
padding = [0.0025, 0.001, 0.0025, 0.001] # left, right, top, bottom
plot_compare(orig, dest, padding, 'ex_04.jpg')