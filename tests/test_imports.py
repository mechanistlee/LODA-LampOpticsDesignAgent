import unittest

class TestImports(unittest.TestCase):
    def test_geometry_imports(self):
        from loda.geometry.occ_reader import OCCReader
        from loda.geometry.meshing import get_preset
        from loda.geometry.labeling import assign_label
        self.assertIsNotNone(OCCReader)
        self.assertIsNotNone(get_preset('fast'))
        self.assertEqual(assign_label('REFLECT_part'), 'REFLECTOR')

    def test_optics_imports(self):
        from loda.optics.registry import OpticalRegistry
        from loda.optics.bsdf import make_bsdf
        from loda.optics.sources import build_source
        from loda.optics.sensors import PlanarSensor
        from loda.optics.surface_bin_sensor import SurfaceBinSensor, SurfaceBin
        self.assertIsNotNone(OpticalRegistry)
        self.assertIsNotNone(make_bsdf('mirror', {}))
        self.assertIsNotNone(build_source(type('Spec', (), {'distribution':'gaussian','params':{}})))
        self.assertIsNotNone(PlanarSensor((10,10),(16,16),100))
        bins = {0: SurfaceBin(face_indices=(1,2,3), normal=(0,0,1), area=1.0)}
        sbs = SurfaceBinSensor(bins)
        sbs.accumulate(0, (0.1,0.1,0.98), 0.5)
        self.assertGreaterEqual(sbs.energy_sum[0], 0.5)

    def test_raytrace_imports(self):
        from loda.raytrace.optix_builder import OptiXBuilder
        from loda.raytrace.wavefront import WavefrontController
        self.assertIsNotNone(OptiXBuilder())
        self.assertIsNotNone(WavefrontController(2))

if __name__ == '__main__':
    unittest.main()
