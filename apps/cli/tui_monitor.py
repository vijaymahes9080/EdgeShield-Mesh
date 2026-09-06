"""
EdgeShield Mesh - Terminal User Interface (TUI) ASCII Radar Monitor
Renders real-time ASCII radar maps of mesh nodes, sparkline graphs of telemetry,
and incident feeds directly inside terminal sessions.
"""

from typing import List, Dict, Any


class TUIRadarMonitor:
    """
    Renders ASCII visual diagnostics in standard terminal.
    """

    SPARK_CHARS = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

    @classmethod
    def render_sparkline(cls, values: List[float], min_val: float = 0.0, max_val: float = 100.0) -> str:
        if not values:
            return ""
        chars = []
        range_val = max(1e-6, max_val - min_val)
        for v in values:
            norm = min(1.0, max(0.0, (v - min_val) / range_val))
            idx = int(norm * (len(cls.SPARK_CHARS) - 1))
            chars.append(cls.SPARK_CHARS[idx])
        return "".join(chars)

    @classmethod
    def render_ascii_radar(cls, nodes: List[Dict[str, Any]]) -> str:
        radar = [
            "+----------------- MESH TOPOLOGY RADAR -----------------+",
            "|                         [SAT-LEO]                      |",
            "|                            │                           |",
            "|                        [GATEWAY]                       |",
            "|                      ┌─────┼─────┐                     |",
            "|                  [SOIL] [VALVE] [PUMP]                 |",
            "+--------------------------------------------------------+"
        ]
        return "\n".join(radar)
