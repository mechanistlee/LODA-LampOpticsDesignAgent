"""Core agent wiring for LODA"""
from .config import LODAConfig

class LODAAgent:
    def __init__(self, config: LODAConfig):
        self.config = config
        # lazy imports of modules (stubs)
        from .input import loader as input_loader
        from .embedding import lpf
        from .curation import lad
        from .rpa import rpa
        from .structure import reconstructor
        from .raytracing import tracer
        from .training import trainer

        self.input = input_loader.InputLoader()
        self.embedding = lpf.LPFModule()
        self.curation = lad.LADModule()
        self.rpa = rpa.RPAModule()
        self.structure = reconstructor.StructureReconstructor()
        self.raytracer = tracer.RayTracer()
        self.trainer = trainer.Trainer()

    def run_once(self):
        # minimal pipeline placeholder
        print("LODAAgent: running basic pipeline")
        self.input.load(self.config)
        self.embedding.initialize(self.config)
        self.curation.curate(self.config)
        self.rpa.step(self.config)
        self.structure.reconstruct(self.config)
        results = self.raytracer.trace(self.config)
        print("Run results (placeholder):", results)
        return results
