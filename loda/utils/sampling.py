import numpy as np

def cosine_hemisphere(n_rays: int):
    u1 = np.random.rand(n_rays)
    u2 = np.random.rand(n_rays)
    r = np.sqrt(u1)
    theta = 2*np.pi*u2
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = np.sqrt(1.0 - u1)
    return np.stack([x,y,z], axis=-1).astype(np.float32)
