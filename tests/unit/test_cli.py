"""
Unit tests for EdgeShield CLI, TUI ASCII Radar, and Prometheus Metrics Exporter.
"""

import pytest
from apps.cli.edgeshield_cli import EdgeShieldCLI
from apps.cli.tui_monitor import TUIRadarMonitor
from apps.cli.exporter import EdgeMetricsExporter


def test_edgeshield_cli_status():
    cli = EdgeShieldCLI()
    res = cli.execute_command(["status"])
    assert res["status"] == "HEALTHY"
    assert res["mesh_nodes_online"] == 5


def test_edgeshield_cli_triage():
    cli = EdgeShieldCLI()
    res = cli.execute_command(["triage-incident", "--id", "inc-12345"])
    assert res["incident_id"] == "inc-12345"
    assert res["triage_state"] == "UNDER_INVESTIGATION"


def test_tui_sparkline():
    values = [10.0, 20.0, 50.0, 80.0, 100.0]
    spark = TUIRadarMonitor.render_sparkline(values, min_val=0.0, max_val=100.0)
    assert len(spark) == 5
    assert spark[-1] == "█"


def test_prometheus_exporter():
    exporter = EdgeMetricsExporter()
    exporter.record_ingest(50)
    exporter.record_anomaly(2)
    
    text = exporter.export_prometheus_text()
    assert "edgeshield_telemetry_ingested_total 50" in text
    assert "edgeshield_anomalies_detected_total 2" in text
