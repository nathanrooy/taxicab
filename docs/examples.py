import taxicab as tc
from matplotlib import pyplot as plt

from osmnx import graph_from_bbox
from osmnx.distance import shortest_path as osmnx_shortest_path
from osmnx.distance import get_nearest_node
from osmnx.plot import plot_graph_route as osmnx_plot_graph_route

from random import uniform
from PIL import Image
import io

#--- FUNCTIONS ----------------------------------------------------------------+


def plot_osmnx(G, orig, dest, padding):
    orig_node = get_nearest_node(G, orig)
    dest_node = get_nearest_node(G, dest)
    lp, rp, tp, bp = padding
    
    osmnx_route = osmnx_shortest_path(G, orig_node, dest_node)

    ox_buf = io.BytesIO()
    fig, ax = osmnx_plot_graph_route(G, osmnx_route, node_size=30, show=False, close=False)
    ax.scatter(orig[1], orig[0], c='lime', s=200, label='orig', marker='x')
    ax.scatter(dest[1], dest[0], c='red', s=200, label='dest', marker='x')
    ax.set_ylim([min([orig[0],dest[0]])-bp, max([orig[0],dest[0]])+tp])
    ax.set_xlim([min([orig[1],dest[1]])-lp, max([orig[1],dest[1]])+rp])
    ax.lines[-1].set_label('route')
    plt.legend()
    plt.savefig(ox_buf, format='png', dpi=500, bbox_inches='tight', pad_inches=0)
    ox_buf.seek(0)
    
    return ox_buf
    
    
def plot_taxi(G, orig, dest, padding):
    taxi_route = tc.distance.shortest_path(G, orig, dest)
    lp, rp, tp, bp = padding
    
    print('TC DIST:', taxi_route[0])
        
    tc_buf = io.BytesIO()
    fig, ax = tc.plot.plot_graph_route(G, taxi_route, node_size=30, show=False, close=False)
    ax.scatter(orig[1], orig[0], c='lime', s=200, label='orig', marker='x')
    ax.scatter(dest[1], dest[0], c='red', s=200, label='dest', marker='x')
    ax.set_ylim([min([orig[0],dest[0]])-bp, max([orig[0],dest[0]])+tp])
    ax.set_xlim([min([orig[1],dest[1]])-lp, max([orig[1],dest[1]])+rp])
    plt.legend()
    plt.savefig(tc_buf, format='png', dpi=500, bbox_inches='tight', pad_inches=0)
    tc_buf.seek(0)
    
    return tc_buf
    
    
#--- GENERATE EXAMPLES --------------------------------------------------------+

xmin = -84.324217
xmax = -84.297417
ymin = 39.084289
ymax = 39.099161
G = graph_from_bbox(ymax, ymin, xmin, xmax, network_type='drive', simplify=True)

# SAME EDGE
orig = (39.0884, -84.3232)
dest = (39.08843038088047, -84.32261113356783)

padding = [0.002, 0.0015, 0.001, 0.001] # left, right, top, bottom
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
plt.savefig('ex_01.jpg', dpi=100, bbox_inches='tight')

# SHORT ROUTES
orig = (39.08734, -84.32400)
dest = (39.08840, -84.32307)

padding = [0.001, 0.0015, 0.001, 0.001] # left, right, top, bottom
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
plt.savefig('ex_02.jpg', dpi=100, bbox_inches='tight')

# NEAREST NODE IS FAR AWAY
orig = (39.08710, -84.31050)
dest = (39.08800, -84.32000)

padding = [0.0025, 0.001, 0.004, 0.001] # left, right, top, bottom
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
plt.savefig('ex_03.jpg', dpi=100, bbox_inches='tight')
