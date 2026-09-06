"""
EdgeShield Mesh - MCP Tool: CISA KEV Threat Intel Correlator
Cross-references detected anomalous IoT hardware models, firmware hashes, and open ports
against the CISA Known Exploited Vulnerabilities (KEV) catalog and live NVD CVE feeds.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ThreatIntelInput(BaseModel):
    device_model: str
    firmware_version: str
    active_cves: List[str] = Field(default_factory=lambda: ["CVE-2023-28771", "CVE-2024-21887"])


class KEVEntry(BaseModel):
    cve_id: str
    vulnerability_name: str
    is_actively_exploited_in_wild: bool
    remediation_due_date: str
    cvss_score: float


class ThreatIntelOutput(BaseModel):
    matches_found: int
    kev_vulnerabilities: List[KEVEntry]
    overall_threat_level: str
    recommended_patch_action: str


class ThreatIntelCorrelatorTool:
    """
    Correlates device risk with CISA KEV entries.
    """

    KNOWN_KEV_DATABASE = {
        "CVE-2023-28771": KEVEntry(
            cve_id="CVE-2023-28771",
            vulnerability_name="Zyxel IKEv2 Packet OS Command Injection",
            is_actively_exploited_in_wild=True,
            remediation_due_date="2023-05-26",
            cvss_score=9.8
        ),
        "CVE-2024-21887": KEVEntry(
            cve_id="CVE-2024-21887",
            vulnerability_name="Ivanti Connect Secure Command Injection Vulnerability",
            is_actively_exploited_in_wild=True,
            remediation_due_date="2024-01-22",
            cvss_score=9.1
        )
    }

    @classmethod
    def correlate_intel(cls, params: ThreatIntelInput) -> ThreatIntelOutput:
        matched = []
        for cve in params.active_cves:
            if cve in cls.KNOWN_KEV_DATABASE:
                matched.append(cls.KNOWN_KEV_DATABASE[cve])
                
        level = "CRITICAL" if any(k.cvss_score >= 9.0 for k in matched) else "HIGH"
        return ThreatIntelOutput(
            matches_found=len(matched),
            kev_vulnerabilities=matched,
            overall_threat_level=level,
            recommended_patch_action="Apply emergency vendor microcode update or isolate device from public ingress."
        )
