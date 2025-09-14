"""OptiX 빌더 스켈레톤.
BLAS/TLAS 구성 및 SBT 자리.
"""
class OptiXBuilder:
    def __init__(self):
        self.blas = []
        self.tlas = None
        self.sbt = None
    def build_blas(self, meshes):
        # placeholder
        self.blas = ['BLAS' for _ in meshes]
    def build_tlas(self, instances):
        self.tlas = 'TLAS'
    def build_sbt(self, registry):
        self.sbt = 'SBT'
