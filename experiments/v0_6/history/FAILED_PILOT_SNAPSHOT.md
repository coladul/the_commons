# v0.6 failed engineering pilot — immutable snapshot

The original failed pilot under `experiments/v0_6/pilot/` is retained as historical
evidence. Replacement-pilot preparation and execution must not write to that directory.

- Snapshot file count: `68`
- Directory aggregate SHA-256: `1386b24511a787e1f95571dc7f4a073bee7248b1a52a20e19aa00c40fdae93f8`
- Exact executed source copy: `experiments/v0_6/history/the_commons_v0_6_failed_pilot_executed.py`
- Executed source SHA-256: `1a4ea925d581a62984e6f8fde67bda4c7bea4c9f78d17d6d8fe17d0fe041d01e`

The directory aggregate is computed over all files below `experiments/v0_6/pilot/`
in sorted relative-path order. For each file, the aggregate receives the UTF-8 bytes
of `relative_posix_path`, the two-character delimiter `\0`, decimal byte size, the
same delimiter, the file's SHA-256, and the two-character terminator `\n`. The
resulting stream is SHA-256 hashed.

The failure occurred after each model response had returned and parsed as
`ChildRevision`: serialization encountered the `ChildRevision` class inside optional
SDK internals and invoked `BaseModel.model_dump()` as an unbound method. Because
essential and optional data were then assembled in one expression, the essential
parsed result was not committed before that optional serialization failure.
