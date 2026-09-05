# FILE_CHANGE_MANIFEST — Final Engineering Pass

Scope: fix the confirmed path-traversal issue in evidence upload, add
regression coverage, add the root-level `.env.example`, and package the
final submission ZIP. No feature work, no UI redesign, no refactors of
already-working code beyond what the fix required.

## Changed

- **`backend/app/services/evidence/pipeline.py`**
  Added `safe_filename()` and `is_path_contained()`. `safe_filename()`
  neutralizes null bytes, normalizes `\` to `/`, takes only the final path
  component (`posixpath.basename`), strips characters outside a
  human-readable-but-safe allow-list, strips leading dots, and falls back
  to `"upload"` if nothing survives. `is_path_contained()` does an
  independent `os.path.realpath`-based containment check. Also widened the
  filename character allow-list after a test caught it over-mangling a
  benign filename containing parentheses (`Bank Statement (June 2026).pdf`).

- **`backend/app/api/routes_evidence.py`**
  `upload_evidence` now sanitizes `file.filename` via `safe_filename()`
  before it ever touches a path, and rejects the upload (`400`) if the
  resulting resolved path is not contained inside
  `settings.evidence_storage_dir`, via `is_path_contained()`. The sanitized
  name (`display_filename`) is now what's stored in the DB `filename`
  field and used in the audit-log summary, so the DB record matches what's
  actually on disk. No other upload behavior changed.

- **`docker-compose.yml`**
  Wired `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` / `DEMO_MODE`
  / `SEED` / `ANTHROPIC_API_KEY` / `VITE_API_BASE_URL` to read from the new
  root `.env.example`-documented variables (with the same defaults as
  before), instead of hardcoding `first_hour`/`first_hour` inline.

- **`frontend/Dockerfile`**
  Added `ARG VITE_API_BASE_URL` / `ENV VITE_API_BASE_URL` so the
  build-time override from `docker-compose.yml` actually reaches the Vite
  build. No change to the default behavior (empty → relative `/api`).

## Added

- **`backend/tests/test_evidence_filename_security.py`** — 13 unit tests
  for `safe_filename()` and `is_path_contained()`: Unix traversal, Windows
  traversal, absolute Unix path, absolute Windows path, null-byte trick,
  pure-traversal-with-no-basename, empty/None input, normal filenames
  preserved, unsafe special characters stripped, and direct
  containment-check true/false cases including the sibling-directory
  prefix-matching trap (`storage` vs `storage_evil`).

- **`backend/tests/test_evidence_upload_security_api.py`** — API-level
  regression tests hitting the real `/evidence/upload` endpoint (not just
  the sanitizer in isolation) with 5 parametrized malicious filenames
  (including the two named in the request: `../../../../etc/cron.d/evil`
  and `..\..\..\evil.txt`), asserting every file that actually lands on
  disk stays inside `EVIDENCE_STORAGE_DIR`, that nothing escapes to the
  parent directory, that a normal filename still uploads and round-trips
  correctly end-to-end, and that the API response's `filename` field is
  itself sanitized.

- **`.env.example`** (repo root) — Postgres/demo/API-key/frontend
  placeholders for `docker compose up`, with no real secrets, and a note
  distinguishing it from the per-service `.env.example` files.

- **`FILE_CHANGE_MANIFEST.md`** (this file)
- **`FINAL_PASS_FAIL_SCORECARD.md`**

## Explicitly not touched

Every backend service module, every frontend page/component, the seed
script, the data model, the state machine, the scoring/entity-
resolution/temporal-reasoning algorithms, the existing 59 tests from the
prior pass, and all three docs (`README.md`, `ARCHITECTURE.md`,
`DEMO_SCRIPT.md`) written in the previous pass — none of these needed to
change for this fix and none were refactored "while I was in there."
