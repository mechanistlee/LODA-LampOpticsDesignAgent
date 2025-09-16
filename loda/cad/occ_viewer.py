"""occ_viewer.py
PyVista 기반 디버그 뷰어 구현.
"""
import numpy as np
class OCCViewer:
    def __init__(self):
        try:  # pragma: no cover
            import pyvista as pv  # noqa: F401
            self._pv = True
            self._pv_mod = pv
        except Exception:
            self._pv = False
            self._pv_mod = None

    def show(self, baked_mesh, axis_lines=None, show_edges: bool = True):  # pragma: no cover - requires optional deps
        if not self._pv:
            raise RuntimeError('PyVista not installed. Install pyvista to enable visualization.')
        pv = self._pv_mod
        if baked_mesh.verts.shape[0] == 0:
            plotter = pv.Plotter()
            plotter.add_text('Empty Mesh', font_size=12)
            plotter.show()
            return
        mesh = pv.PolyData(baked_mesh.verts, np.hstack([np.full((baked_mesh.faces.shape[0],1),3), baked_mesh.faces]).astype(np.int32))
        cmap = 'viridis'
        scalars = baked_mesh.tri_label if baked_mesh.tri_label.size else None
        plotter = pv.Plotter()
        plotter.add_mesh(mesh, scalars=scalars, show_edges=show_edges, cmap=cmap)
        if axis_lines:
            for line in axis_lines:
                arr = pv.Spline(line, len(line))
                plotter.add_mesh(arr, color='red', line_width=2)
        plotter.show()

__all__ = ['OCCViewer']
