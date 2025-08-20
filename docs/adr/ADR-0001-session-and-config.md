# ADR-0001: Session Context and Config Caching

Decision: Introduce `src/core/session.py` providing a context manager `Session` that starts an MPh/COMSOL session with bounded retries and clear diagnostics. Add content-hash based caching to `src/core/config/loader.py` using merged YAML content plus environment-sensitive keys.

Status: Accepted (non-breaking, additive).

## Rationale

- COMSOL is unavailable in CI; we need a clear, robust local-only session boundary with actionable errors and retry.
- Config reads occur multiple times; caching by file path is brittle. Hashing the merged content plus env keys avoids stale reads.

## Consequences

- No behavior changes by default; existing CLI remains intact.
- Tests can mock the `mph` module to validate session behavior without COMSOL.

