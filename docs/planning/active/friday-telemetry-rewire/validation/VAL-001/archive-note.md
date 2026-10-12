# VAL-001 archival note

The independent reviewer's original report, evidence, probes, runners, and logs
are preserved byte-for-byte in `original-review-artifacts.tar.gz`;
`original-sha256.json` pins every original file. Readable report facts and
conclusions are unchanged. Probe/runner source copies are also lossless gzip evidence, rather than new
maintained repository Python modules. Its relative log/diff/probe links point to lossless gzip
copies here; source-line suffixes are rendered as adjacent line references so
repository link validation can resolve the underlying files. The original structured evidence keeps original artifact names,
which resolve when the original archive is extracted. Full tracked-file hash
snapshots and report-generation tooling are retained in the original archive.
The detached frozen review checkout remains at `/private/tmp/telem-01/review`.
