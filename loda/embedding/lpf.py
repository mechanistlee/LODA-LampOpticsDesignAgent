"""Light Path Field (LPF) module stub"""

class LPFModule:
    def __init__(self):
        print("LPFModule: initialized")

    def initialize(self, config):
        print("LPFModule: initialize with source", config.source.position)
        # TODO: create LPF grid (theta,phi) and nodes
        return None
