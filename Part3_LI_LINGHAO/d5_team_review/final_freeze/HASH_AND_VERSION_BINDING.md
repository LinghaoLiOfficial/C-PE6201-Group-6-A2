# D5 release hash and prompt-version binding audit

Audit date: 2026-09-18

## Hash semantics

The frozen runner defines `package_sha256` as the SHA-256 digest of the immutable
`package_manifest.json` bytes. It does not mean the SHA-256 digest of the ZIP
container. ZIP metadata and compression headers can change when a package is
transported or re-packed, so a container hash is not the release binding used by
the runner.

For all six formal batteries, the following checks passed:

1. External `release.json` `package_sha256` equals the SHA-256 of the submitted
   package's `package_manifest.json`.
2. The ZIP's embedded `suite/release.json` has the same package hash.
3. The external and embedded `preflight_sha256` values equal the SHA-256 of the
   corresponding `suite/preflight.json` / retained preflight file.
4. The suite assignment and package manifest are byte-identical to the submitted
   package metadata.

Therefore no raw release receipt or trial evidence is rewritten. The apparent
ZIP-hash mismatch was a comparison against the wrong object and is resolved by
recording the runner's binding semantics here.

## ZHOU_SIHAN prompt version

ZHOU_SIHAN is the assigned DeepSeek paired **v1** run. `assignment.json`,
`suite/metadata.json`, every trial record, the preflight assignment, and
`OBSERVATIONS.md` all identify `prompt_version: v1`; the contract revision remains
`d5-live-1.1`. The other members' assigned runs use v2. This is an intentional
paired model/version allocation and is preserved in the final comparison. No
trial was rerun or edited to force v2.
