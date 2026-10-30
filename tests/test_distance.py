import os
import unittest
import osmnx as ox
import taxicab as tc

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
NETWORK_PATH = os.path.join(THIS_DIR, "data/test_graph.osm")
G = ox.load_graphml(NETWORK_PATH)


class TestDistance(unittest.TestCase):
    """Test shortest path distance computations across OSM graph."""

    def test_same_edge(self):
        """Test routing when origin and destination are along the same edge."""
        orig = (39.0884, -84.3232)
        dest = (39.08843038088047, -84.32261113356783)
        route = tc.distance.shortest_path(G, orig, dest)
        self.assertAlmostEqual(route.length, 50.61630824638745, places=8)

    def test_adjacent_edges(self):
        """Test routing across two edges meeting at a common node."""
        orig = (39.08734, -84.32400)
        dest = (39.08840, -84.32307)
        route = tc.distance.shortest_path(G, orig, dest)
        self.assertAlmostEqual(route.length, 180.58915031422694, places=8)

    def test_far_away_nodes(self):
        """Test multi-edge route spanning multiple intermediate nodes."""
        orig = (39.08710, -84.31050)
        dest = (39.08800, -84.32000)
        route = tc.distance.shortest_path(G, orig, dest)
        self.assertAlmostEqual(route.length, 848.8428082642993, places=8)
        # verify partial edges are oriented in the direction of travel
        first_node = (G.nodes[route.nodes[0]]["x"], G.nodes[route.nodes[0]]["y"])
        last_node = (G.nodes[route.nodes[-1]]["x"], G.nodes[route.nodes[-1]]["y"])
        self.assertEqual(route.orig_edge.coords[-1], first_node)
        self.assertEqual(route.dest_edge.coords[0], last_node)

    def test_same_node(self):
        """Test routing when origin and destination are closest to the same node."""
        orig = (39.089, -84.319)
        dest = (39.088, -84.320)
        route = tc.distance.shortest_path(G, orig, dest)
        self.assertAlmostEqual(route.length, 878.0271885609947, places=8)


if __name__ == "__main__":
    unittest.main()

