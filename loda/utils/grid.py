import numpy as np

def theta_phi_grid(T: int, P: int, theta_max_rad: float):
    theta = np.linspace(0, theta_max_rad, T)
    phi = np.linspace(-np.pi, np.pi, P, endpoint=False)
    th, ph = np.meshgrid(theta, phi, indexing='ij')
    dirs = np.stack([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)], axis=-1)
    return th, ph, dirs  # (T,P), (T,P), (T,P,3)
