"""
Protocols Module
=================

Certification protocols, evidence generation, and communication protocols.

Covers:
- Certification lifecycle management
- Evidence pack generation and verification
- Signature and seal protocols
- Inter-system communication protocols
- Regression monitoring protocols
"""

from .certification import (
    CertificationProtocol,
    CertificationPhase,
    CertificationOutcome,
    EvidencePack,
)
from .evidence import (
    EvidenceGenerator,
    EvidenceVerifier,
    EvidenceChain,
)
from .communication import (
    ProtocolMessage,
    ProtocolChannel,
    MessageType,
)

__all__ = [
    "CertificationProtocol",
    "CertificationPhase",
    "CertificationOutcome",
    "EvidencePack",
    "EvidenceGenerator",
    "EvidenceVerifier",
    "EvidenceChain",
    "ProtocolMessage",
    "ProtocolChannel",
    "MessageType",
]
