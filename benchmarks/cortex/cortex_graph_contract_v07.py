#!/usr/bin/env python3
"""Fixed-case fictional CORTEX v0.7 downstream RDF semantic-contract audit.

Rejects altered RDF relationships after the existing v0.5 exporter. This is NOT
PROV compliance, source authentication, or general semantic verification.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

from rdflib import Graph, Namespace, RDF, URIRef

VERSION = "cortex-fixed-graph-contract-v0.7"
MAX_BYTES = 100_000
EX = Namespace("https://example.org/cortex-fictional/20261024/")
PROV = Namespace("http://www.w3.org/ns/prov#")
CORTEX = Namespace("https://example.org/cortex-fictional/vocab#")

# Independently declared allowlist for the frozen, author-created fictional
# 14-triple case. Not inferred from v0.5 code or user-supplied graph contents.
EXPECTED = frozenset({
    (EX["source-b03"], RDF.type, PROV.Entity),
    (EX["source-b07"], RDF.type, PROV.Entity),
    (EX["archive-H11"], RDF.type, PROV.Entity),
    (EX["archive-H12"], RDF.type, PROV.Entity),
    (EX["hold-H11"], RDF.type, PROV.Entity),
    (EX["hold-H11"], PROV.wasDerivedFrom, EX["archive-H11"]),
    (EX["checklist-H12"], RDF.type, PROV.Entity),
    (EX["checklist-H12"], PROV.wasDerivedFrom, EX["archive-H12"]),
    (EX["checklist-B"], RDF.type, PROV.Entity),
    (EX["checklist-B"], PROV.wasDerivedFrom, EX["source-b07"]),
    (EX["checklist-B"], CORTEX.supersedes, EX["checklist-H12"]),
    (EX["hold-clarification"], RDF.type, PROV.Entity),
    (EX["hold-clarification"], PROV.wasDerivedFrom, EX["source-b03"]),
    (EX["hold-clarification"], CORTEX.clarifies, EX["hold-H11"]),
})
ALLOWED_PROV_PREDICATES = frozenset({PROV.wasDerivedFrom})


def audit_bytes(raw: bytes) -> dict:
    """Parse bounded Turtle, compare RDF triples (not textual serialization)."""
    base = {"schema": VERSION, "scope": "frozen_author_created_fictional_graph",
            "valid": False, "expected_triples": len(EXPECTED),
            "observed_triples": "TBD", "missing_triples": "TBD",
            "unexpected_triples": "TBD", "error": "TBD"}
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        return {**base, "error": "invalid_or_oversized_input"}
    try:
        graph = Graph()
        graph.parse(data=raw.decode("utf-8"), format="turtle")
        observed = frozenset(graph)
    except (Exception):  # fail closed; do not echo attacker-supplied parser text
        return {**base, "error": "invalid_turtle"}
    missing = EXPECTED - observed
    unexpected = observed - EXPECTED
    unsafe_prov = any(isinstance(p, URIRef) and str(p).startswith(str(PROV))
                      and p not in ALLOWED_PROV_PREDICATES
                      for _, p, _ in observed)
    ok = not missing and not unexpected and len(observed) == len(EXPECTED)
    return {**base, "valid": ok, "observed_triples": len(observed),
            "missing_triples": len(missing), "unexpected_triples": len(unexpected),
            "error": "none" if ok else ("unsupported_prov_predicate" if unsafe_prov
                                         else "graph_contract_mismatch")}


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2 or args[0] != "audit":
        print("usage: cortex_graph_contract_v07.py audit FROZEN_TURTLE", file=sys.stderr)
        return 2
    try:
        with Path(args[1]).open("rb") as handle:
            raw = handle.read(MAX_BYTES + 1)
        result = audit_bytes(raw)
    except OSError:
        result = {"schema": VERSION, "scope": "frozen_author_created_fictional_graph",
                  "valid": False, "error": "unreadable_input"}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
