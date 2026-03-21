"""
Agent Roles
===========

Each role has a specific prompt template and session behavior.

Roles:
- Initializer: Reads seed, decomposes into DAG, runs once.
- Explorer: Picks an objective, implements it, commits output.
- Reviewer: Independent peer review of explorer output.
- Director: Visual tuning via Gemini (multimodal video review).
- Integrator: Periodic coherence check across verified nodes.
- Synthesizer: Assembles verified nodes into final deliverable.
"""
