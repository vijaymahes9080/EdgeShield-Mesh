"""
EdgeShield Mesh - Streaming Isolation Forest Detector
Lightweight online tree-ensemble anomaly detector that builds micro iTrees
over rolling multi-metric sensor vectors without heavy matrix dependencies.
"""

import random
import math
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import time


class StreamingIsolationTree:
    def __init__(self, max_depth: int = 8):
        self.max_depth = max_depth
        self.split_feature: Optional[str] = None
        self.split_value: Optional[float] = None
        self.left: Optional['StreamingIsolationTree'] = None
        self.right: Optional['StreamingIsolationTree'] = None
        self.size = 0

    def fit(self, data: List[Dict[str, float]], current_depth: int = 0):
        self.size = len(data)
        if current_depth >= self.max_depth or len(data) <= 1:
            return

        features = list(data[0].keys())
        self.split_feature = random.choice(features)
        vals = [d[self.split_feature] for d in data]
        min_v, max_v = min(vals), max(vals)
        if min_v == max_v:
            return

        self.split_value = random.uniform(min_v, max_v)
        left_data = [d for d in data if d[self.split_feature] < self.split_value]
        right_data = [d for d in data if d[self.split_feature] >= self.split_value]

        if left_data:
            self.left = StreamingIsolationTree(self.max_depth)
            self.left.fit(left_data, current_depth + 1)
        if right_data:
            self.right = StreamingIsolationTree(self.max_depth)
            self.right.fit(right_data, current_depth + 1)

    def path_length(self, point: Dict[str, float], current_depth: int = 0) -> float:
        if self.left is None and self.right is None:
            return current_depth + self._c(self.size)
        if self.split_feature is None or self.split_value is None:
            return current_depth

        val = point.get(self.split_feature, 0.0)
        if val < self.split_value and self.left is not None:
            return self.left.path_length(point, current_depth + 1)
        elif self.right is not None:
            return self.right.path_length(point, current_depth + 1)
        return current_depth

    @staticmethod
    def _c(n: int) -> float:
        if n <= 1:
            return 0.0
        if n == 2:
            return 1.0
        # Harmonic number approximation H(n-1) = ln(n-1) + 0.5772156649
        h = math.log(n - 1) + 0.5772156649
        return 2.0 * h - (2.0 * (n - 1) / n)


class StreamingIsolationForestDetector:
    """
    Forest of isolation trees trained on sliding window baseline telemetry.
    """

    def __init__(self, num_trees: int = 15, max_samples: int = 64, anomaly_threshold: float = 0.65):
        self.num_trees = num_trees
        self.max_samples = max_samples
        self.anomaly_threshold = anomaly_threshold
        self.trees: List[StreamingIsolationTree] = []
        self.buffer: List[Dict[str, float]] = []

    def update_baseline(self, vector: Dict[str, float]):
        self.buffer.append(vector)
        if len(self.buffer) > self.max_samples:
            self.buffer.pop(0)

        # Retrain trees if buffer is full
        if len(self.buffer) >= 16:
            self.trees = []
            for _ in range(self.num_trees):
                sample_data = random.sample(self.buffer, min(len(self.buffer), 32))
                t = StreamingIsolationTree()
                t.fit(sample_data)
                self.trees.append(t)

    def compute_anomaly_score(self, vector: Dict[str, float]) -> float:
        if not self.trees:
            return 0.0
        avg_path = sum(t.path_length(vector) for t in self.trees) / len(self.trees)
        c_n = StreamingIsolationTree._c(len(self.buffer) if self.buffer else 32)
        if c_n == 0:
            return 0.0
        score = 2.0 ** (-avg_path / c_n)
        return score

    def evaluate_sample(self, device_id: str, vector: Dict[str, float]) -> Optional[Dict[str, Any]]:
        score = self.compute_anomaly_score(vector)
        if score >= self.anomaly_threshold:
            return {
                "device_id": device_id,
                "anomaly_score": score,
                "threshold": self.anomaly_threshold,
                "features": vector,
                "is_anomaly": True
            }
        self.update_baseline(vector)
        return None
