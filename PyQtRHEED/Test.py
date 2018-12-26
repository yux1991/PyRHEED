import unittest
import Graph3DSurface

class Test3DGraph(unittest.TestCase):

    def setUp(self):
        self.graph = Graph3DSurface.SurfaceGraph()

    def test_fillTwoDimensionalMappingProxy(self):
        self.graph.fillTwoDimensionalMappingProxy()

if __name__ == '__main__':
    unittest.main()