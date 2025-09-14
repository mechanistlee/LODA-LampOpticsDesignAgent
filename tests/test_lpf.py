import unittest
import numpy as np
from loda.fields.lpf import LPFConfig, LPF, RayPath


class TestLPFMatrix(unittest.TestCase):
    def test_init_and_distribution(self):
        cfg = LPFConfig(source_angle=20, ray_resolution=5, bounces=2)
        H, W = cfg.compute_size()
        self.assertEqual(H, 5)  # 20/5 + 1 = 5
        lpf = LPF(cfg)
        lpf.build_from_source_distribution(lambda th, ph: 1.0)
        # 첫 step 에너지 맵 합 = 1.0
        m0 = lpf.distribution_map(0)
        self.assertAlmostEqual(float(m0.sum()), 1.0, places=6)
        # append interaction on one cell
        lpf.append_interaction(0, 0, vertex=np.array([0,0,0.1],dtype=np.float32), theta=0.1, phi=0.2, energy=m0[0,0]*0.9)
        path = lpf.get_path(0,0)
        self.assertEqual(len(path.steps), 2)
        # connectivity check should pass
        lpf.enforce_all_connectivity()

    def test_export(self):
        cfg = LPFConfig(source_angle=10, ray_resolution=5, bounces=1)
        lpf = LPF(cfg)
        lpf.build_from_source_distribution(lambda th, ph: th + ph + 1)
        data = lpf.export_numpy()
        self.assertIn('config', data)
        self.assertIn('paths', data)
        self.assertEqual(len(data['paths']), lpf.H * lpf.W)

if __name__ == '__main__':
    unittest.main()
