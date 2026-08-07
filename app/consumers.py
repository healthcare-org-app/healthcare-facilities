"""Kafka consumers for facilities-service.

One handler per subscribed topic. Handlers are best-effort logging plus
audit — services override this file to implement real cross-domain behavior.
"""
from __future__ import annotations

import logging

from healthcare_common.audit import emit_audit

log = logging.getLogger("facilities-service.consumers")


def register(svc) -> None:
    bus = svc.bus
    # This service does not subscribe to any topics.
    return

