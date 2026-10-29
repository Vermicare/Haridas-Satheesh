#!/usr/bin/env python3
"""Read-only Zhou2020 NEMAR Git-tree inventory; no EEG or trial labels accessed.

Usage: python zhou2020_tree_inventory_v03.py > inventory.json
Requires public GitHub API access. GITHUB_TOKEN optional for rate limits.
The pinned ref is not a publisher-signed data checksum.
"""
import json
import os
import re
import sys
import urllib.request
from collections import defaultdict

REPO = "nemarDatasets/nm000237"
REF = "a291ed8a2afab3f93b85a540134dceb98092fcaf"
API = f"https://api.github.com/repos/{REPO}/git/trees/"
SUBJECT = re.compile(r"^sub-(\d+)$")
RECORDING = re.compile(
    r"^ses-(\d+)/eeg/sub-(\d+)_ses-(\d+)_task-imagery_run-(\d+)_(channels|events)\.tsv$"
)


def get_json(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "wbi-metadata-inventory-v03"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return json.load(response)


def audit(root, trees):
    if root.get("truncated") or root.get("sha") != REF:
        raise ValueError("root tree truncated or not pinned")
    subjects = {}
    for entry in root.get("tree", []):
        match = SUBJECT.fullmatch(entry.get("path", ""))
        if match and entry.get("type") == "tree":
            subject = int(match.group(1))
            if subject in subjects:
                raise ValueError("duplicate subject tree")
            subjects[subject] = entry["sha"]
    if set(subjects) != set(range(1, 21)):
        raise ValueError("expected exactly subjects 1..20")
    output = []
    for subject in sorted(subjects):
        tree = trees.get(subject)
        if not isinstance(tree, dict) or tree.get("truncated") or tree.get("sha") != subjects[subject]:
            raise ValueError(f"subject {subject} missing/truncated/tree SHA mismatch")
        session_dirs = set()
        records = defaultdict(lambda: {"channels": set(), "events": set()})
        for entry in tree.get("tree", []):
            path = entry.get("path", "")
            if entry.get("type") == "tree" and re.fullmatch(r"ses-\d+", path):
                session_dirs.add(int(path.split("-")[1]))
            if entry.get("type") != "blob" or not path.endswith(("_channels.tsv", "_events.tsv")):
                continue
            m = RECORDING.fullmatch(path)
            if not m:
                raise ValueError(f"unexpected recording metadata filename: {path}")
            ses, sub, embedded_ses, run, kind = m.groups()
            ses, sub, embedded_ses, run = map(int, (ses, sub, embedded_ses, run))
            if sub != subject or ses != embedded_ses or ses not in range(7):
                raise ValueError(f"invalid subject/session identifier: {path}")
            if run in records[ses][kind]:
                raise ValueError(f"duplicate {kind} run: {path}")
            records[ses][kind].add(run)
        if any(ses not in range(7) for ses in session_dirs):
            raise ValueError(f"unexpected session directory for subject {subject}")
        if set(records) - session_dirs:
            raise ValueError(f"metadata without session directory for subject {subject}")
        counts = []
        for ses in range(7):
            channels = records[ses]["channels"]
            events = records[ses]["events"]
            if channels != events:
                raise ValueError(f"subject {subject} session {ses}: unpaired events/channels")
            counts.append({"session": ses, "present": ses in session_dirs,
                           "run_indices": sorted(channels), "count": len(channels)})
        output.append({"subject": subject, "subject_tree_sha1": subjects[subject],
                       "sessions": counts, "recordings": sum(x["count"] for x in counts)})
    observed = sum(x["recordings"] for x in output)
    absent = [{"subject": x["subject"], "session": s["session"]}
              for x in output for s in x["sessions"] if not s["present"]]
    irregular = [{"subject": x["subject"], "session": s["session"],
                  "run_indices": s["run_indices"]}
                 for x in output for s in x["sessions"] if s["run_indices"] != list(range(6))]
    return {"schema": "ZHOU2020_TREE_INVENTORY_V03", "upstream_repository": REPO,
            "pinned_ref": REF, "observed_subjects": len(output),
            "observed_session_directories": 140 - len(absent),
            "nominal_runs": 840, "observed_channel_metadata_files": observed,
            "observed_event_metadata_files": observed,
            "difference_from_nominal": observed - 840,
            "absent_session_directories": absent, "noncanonical_run_sets": irregular,
            "subject_inventory": output,
            "metadata_pairing": "PASS", "eeg_signals_read": False,
            "trial_event_rows_read": False, "publisher_checksum_verified": False,
            "maturity_advanced": False,
            "limitations": "Git-tree filenames only; does not prove original recordings, EEG signals, event counts or label validity."}


def main():
    root = get_json(API + REF)
    subjects = {int(m.group(1)): entry["sha"] for entry in root.get("tree", [])
                if (m := SUBJECT.fullmatch(entry.get("path", ""))) and entry.get("type") == "tree"}
    trees = {s: get_json(API + sha + "?recursive=1") for s, sha in sorted(subjects.items())}
    print(json.dumps(audit(root, trees), indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        sys.exit(1)
