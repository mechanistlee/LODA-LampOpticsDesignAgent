"""Minimal demo to instantiate the LODA agent and run one pipeline step"""
from loda.config import LODAConfig, SourceInfo, SpaceInfo, OutputSurfaceInfo
from loda import LODAAgent

def run_demo():
    src = SourceInfo(position=(0.0,0.0,0.0), direction=(0.0,0.0,1.0), angular_distribution=None, etendue=1.0, power=1.0)
    space = SpaceInfo(bounds=None)
    out = OutputSurfaceInfo(mesh=None)
    cfg = LODAConfig(source=src, space=space, output_surface=out)

    agent = LODAAgent(cfg)
    results = agent.run_once()
    print("Demo finished")
    return results

if __name__ == '__main__':
    run_demo()
