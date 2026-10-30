# Zhou2020 v0.8 — original-NPZ source acquisition and provenance bridge (protocol only)

**2026-10-30. Stage:** WBI Research / Simulation, unchanged. **Execution status:** source locations and publisher-listed archive checksums inspected; **no original NPZ/ZIP bytes downloaded, authenticated, decoded or compared** in this protocol. This is a source-acquisition plan, not EEG validation or a completed provenance bridge.

## Decision-changing primary-source discovery

The [Zenodo v1 record (2026-03-12)](https://zenodo.org/records/18988317), DOI `10.5281/zenodo.18988317`, identifies a **repackaging** of the IEEE DataPort Zhou2020 release (DOI `10.21227/f1c7-7x89`) into 20 per-subject ZIP archives totaling approximately 17.6 GB. It describes `S01.zip/session_1/run_01.npz` with `signal`, `MarkOnSignal` and `SampleRate` keys. The archive names are **not** the corrected NEMAR BIDS event/channel filenames. The Zenodo page provides MD5 values for the *repackaged ZIP containers*, not verified SHA-256 hashes for the original NPZ members. An MD5 match can detect many accidental transfer errors but does not prove original-source authenticity or equality with the IEEE deposit.

This is a concrete acquisition path for the outstanding original-signal gate. The corrected [NEMAR v1.1.0 Git ref](https://github.com/nemarDatasets/nm000237/tree/a291ed8a2afab3f93b85a540134dceb98092fcaf) remains the **separate**, Git-blob-pinned BIDS metadata source used in v0.3–v0.7. The [NEMAR README](https://github.com/nemarDatasets/nm000237/blob/main/README.md) says `sourcedata/` was unchanged by the October 14 channel-label correction; that statement is not a verified byte-level equivalence between Zenodo and BIDS. The [EEGDash listing](https://eegdash.org/api/dataset/eegdash.dataset.NM000237.html) reports 833 BIDS recordings and 16.0 GB, a different packaging/measurement context. **Do not equate ZIP member count, BIDS recording count, structural event rows or trial counts without a demonstrated mapping.**

## Frozen publisher-listed ZIP manifest (not independently downloaded)

Source: Zenodo record `18988317`, version `v1`, inspected 2026-10-30. Values below are the publisher's **MD5** checksums of ZIP containers, not SHA-256 of NPZ members.

| Subject ZIP | Zenodo MD5 |
|---|---|
| S01.zip | `34867b4b27a8c91fd6fe010cbf4f9caa` |
| S02.zip | `47c316f0c69378f1a98706f15f19a474` |
| S03.zip | `7e313b97b6b33cb1823d788d6d1ae264` |
| S04.zip | `f5f00cc57235d6ce414b5d732e066cdb` |
| S05.zip | `d0333d431e398de9c71413793666d9c7` |
| S06.zip | `c4c16b839b64e8085923469cac8de2aa` |
| S07.zip | `a4e55473a2c867c48c975476f39b670d` |
| S08.zip | `66c9b2a9c5e097901e038aaffeaa7b22` |
| S09.zip | `c90a989545a5bdc5167c46cfc1afd234` |
| S10.zip | `ab751b523db0b9a19d9a3dff7e54c806` |
| S11.zip | `8bee7bd7e49ea5e8c804faf9c5641af9` |
| S12.zip | `5af97a8013556e9198256350ab6a018d` |
| S13.zip | `ef2e519a94e142b8e5c152bd5a66d849` |
| S14.zip | `529cebd554af45c6d2fc11990e0c8413` |
| S15.zip | `b47bc7938da8fabc752eb2423efa3b53` |
| S16.zip | `e6a703e9798bd1150b87d63a0bf44cb5` |
| S17.zip | `8d23b84736b85bc253f543f5994d3923` |
| S18.zip | `0d5a4f60513a60a64f1c7c0efa7f9acd` |
| S19.zip | `75f1eeb46a4ae4332934edb8c891a3fb` |
| S20.zip | `6751e946234790f16673c9066cbd46b0` |

The Zenodo description maps original S1–S12 to S01–S12 and original A1–A8 to S13–S20. **This is a publisher-described identity map, not an independently verified session/run correspondence.** The ZIP listing describes 40 trials per run nominally, which must not override the observed 833 corrected event TSVs / 33,534 structural rows.

## Next experiment — single-subject byte-and-mapping gate, before outcomes

1. Pin Zenodo record version and download **only S01.zip** through its official record; record retrieval timestamp, URL, HTTP size, local tool versions, complete ZIP SHA-256 and MD5. Reject mismatched publisher MD5, truncation, unreadable ZIP central directory, duplicate paths, absolute paths, traversal, symlinks, encrypted members or excessive uncompressed sizes. Do **not** execute or unpickle archive contents.
2. Enumerate member paths without extraction; independently compute SHA-256 for each selected NPZ member and record compressed/uncompressed sizes. Validate NPZ as a ZIP container with an explicit allowlist of expected array names; use `numpy.load(..., allow_pickle=False)` only in an isolated resource-bounded environment. Do not publish signal arrays, participant data or labels.
3. Predeclare an exact source `S01/session_1/run_01.npz` ↔ corrected NEMAR `sub-1/ses-0/run-0` **hypothesis only**, then **test rather than assume** whether indexing is one-based/zero-based, whether all run counts align, and whether source MarkOnSignal and corrected BIDS events share the same sample-time semantics. Compare channel count/types against corrected v1.1.0 provenance; independently verify acquisition order if dates exist.
4. Preserve a private byte-level manifest and a public **aggregate-only** PASS/FAIL report with explicit mismatch reasons and hashes. Freeze protocol before looking at any new held-out outcomes. If no trustworthy mapping can be established, **stop** and reframe to metadata-only structural work.

**Acceptance:** exact publisher ZIP checksum; independently measured NPZ member hashes; reproducible path-to-recording mapping with explicit indexing/units and a documented mismatch policy; independent review of the frozen train/calibration/test outcome boundary. **Current status: ALL TBD.** No new synthetic evaluator result, clinical claim, novel method, external review, stage advancement, release, merge, or human-subject access.

**Four lenses:** hiring manager — reproducible provenance before claims; technical reviewer — separates repackaged ZIP integrity, original NPZ members, corrected BIDS metadata and label-blind evaluation; innovation leader — identifies a source-identity confound without novelty claims; founder — no validated efficacy, users or deployment. No employer material, private correspondence or outreach tracking.
