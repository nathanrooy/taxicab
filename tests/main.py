import os
import unittest
import taxicab as tc
import osmnx as ox


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
NETWORK_PATH = os.path.join(THIS_DIR, 'data/test_graph.osm')
G = ox.load_graphml(NETWORK_PATH)


class test_main(unittest.TestCase):

    def test_short_route(self):
        orig = (39.0884, -84.3232)
        dest = (39.08843038088047, -84.32261113356783)
        route = tc.distance.shortest_path(G, orig, dest)
        self.assertEqual(route.length, 50.61630824638745)

    def test_same_edge(self):
        orig = (39.08734, -84.32400)
        dest = (39.08840, -84.32307)
        route = tc.distance.shortest_path(G, orig, dest)
        self.assertEqual(route.length, 180.58915031422694)

    def test_far_away_nodes(self):
        orig = (39.08710, -84.31050)
        dest = (39.08800, -84.32000)
        route = tc.distance.shortest_path(G, orig, dest)
        self.assertEqual(route.length, 848.8428082642993)
        # verify partial edges are oriented in the direction of travel
        first_node = (G.nodes[route.nodes[0]]["x"], G.nodes[route.nodes[0]]["y"])
        last_node = (G.nodes[route.nodes[-1]]["x"], G.nodes[route.nodes[-1]]["y"])
        self.assertEqual(route.orig_edge.coords[-1], first_node)
        self.assertEqual(route.dest_edge.coords[0], last_node)

    def test_same_node(self):
        orig = (39.089, -84.319)
        dest = (39.088, -84.320)
        route = tc.distance.shortest_path(G, orig, dest)
        self.assertEqual(route.length, 878.0271885609947)


if __name__ == '__main__':
    unittest.main()
