"""Kafka consumers for facilities-service.

One handler per subscribed topic. Real handlers write to this service's own
database and/or publish follow-up events; stub handlers just log + audit.
"""
from __future__ import annotations

import logging

from psycopg.types.json import Json

from healthcare_common.audit import emit_audit

log = logging.getLogger("facilities-service.consumers")

TABLE = "facilities"


def register(svc) -> None:
    bus = svc.bus
    db = svc.db
    clients = svc.clients
    # This service does not subscribe to any topics.
    return

