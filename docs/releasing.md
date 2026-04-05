# Installing and releasing Velarium packages

The repo is a **[uv](https://docs.astral.sh/uv/) workspace** at the root. **Tier-1** publish targets are **`velarium`** (core IR) and **`velotype`** (stubs + CLI). Scaffold packages (**`viperis`**, **`morphra`**, **`granitus`**, **`velocus`**) are versioned in lockstep (e.g. **0.2.0**) and buildable; publish them to PyPI only when you want those names live (they remain minimal stubs).

## Version numbers

- **velarium:** `__version__` in [`packages/velarium/velarium/__init__.py`](../packages/velarium/velarium/__init__.py) (Hatch dynamic metadata in that package’s `pyproject.toml`).
- **velotype:** `__version__` in [`packages/velotype/velotype/__init__.py`](../packages/velotype/velotype/__init__.py).

Do not duplicate version strings under `[project]` in those `pyproject.toml` files.

Before tagging a release for **`velarium`** or **`velotype`**, run the full test suite (`pytest` with coverage) and `ty check` as in the root [README.md](../README.md#development). Any intentional **JSON IR** output change should update golden fixtures under `tests/fixtures/ir_golden/` and [CHANGELOG.md](../CHANGELOG.md).

### Ready for **0.2.0**?

Before publishing the **0.2.0** tag / GitHub Release, confirm:

| Check | Notes |
|-------|--------|
| Versions | Every package’s `__version__` is **`0.2.0`** (see each `packages/*/…/__init__.py`). **`velotype`** lists **`velarium>=0.2.0`** in [packages/velotype/pyproject.toml](../packages/velotype/pyproject.toml). |
| Changelog | [CHANGELOG.md](../CHANGELOG.md) has a **`[0.2.0]`** section with the correct date and `[Unreleased]` compare link pointing at **`v0.2.0...HEAD`**. |
| CI | [ci.yml](../.github/workflows/ci.yml) green on **`main`** (pytest, `ty`, wheel build for all packages). |
| Local build | `python -m build` in each `packages/*/`, or the merged `dist/` loop + `twine check dist/*` below. |
| Tag | Create **`v0.2.0`** on the commit that contains the version bump (annotated tag recommended). |
| PyPI order | If uploading manually, ensure **`velarium`** is available before **`velotype`** (dependency). |

Scaffold packages (**`viperis`**, **`morphra`**, **`granitus`**, **`velocus`**) are also **0.2.0** in-repo; only publish them to PyPI if you intend those names to update.

## Install from a Git checkout

```bash
git clone https://github.com/eddiethedean/velarium.git
cd velarium
uv sync --group dev
```

Or with **pip** (editable):

```bash
pip install -e packages/velarium -e "packages/velotype[dev]"
```

Tagged installs:

```bash
pip install git+https://github.com/eddiethedean/velarium.git@v0.2.0#subdirectory=packages/velotype
```

(Adjust tag and subdirectory for **`velarium`** or scaffold packages as needed.)

## Build wheels locally

From the repo root:

```bash
uv sync --group dev
for d in packages/*/; do (cd "$d" && uv run python -m build); done
```

Artifacts appear under each package’s `dist/` directory. To merge into a single **`dist/`** at the repo root (for **twine**):

```bash
rm -rf dist && mkdir -p dist
for pkg in velarium velotype viperis morphra granitus velocus; do
  (cd "packages/$pkg" && uv run python -m build --outdir "$PWD/../../dist")
done
uv run twine check dist/*
```

Configure credentials in the usual way for the CLI: **`~/.pypirc`**, **keyring**, or **`TWINE_USERNAME`** / **`TWINE_PASSWORD`** (see [twine authentication](https://twine.readthedocs.io/en/stable/#authentication)). If upload fails with **403** and a message that your user **isn’t allowed to upload to project `X`**, the name **`X`** is already taken on PyPI by another owner — pick a different [project name](https://pypi.org/help/#project-name) (e.g. rename the package in `pyproject.toml`).

Then upload:

```bash
uv run twine upload dist/*
```

Upload **`velarium`** before **`velotype`** if you step through uploads manually (so **`velotype`**’s `velarium>=0.2.0` resolves on PyPI). A single `twine upload dist/*` is fine once **`velarium`** is already published or all files upload in one batch.

### Manual release checklist

1. Bump `__version__` in the package(s) you release and update [CHANGELOG.md](../CHANGELOG.md).
2. Tag (e.g. `git tag -a v0.2.0 -m "Release 0.2.0"`) and `git push origin v0.2.0`.
3. Build and upload as above.

### Automated (GitHub Actions)

The [Publish workflow](../.github/workflows/publish.yml) runs when a **GitHub Release** is **published**. It builds **all workspace packages** into a single `dist/` folder and uploads via [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish). Publish **`velarium`** before **`velotype`** on PyPI if you upload manually (velotype depends on velarium).

1. Configure **trusted publishing** on [pypi.org](https://pypi.org) for this repository (OIDC / GitHub).
2. Add a GitHub **environment** named `pypi` if you use environment protection rules.
3. Create a release from the tag; publishing the release triggers the workflow.

Configure trusted publishers for each PyPI project you publish (**`velarium`**, **`velotype`**, and any scaffold package), or use one workflow job per package.

If automated publish is not configured, use the manual steps above.

The **Publish** workflow uploads **every** wheel and sdist in `dist/`. If you only intend to ship **`velarium`** and **`velotype`**, upload those artifacts only (or split the workflow) so scaffold packages are not published unintentionally.
