"""
Roles — Agent Role Implementations
====================================

Each role has a specific prompt template, tool set, and evaluation criteria.
Roles are the functional units of the harness.
"""

from roles.initializer import run_initializer
from roles.explorer import run_explorer
from roles.reviewer import run_reviewer
from roles.director import run_director
from roles.integrator import run_integrator
from roles.synthesizer import run_synthesizer

__all__ = [
    "run_initializer",
    "run_explorer",
    "run_reviewer",
    "run_director",
    "run_integrator",
    "run_synthesizer",
]
