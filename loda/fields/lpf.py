"""LPF (Light Path Field)

목적:
  - 광 경로(ray path)와 각 경로상의 광선 상태(ray_data: 절점, 방향, 에너지)를 2차원 메트릭스 형태로 관리
  - RPA 및 LAD 수렴 평가, ONF 계산의 기반 데이터 구조

메트릭스 정의:
  - 행/열 크기 = floor(source_angle / ray_resolution) + 1
  - 각 셀(row=i, col=j)는 하나의 RayPath를 가진다.
  - RayPath는 최대 b (bounce 수) 단계의 ray_data 시퀀스 + 마지막 도착 절점을 포함할 수 있다.

ray_data 구조:
  - 기본 (중간 단계): vertex(np.ndarray shape (3,)), direction(theta, phi), energy(float 0~1)
  - 마지막 단계: 위 필드 + final_vertex(np.ndarray shape (3,)) (광선 최종 도착점)

규칙:
  - 연속된 ray_data_k 와 ray_data_{k+1} 는 동일한 교점(vertex) 공유 (k+1의 vertex == k의 final_vertex or interaction point)
  - 첫 ray_data는 광원 배광 분포에서 초기화

Config 파라미터:
  - source_angle (deg) : (1~180, default 120)
  - ray_resolution (deg) : (0.001~20, default 10)
  - bounces (int b >=1, default 2)

핵심 메서드:
  - LPFConfig.compute_size() → (H,W)
  - LPF.build_from_source_distribution(dist_func)
  - get_path(i,j) / set_path(i,j,path)
  - update_ray_step(i,j,step, new_data)
  - enforce_connectivity(path)
  - export_numpy() 직렬화

NOTE:
  - 방향 표현: 내부 저장은 (theta, phi) (라디안). 필요 시 3D 벡터 변환 헬퍼 추가 예정.
  - 성능 최적화(NumPy 벡터화, torch 변환)는 후속 단계.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Callable, Dict, Any
import math
import numpy as np
from loda.config import LPFConfig

@dataclass
class RayData:
	"""단일 광선 상태.
	vertex: 상호작용 직후(또는 시작) 위치 (x,y,z)
	theta, phi: 광축 기준 구면좌표(라디안)
	energy: 0~1 정규화(총 광원 파워 대비 비율이나 상대량)
	final_vertex: 마지막 단계일 경우 도착 절점(없으면 None)
	"""
	vertex: np.ndarray
	theta: float
	phi: float
	energy: float
	final_vertex: Optional[np.ndarray] = None

	def to_dict(self) -> Dict[str, Any]:
		return {
			'vertex': self.vertex,
			'theta': self.theta,
			'phi': self.phi,
			'energy': self.energy,
			'final_vertex': self.final_vertex
		}

@dataclass
class RayPath:
	"""하나의 셀을 구성하는 광 경로 (최대 b 단계)."""
	steps: List[RayData] = field(default_factory=list)
	max_bounces: int = 1

	def add_step(self, rd: RayData):
		if len(self.steps) >= self.max_bounces:
			raise ValueError("Exceeded max bounces for this RayPath")
		self.steps.append(rd)

	def last(self) -> Optional[RayData]:
		return self.steps[-1] if self.steps else None

	def to_dict(self) -> Dict[str, Any]:
		return {
			'steps': [s.to_dict() for s in self.steps],
			'max_bounces': self.max_bounces
		}

	def enforce_connectivity(self):
		"""연속된 단계의 교점 일관성 점검 (간단 검증: 위치 근접성)."""
		for i in range(len(self.steps)-1):
			a = self.steps[i]
			b = self.steps[i+1]
			# a.final_vertex 가 있다면 b.vertex 와 가까워야 함, 없으면 a.vertex==b.vertex 가정
			ref = a.final_vertex if a.final_vertex is not None else a.vertex
			if np.linalg.norm(ref - b.vertex) > 1e-6:
				raise ValueError(f"Connectivity violation at segment {i}->{i+1}")


class LPF:
	"""Light Path Field 2D 컨테이너.

	내부 표현:
	  - self.paths: 길이 H*W 의 RayPath 리스트
	  - (i,j) 인덱싱 → idx = i*W + j
	"""
	def __init__(self, cfg: LPFConfig):
		self.cfg = cfg
		self.H, self.W = cfg.compute_size()
		self.paths: List[RayPath] = [RayPath(max_bounces=cfg.bounces) for _ in range(self.H * self.W)]
		self.meta: Dict[str, Any] = {}

	# ---------------- 인덱스 도우미 ----------------
	def _index(self, i: int, j: int) -> int:
		if not (0 <= i < self.H and 0 <= j < self.W):
			raise IndexError("(i,j) out of bounds")
		return i * self.W + j

	# ---------------- 접근자 ----------------
	def get_path(self, i: int, j: int) -> RayPath:
		return self.paths[self._index(i, j)]

	def set_path(self, i: int, j: int, path: RayPath):
		if path.max_bounces != self.cfg.bounces:
			raise ValueError("path max_bounces mismatch with LPF config")
		self.paths[self._index(i, j)] = path

	# ---------------- 초기화 ----------------
	def build_from_source_distribution(self, distribution: Callable[[float, float], float]):
		"""배광 분포 함수 distribution(theta_deg, phi_deg)->상대에너지 사용하여 첫 step 초기화.
		phi 축도 동일 해상도로 가정(0~source_angle). 후속 구현에서 phi 0~360 확장 가능.
		"""
		H, W = self.H, self.W
		origin = np.asarray(self.cfg.source_origin, dtype=np.float32)
		total = 0.0
		energies = np.zeros((H, W), dtype=np.float64)
		for i in range(H):
			theta_deg = i * self.cfg.ray_resolution
			for j in range(W):
				phi_deg = j * self.cfg.ray_resolution
				e = distribution(theta_deg, phi_deg)
				if e < 0:
					e = 0.0
				energies[i, j] = e
				total += e
		if total <= 0:
			# 균일 분배 fall-back
			energies[:] = 1.0
			total = energies.sum()
		energies /= total  # 정규화
		for i in range(H):
			theta_deg = i * self.cfg.ray_resolution
			for j in range(W):
				phi_deg = j * self.cfg.ray_resolution
				path = self.get_path(i, j)
				if path.steps:  # 재초기화 시 비움
					path.steps.clear()
				rd = RayData(
					vertex=origin.copy(),
					theta=math.radians(theta_deg),
					phi=math.radians(phi_deg),
					energy=float(energies[i, j]),
					final_vertex=None
				)
				path.add_step(rd)

	# ---------------- 업데이트 ----------------
	def update_ray_step(self, i: int, j: int, step_index: int, *, vertex: Optional[np.ndarray] = None, theta: Optional[float] = None, phi: Optional[float] = None, energy: Optional[float] = None, final_vertex: Optional[np.ndarray] = None):
		path = self.get_path(i, j)
		if step_index >= len(path.steps):
			raise IndexError("step_index out of range")
		rd = path.steps[step_index]
		if vertex is not None:
			rd.vertex = vertex.astype(np.float32)
		if theta is not None:
			rd.theta = theta
		if phi is not None:
			rd.phi = phi
		if energy is not None:
			rd.energy = max(0.0, energy)
		if final_vertex is not None:
			rd.final_vertex = final_vertex.astype(np.float32)

	def append_interaction(self, i: int, j: int, vertex: np.ndarray, theta: float, phi: float, energy: float, final_vertex: Optional[np.ndarray] = None):
		path = self.get_path(i, j)
		if len(path.steps) >= path.max_bounces:
			raise ValueError("Cannot append: max bounces reached")
		rd = RayData(vertex=vertex.astype(np.float32), theta=theta, phi=phi, energy=max(0.0, energy), final_vertex=final_vertex.astype(np.float32) if final_vertex is not None else None)
		path.add_step(rd)

	# ---------------- 검증 ----------------
	def enforce_all_connectivity(self):
		for p in self.paths:
			p.enforce_connectivity()

	# ---------------- 쿼리/통계 ----------------
	def energy_sum(self) -> float:
		return float(sum((s.energy for p in self.paths for s in p.steps)))

	def distribution_map(self, step: int = 0) -> np.ndarray:
		"""특정 step의 에너지 맵 (존재하지 않는 step은 0)."""
		m = np.zeros((self.H, self.W), dtype=np.float32)
		for i in range(self.H):
			for j in range(self.W):
				path = self.get_path(i, j)
				if step < len(path.steps):
					m[i, j] = path.steps[step].energy
		return m

	# ---------------- 직렬화 ----------------
	def export_numpy(self) -> Dict[str, Any]:
		# 단순 직렬화 (JSON 변환 전용이면 리스트 화 필요)
		data = []
		for p in self.paths:
			data.append([s.to_dict() for s in p.steps])
		return {
			'config': {
				'source_angle': self.cfg.source_angle,
				'ray_resolution': self.cfg.ray_resolution,
				'bounces': self.cfg.bounces,
				'source_origin': self.cfg.source_origin,
				'size': (self.H, self.W)
			},
			'paths': data
		}

	# ---------------- 유틸 ----------------
	@staticmethod
	def sph_to_cart(theta: float, phi: float) -> np.ndarray:
		st = math.sin(theta)
		return np.array([st * math.cos(phi), st * math.sin(phi), math.cos(theta)], dtype=np.float32)

	@staticmethod
	def cart_to_sph(v: np.ndarray) -> Tuple[float, float]:
		x, y, z = v
		r = math.sqrt(x*x + y*y + z*z) + 1e-12
		theta = math.acos(max(-1.0, min(1.0, z / r)))
		phi = math.atan2(y, x)
		return theta, phi


# ---- 사용 예시 ----
# cfg = LPFConfig(source_angle=120, ray_resolution=10, bounces=2)
# lpf = LPF(cfg)
# lpf.build_from_source_distribution(lambda th, ph: 1.0)  # 균일 분포
# print(lpf.energy_sum())
# path = lpf.get_path(0,0)
# lpf.append_interaction(0,0, vertex=np.array([0,0,1],dtype=np.float32), theta=0.5, phi=1.0, energy=path.steps[0].energy*0.9)
# dist0 = lpf.distribution_map(step=0)

