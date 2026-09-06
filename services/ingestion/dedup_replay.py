"""
Deduplication and Replay Attack Detector
Maintains sliding cache of message hashes, nonces, sequence numbers, and max seen timestamps.
"""
from typing import Dict, Set, Tuple, Optional
from datetime import datetime, timezone, timedelta
from packages.shared.models import NormalizedTelemetry


class DedupReplayTracker:
    def __init__(self, cache_ttl_seconds: int = 60, max_sequence_gap: int = 1000):
        self.cache_ttl_seconds = cache_ttl_seconds
        self.max_sequence_gap = max_sequence_gap
        # Hash cache: (device_id, payload_hash) -> expires_at
        self._hash_cache: Dict[Tuple[str, str], datetime] = {}
        # Nonce cache: (device_id, nonce) -> expires_at
        self._nonce_cache: Dict[Tuple[str, str], datetime] = {}
        # Device max timestamp: device_id -> max_seen_timestamp
        self._device_max_ts: Dict[str, datetime] = {}
        # Device last seq: device_id -> last_seq
        self._device_last_seq: Dict[str, int] = {}

    def _purge_expired(self, now: datetime):
        self._hash_cache = {k: exp for k, exp in self._hash_cache.items() if exp > now}
        self._nonce_cache = {k: exp for k, exp in self._nonce_cache.items() if exp > now}

    def check_duplicate(self, telemetry: NormalizedTelemetry) -> Tuple[bool, str]:
        """
        Returns (is_duplicate, reason)
        """
        now = datetime.now(timezone.utc)
        self._purge_expired(now)

        key = (telemetry.device_id, telemetry.payload_hash)
        if key in self._hash_cache:
            return True, f"Identical payload hash {telemetry.payload_hash[:12]} observed within deduplication window"

        # Record hash
        self._hash_cache[key] = now + timedelta(seconds=self.cache_ttl_seconds)
        return False, ""

    def check_replay_and_rollback(self, telemetry: NormalizedTelemetry) -> Tuple[bool, str]:
        """
        Checks nonce reuse, sequence rollback, and timestamp rollback.
        Returns (is_replay_or_rollback, reason)
        """
        now = datetime.now(timezone.utc)
        dev_id = telemetry.device_id

        # 1. Nonce check if non-empty
        if telemetry.nonce:
            nonce_key = (dev_id, telemetry.nonce)
            if nonce_key in self._nonce_cache:
                return True, f"Reused cryptographic nonce '{telemetry.nonce}' detected for device {dev_id}"
            self._nonce_cache[nonce_key] = now + timedelta(seconds=self.cache_ttl_seconds * 2)

        # 2. Timestamp rollback check (tolerance 10 seconds)
        if dev_id in self._device_max_ts:
            max_seen = self._device_max_ts[dev_id]
            if telemetry.timestamp < max_seen - timedelta(seconds=10):
                diff = (max_seen - telemetry.timestamp).total_seconds()
                return True, f"Timestamp rollback of {diff:.1f}s detected (incoming: {telemetry.timestamp.isoformat()} vs max seen: {max_seen.isoformat()})"

        # Update max timestamp
        if dev_id not in self._device_max_ts or telemetry.timestamp > self._device_max_ts[dev_id]:
            self._device_max_ts[dev_id] = telemetry.timestamp

        # Update sequence
        self._device_last_seq[dev_id] = telemetry.seq

        return False, ""
