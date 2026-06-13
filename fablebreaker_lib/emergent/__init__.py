"""
Emergent Module
================

Detection, monitoring, and analysis of emergent behaviors in AI systems.

Covers:
- Emergent behavior detection and classification
- Behavioral monitoring and drift detection
- Safety boundary enforcement
- Anomaly detection in evaluation outputs
- Pattern recognition for unexpected capabilities
"""

from .detection import (
    EmergentBehavior,
    BehaviorClassification,
    EmergentDetector,
    DetectionResult,
)
from .monitoring import (
    BehaviorMonitor,
    DriftMetric,
    MonitoringAlert,
    AlertSeverity,
)
from .safety import (
    SafetyBoundary,
    SafetyEnvelope,
    BoundaryViolation,
    SafetyMonitor,
    EVALUATION_SAFETY_ENVELOPE,
)

__all__ = [
    "EmergentBehavior",
    "BehaviorClassification",
    "EmergentDetector",
    "DetectionResult",
    "BehaviorMonitor",
    "DriftMetric",
    "MonitoringAlert",
    "AlertSeverity",
    "SafetyBoundary",
    "SafetyEnvelope",
    "BoundaryViolation",
    "SafetyMonitor",
    "EVALUATION_SAFETY_ENVELOPE",
]
