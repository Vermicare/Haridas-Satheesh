#!/usr/bin/env python3
"""Fixed fictional provenance-of-assertion control, not authorization or truth.

Uses RDF named graphs to keep two competing assertions separate. W3C PROV-O
prov:Bundle is an entity that can itself have provenance; named RDF graphs
are a representation choice, not mandated by PROV-O. No real data or network.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from rdflib import Dataset, Namespace, RDF, URIRef

VERSION = "cortex-assertion-bundles-v0.9"
MAX_BYTES = 40_000
EX = Namespace("https://example.org/cortex-fictional/20261024/")
CORTEX = Namespace("https://example.org/cortex-fictional/vocab#")
PROV = Namespace("http://www.w3.org/ns/prov#")

# Independently specified fixed-case semantic contract. Two incompatible
# *interpretations*, not an OWL-logical contradiction or adjudicated facts.
EXPECTED = frozenset({
    (EX["checklist-B"], CORTEX.supersedes, EX["checklist-H12"], EX["bundle-A"]),
    (EX["checklist-B"], PROV.wasDerivedFrom, EX["source-b07"], EX["bundle-A"]),
    (EX["checklist-B"], CORTEX.clarifies, EX["checklist-H12"], EX["bundle-B"]),
    (EX["checklist-B"], PROV.wasDerivedFrom, EX["source-b07"], EX["bundle-B"]),
    (EX["bundle-A"], RDF.type, PROV.Bundle, EX["bundle-metadata"]),
    (EX["bundle-B"], RDF.type, PROV.Bundle, EX["bundle-metadata"]),
    (EX["bundle-A"], PROV.wasAttributedTo, EX["fictional-analyst-A"], EX["bundle-metadata"]),
    (EX["bundle-B"], PROV.wasAttributedTo, EX["fictional-analyst-B"], EX["bundle-metadata"]),
    (EX["fictional-analyst-A"], RDF.type, PROV.Agent, EX["bundle-metadata"]),
    (EX["fictional-analyst-B"], RDF.type, PROV.Agent, EX["bundle-metadata"]),
})


def _line(quad):
    if not all(isinstance(term, URIRef) for term in quad):
        raise ValueError("non_iri_term")
    return " ".join(term.n3() for term in quad) + " .\n"


def build_example() -> bytes:
    """Generate an intentionally limited, deterministic N-Quads example."""
    return "".join(sorted(_line(q) for q in EXPECTED)).encode("ascii")


def audit_bytes(raw: bytes) -> dict:
    """Fail closed on altered attribution, changed context or unsupported edge."""
    base = {"schema": VERSION, "fictional": True, "valid": False,
            "expected_quads": len(EXPECTED), "observed_quads": "TBD",
            "missing_quads": "TBD", "unexpected_quads": "TBD",
            "bundle_count": "TBD", "independent_truth": "TBD",
            "authorization": "TBD", "error": "TBD"}
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BYTES:
        return {**base, "error": "invalid_or_oversized_input"}
    try:
        ds = Dataset()
        ds.parse(data=raw.decode("utf-8"), format="nquads")
        observed = frozenset(ds.quads((None, None, None, None)))
    except Exception:
        # Do not echo user-supplied parser content or source identifiers.
        return {**base, "error": "invalid_nquads"}
    missing, unexpected = EXPECTED - observed, observed - EXPECTED
    valid = not missing and not unexpected and len(observed) == len(EXPECTED)
    return {**base, "valid": valid, "observed_quads": len(observed),
            "missing_quads": len(missing), "unexpected_quads": len(unexpected),
            "bundle_count": 2 if valid else "TBD",
            "error": "none" if valid else "assertion_or_attribution_mismatch"}


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args == ["demo"]:
        report = audit_bytes(build_example())
    elif len(args) == 2 and args[0] == "audit":
        try:
            with Path(args[1]).open("rb") as handle:
                raw = handle.read(MAX_BYTES + 1)
            report = audit_bytes(raw)
        except OSError:
            report = {"schema": VERSION, "fictional": True, "valid": False,
                      "error": "unreadable_input", "independent_truth": "TBD",
                      "authorization": "TBD"}
    else:
        print("usage: cortex_assertion_bundles_v09.py demo | audit FILE.nq", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
