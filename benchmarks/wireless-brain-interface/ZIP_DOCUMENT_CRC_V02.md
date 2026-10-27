# WBI BNCI2a ZIP document CRC integrity — v0.2 (2026-10-27)

**Evidence type:** executable, fictional ZIP integrity negative control. **No EEG downloaded, read or scored.** Research / Simulation unchanged. Existing frozen synthetic evaluator is untouched.

## Hypothesis and code-review finding

The v0.1 archive inspector streamed all 18 expected GDF members, but it merely **listed** allowlisted `.txt`, `.md`, and `.pdf` members without opening them. A ZIP entry's CRC is checked by Python's `zipfile` only when its uncompressed content is read. Therefore v0.1 could report an archive-integrity pass for an archive with a corrupt allowed document, even though GDFs were sound. This is an *integrity-contract gap*, not evidence of malicious publisher data or EEG invalidity.

## Controlled adversarial experiment

- **Fixture:** generated in memory/on a temporary disk by `test_bnci2a_source_archive_preflight.py`: 18 fictional, minimally signed GDF entries and one `README.txt`; no EEG or labels.
- **Negative control:** write `README.txt` uncompressed, flip one payload byte while retaining its original ZIP CRC, and assert fail-closed rejection.
- **Positive controls:** intact `README.txt` emits SHA-256, byte count and declared ZIP CRC without publishing document text; an empty `NOTES.md` hashes correctly.
- **Change:** stream every allowlisted document, check decompression/CRC and size, and emit only hashes/lengths. No extraction. Original GDF and label-firewall checks remain intact.
- **Run:** `python -B -m unittest discover -s benchmarks/wireless-brain-interface -p test_bnci2a_source_archive_preflight.py -v`
- **30–90-second demonstration:** run the command and point to the three `test_corrupted_permitted_document_crc_rejected`, `test_document_bytes_are_hashed_without_text_disclosure`, and `test_empty_permitted_document_is_hashed` cases. This demonstrates only a synthetic integrity boundary.

## Verified execution and provenance

[GitHub Actions run #40474963906](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40474963906) **completed successfully** at tested commit `968ecf5792acb7e955ae32900cc2730ca4766ef6`. Both Ubuntu and Windows job logs were read. Each OS: **17/17** synthetic ZIP tests, **9/9** fictional split tests, plus frozen synthetic evaluator verification. Frozen evaluator source Git blob `2becec81a8002cc5ff2f445889b7617baf9937b9` and risk–coverage CSV SHA-256 `65695ce77a098e751778c3de5988fc3944bbc77ccaa53228ced858f46aaa8d5a` remain unchanged.

Source Git blob `9eebcf5a71daed20917219b406f15419a824cebe`; test Git blob `523fcac141ac4e195b0bf9ed2fbdb6eaddeb1b2a`. Hosted CPython 3.13 on GitHub Ubuntu and Windows runners; exact patch-level Python versions: **TBD** in this note. Independent local execution of the updated code: **not claimed**.

## Limitations and decision

ZIP CRC plus SHA-256 establishes member byte integrity **only**, not publisher authenticity, GDF validity, true EEG provenance, correct trial labels, data privacy, or model quality. Source URL remains a declared, unverified string. Documents are streamed but their content is not published. Real archive hash, source acquisition, loader version, event counts, risk–coverage metrics and external review: **TBD**.

**Decision:** retain Research / Simulation. **Next:** acquire the official publisher archive, independently authenticate its origin and license, run the integrity gate, derive actual label-free session metadata, then freeze the decoder before isolated held-out scoring. **Reframe:** do not present the synthetic archive gate as EEG validation or any kind of safety result.
