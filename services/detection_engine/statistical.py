"""
Statistical Baseline and EWMA Anomaly Detector
Tracks rolling statistics and flags multi-sigma deviations.
"""
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from packages.shared.models import BaselineMetric, NormalizedTelemetry, DetectorResult, IncidentSeverity


class StatisticalBaselineEngine:
    def __init__(self, alpha: float = 0.2, z_score_threshold: float = 3.0, min_samples: int = 5):
        self.alpha = alpha  # EWMA smoothing factor
        self.z_score_threshold = z_score_threshold
        self.min_samples = min_samples
        # Baselines: (device_type, metric_name) -> BaselineMetric
        self.baselines: Dict[Tuple[str, str], BaselineMetric] = {}
        # Historical buffer: (device_type, metric_name) -> list of floats
        self.buffers: Dict[Tuple[str, str], List[float]] = {}

    def update_and_detect(self, telemetry: NormalizedTelemetry) -> List[DetectorResult]:
        results = []
        dev_type = telemetry.device_type

        for metric, val in telemetry.measurements.items():
            if not isinstance(val, (int, float)):
                continue
            val_f = float(val)
            key = (dev_type, metric)

            if key not in self.buffers:
                self.buffers[key] = []
            self.buffers[key].append(val_f)
            if len(self.buffers[key]) > 200:
                self.buffers[key] = self.buffers[key][-200:]

            samples = self.buffers[key]
            n = len(samples)

            # Compute stats
            mean = sum(samples) / n
            variance = sum((x - mean) ** 2 for x in samples) / (n - 1) if n > 1 else 0.0
            std_dev = math.sqrt(variance)

            # Update EWMA
            if key not in self.baselines:
                ewma = val_f
            else:
                ewma = self.alpha * val_f + (1 - self.alpha) * self.baselines[key].ewma

            baseline = BaselineMetric(
                device_type=dev_type,
                metric_name=metric,
                rolling_mean=round(mean, 3),
                rolling_std=round(std_dev, 3),
                min_observed=round(min(samples), 3),
                max_observed=round(max(samples), 3),
                ewma=round(ewma, 3),
                sample_count=n,
                last_updated=datetime.now(timezone.utc)
            )
            self.baselines[key] = baseline

            # Detect Anomaly if enough samples
            if n >= self.min_samples and std_dev > 0.001:
                z_score = abs(val_f - mean) / std_dev
                if z_score >= self.z_score_threshold:
                    results.append(
                        DetectorResult(
                            detector_id="statistical_drift",
                            severity=IncidentSeverity.MEDIUM if z_score < 4.5 else IncidentSeverity.HIGH,
                            confidence=min(0.99, round(0.5 + (z_score / 10.0), 2)),
                            device_id=telemetry.device_id,
                            observed_fields={
                                "metric": metric,
                                "observed_value": val_f,
                                "rolling_mean": baseline.rolling_mean,
                                "rolling_std": baseline.rolling_std,
                                "ewma": baseline.ewma,
                                "z_score": round(z_score, 2),
                                "sample_count": n
                            },
                            explanation=f"Statistical anomaly in metric '{metric}' on {telemetry.device_id}: observed {val_f} deviates {z_score:.2f} standard deviations from baseline mean {mean:.2f}.",
                            evidence_ids=[f"ev-stat-{telemetry.event_id[:8]}"],
                            recommended_next_step="Review environmental trend or evaluate sensor calibration."
                        )
                    )

        return results

    def get_baseline(self, device_type: str, metric_name: str) -> Optional[BaselineMetric]:
        return self.baselines.get((device_type, metric_name))
