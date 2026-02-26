# Release Process (`gtaf-runtime`)

This document defines the minimal release procedure for `gtaf-runtime`.

## 1. Version Bump Policy

Use semantic versioning (`MAJOR.MINOR.PATCH`) for package releases.

- Patch (`x.y.Z`): bug fixes, packaging/docs/CI updates, and internal refactors that do not change runtime semantics.
- Minor (`x.Y.z`): additive, backward-compatible capabilities that do not break existing Projection contract behavior.
- Major (`X.y.z`): any breaking contract change, including evaluation-order changes, first-failure behavior changes, or reason-code semantic changes.

Before release:
- Update version in `pyproject.toml`.
- Ensure versioning/contract expectations remain aligned with `VERSIONING.md` and `docs/projection-v0.1.md`.

## 2. Tag Creation Policy

Release tags must follow `vX.Y.Z` and match `pyproject.toml` exactly.

Example:

```sh
git checkout main
git pull
git tag v0.1.1
git push origin v0.1.1
```

Notes:
- Create tags only from reviewed commits on `main`.
- Do not retag an existing released version.

## 3. Pre-Release Validation

Run the same checks enforced by CI:

```sh
python -m unittest discover -s tests -p "test_*.py" -v
python -m build
```

Packaging smoke test in a clean virtual environment:

```sh
python -m venv venv_test
source venv_test/bin/activate
python -m pip install --upgrade pip
python -m pip install dist/*.whl
python -c "import gtaf_runtime"
python -c "from gtaf_runtime import enforce"
deactivate
```

## 4. Build and Publish (PyPI)

Build artifacts:

```sh
python -m pip install --upgrade pip build twine
python -m build
```

Validate distribution metadata:

```sh
python -m twine check dist/*
```

Upload artifacts:

```sh
python -m twine upload dist/*
```

## 5. Changelog Expectation

Each release should include a changelog entry describing:
- version number and date,
- user-visible changes,
- compatibility/contract impact (if any),
- migration notes for breaking releases.

If no dedicated `CHANGELOG.md` exists yet, include release notes in the release PR description and/or GitHub release notes.

## 6. Future Hardening (Optional)

Trusted Publishing via GitHub Actions OIDC can replace token-based `twine upload` in a future hardening pass.
