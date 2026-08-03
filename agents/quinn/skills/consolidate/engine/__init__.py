"""Finance Consolidation Engine — Layer A (deterministic, offline, no LLM).

Ingest -> normalise -> dedup -> categorise -> reconcile -> render.

Design invariants (enforced elsewhere by tests/no_network guard):
  * No network. No credentials. No send. The package imports nothing that
    can reach a bank, an email server, or a socket.
  * Reads local source files (read-only) and writes ONLY inside one WORKDIR.
  * Never fabricates a value: unknown -> flagged to open_items, never invented.

See BUILD-HANDOFF.md and the commission for the governing contract.
"""

__version__ = "0.1.0"
