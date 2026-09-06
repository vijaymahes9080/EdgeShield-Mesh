"""
Unit tests for Neuromorphic SNN, Streaming Isolation Forest, Acoustic Tamper, GPS Teleportation, and Entropy Auditor.
"""

import pytest
import time
import os
import random
from services.detection_engine.detectors.neuromorphic_spiking import LeakyIntegrateFireDetector
from services.detection_engine.detectors.isolation_forest import StreamingIsolationForestDetector
from services.detection_engine.detectors.acoustic_side_channel import AcousticSideChannelDetector
from services.detection_engine.detectors.geo_spatial_teleportation import GeoSpatialTeleportationDetector
from services.detection_engine.detectors.quantum_entropy_auditor import QuantumEntropyAuditor


def test_lif_neuron_spike_on_rapid_delta():
    lif = LeakyIntegrateFireDetector(decay_rate=0.5, threshold=10.0, min_refractory_period=0.01)
    
    # Normal slow change -> no spike
    res1 = lif.process_sample("dev1", "flow_rate", 10.0, timestamp=100.0)
    res2 = lif.process_sample("dev1", "flow_rate", 10.5, timestamp=101.0)
    assert res1 is None
    assert res2 is None
    
    # Sudden huge burst delta -> fires spike!
    res3 = lif.process_sample("dev1", "flow_rate", 150.0, timestamp=101.1)
    assert res3 is not None
    assert res3.device_id == "dev1"
    assert res3.membrane_potential >= 10.0


def test_streaming_isolation_forest_anomaly():
    iso = StreamingIsolationForestDetector(num_trees=15, max_samples=32, anomaly_threshold=0.5)
    
    # Train normal baseline around (10.0, 20.0)
    for _ in range(25):
        iso.update_baseline({"temp": 10.0 + random.uniform(-1, 1), "pressure": 20.0 + random.uniform(-0.5, 0.5)})
        
    # Extreme outlier has short path length -> high anomaly score
    score = iso.compute_anomaly_score({"temp": 999.0, "pressure": 500.0})
    assert score > 0.4
    
    alert = iso.evaluate_sample("sensor-x", {"temp": 999.0, "pressure": 500.0})
    assert alert is not None
    assert alert["is_anomaly"] is True


def test_acoustic_tamper_detector():
    detector = AcousticSideChannelDetector(sample_rate_hz=1000.0, nominal_motor_hz=60.0)
    
    # Generate high frequency noisy signal (500Hz)
    import math
    samples = [math.sin(2 * math.pi * 500 * (i / 1000.0)) for i in range(100)]
    
    alert = detector.analyze_waveform("pump-01", samples)
    assert alert is not None
    assert alert.dominant_frequency_hz > 100.0


def test_gps_teleportation_detector():
    gps = GeoSpatialTeleportationDetector(max_speed_mps=20.0)
    
    # Fix 1: New York
    gps.update_gps_fix("tractor-01", 40.7128, -74.0060, timestamp=1000.0)
    
    # Fix 2: 1 second later in London -> impossible speed!
    alert = gps.update_gps_fix("tractor-01", 51.5074, -0.1278, timestamp=1001.0)
    assert alert is not None
    assert alert.inferred_speed_mps > 1000.0


def test_quantum_entropy_auditor():
    auditor = QuantumEntropyAuditor()
    
    # Strong random bytes
    good_bytes = os.urandom(1024)
    res_good = auditor.audit_sample("tpm_trng_0", good_bytes)
    assert res_good is None
    
    # Degraded / repeating bytes (all zeroes)
    bad_bytes = b"\x00" * 1024
    res_bad = auditor.audit_sample("tpm_trng_0", bad_bytes)
    assert res_bad is not None
    assert res_bad.shannon_entropy < 1.0
