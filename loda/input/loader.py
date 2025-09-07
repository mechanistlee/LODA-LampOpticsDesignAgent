"""Input loading and validation"""
from ..config import LODAConfig

class InputLoader:
    def load(self, config: LODAConfig):
        print("InputLoader: loaded config with source at", config.source.position)
        # TODO: validate and preprocess inputs
        return config
