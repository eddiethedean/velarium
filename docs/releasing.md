# Installing and releasing stubber

## Version number

The release version is defined in **one place**: `__version__` in [`stubber/__init__.py`](../stubber/__init__.py). [`pyproject.toml`](../pyproject.toml) uses Hatch dynamic metadata (`[tool.hatch.version]`) so `pip` and `importlib.metadata` stay aligned—do not duplicate the version string under `[project]`.

## Install from a Git checkout

```bash
pip install /path/to/stubber
# or
pip install git+https://github.com/eddiethedean/stubber.git@v0.1.0
```

Use a tag (e.g. `v0.1.0`) for reproducible installs.

## Build wheels locally

```bash
pip install build
python -m build
```

Artifacts appear under `dist/` (`*.whl` and `*.tar.gz`).

## Publish to PyPI

### Manual (API token)

1. Bump `__version__` in `stubber/__init__.py` and update [CHANGELOG.md](../CHANGELOG.md).
2. Tag: `git tag -a v0.1.0 -m "Release 0.1.0"` and `git push origin v0.1.0`.
3. `python -m build` then upload with [twine](https://twine.readthedocs.io/):

   ```bash
   pip install twine
   twine upload dist/*
   ```

### Automated (GitHub Actions)

The [Publish workflow](../.github/workflows/publish.yml) runs when a **GitHub Release** is **published**, building with `python -m build` and uploading via [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish).

1. Configure **trusted publishing** on [pypi.org](https://pypi.org) for this repository (see PyPI docs for “OIDC” / GitHub).
2. Add a GitHub **environment** named `pypi` if you use environment protection rules.
3. Create a release from the tag; publishing the release triggers the workflow.

If automated publish is not configured, use the manual steps above.
