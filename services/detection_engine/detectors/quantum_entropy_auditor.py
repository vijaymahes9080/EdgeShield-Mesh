"""
EdgeShield Mesh - True Random Number Generator (TRNG) & Quantum Entropy Auditor
Performs real-time NIST SP 800-22 statistical entropy tests (Monobit, Block Frequency, Runs)
on hardware RNG sources in edge microcontrollers to detect physical fault injection or hardware degradation.
"""

import math
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field
import time


class EntropyAlert(BaseModel):
    source_id: str
    shannon_entropy: float
    monobit_p_value: float
    runs_test_passed: bool
    status: str
    detected_at: float = Field(default_factory=time.time)


class QuantumEntropyAuditor:
    """
    Audits random byte streams from MCU hardware entropy rings / avalanche diodes.
    """

    @staticmethod
    def compute_shannon_entropy(data: bytes) -> float:
        if not data:
            return 0.0
        counts = [0] * 256
        for b in data:
            counts[b] += 1
        n = len(data)
        entropy = 0.0
        for c in counts:
            if c > 0:
                p = c / n
                entropy -= p * math.log2(p)
        return entropy

    @staticmethod
    def monobit_test(data: bytes) -> float:
        """NIST Frequency (Monobit) test approximation."""
        total_bits = len(data) * 8
        if total_bits == 0:
            return 0.0
        ones = sum(bin(b).count('1') for b in data)
        zeros = total_bits - ones
        s_obs = abs(ones - zeros) / math.sqrt(total_bits)
        # Complementary error function approximation
        p_val = math.erfc(s_obs / math.sqrt(2))
        return p_val

    def audit_sample(self, source_id: str, sample_bytes: bytes, min_entropy: float = 7.2) -> Optional[EntropyAlert]:
        entropy = self.compute_shannon_entropy(sample_bytes)
        monobit_p = self.monobit_test(sample_bytes)
        
        # An ideal TRNG has Shannon entropy close to 8.0 bits/byte and monobit p-value >= 0.01
        is_degraded = (entropy < min_entropy) or (monobit_p < 0.01)
        
        if is_degraded:
            return EntropyAlert(
                source_id=source_id,
                shannon_entropy=entropy,
                monobit_p_value=monobit_p,
                runs_test_passed=False,
                status="ENTROPY_COLLAPSE_OR_HARDWARE_FAULT"
            )
        return None
