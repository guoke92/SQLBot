"""Contract issues and the single contract validation entry point.

Submodules are imported directly so that ``query_contract`` can depend on
``issues`` without pulling in ``validation``, which depends on it in turn.
"""
