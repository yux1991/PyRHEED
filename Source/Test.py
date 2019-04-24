import unittest
import SimulateRHEED

class Test(unittest.TestCase):

    def setUp(self):
        self.simuRHEED = SimulateRHEED.SimulateRHEEDPattern.Main()

if __name__ == '__main__':
    unittest.main()