"""Project lifecycle stubs for Citera."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    name: str
    stage: str
    path: str
