import unittest
from scripts import demo

class SmokeTest(unittest.TestCase):
    def test_demo_runs(self):
        res = demo.run_demo()
        self.assertIsInstance(res, dict)

if __name__ == '__main__':
    unittest.main()
