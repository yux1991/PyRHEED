import unittest
import simulate_RHEED

class Test(unittest.TestCase):

    def setUp(self):
        self.simuRHEED = simulate_RHEED.Window.main()

if __name__ == '__main__':
    unittest.main()