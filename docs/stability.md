# Stability policy (pre-1.0)

This document applies from **Phase 0.8** onward (monorepo **0.8.0**+), aligned with [What “1.0.0” means](ROADMAP.md#what-100-means) in the roadmap.

## Semver during 0.x

Until **1.0.0**:

- **Minor** releases (**0.y.0**) may add public API, extend JSON IR in **additive** ways, and introduce **deprecation warnings** for symbols or behaviors we intend to remove or change before 1.0.
- **Patch** releases (**0.y.z**) are for fixes and documentation; they should not remove or break documented public behavior without a prior deprecation in an earlier minor (see [deprecations](#deprecations)).

We do **not** treat every 0.x minor as a free-for-all breaking change: tier‑1 packages (**velarium**, **velotype**) aim for predictable upgrades—prefer **additive** changes and **deprecation paths** until **1.0.0**.

## Public API surface

The **supported** import paths for semantic versioning are:

- **`velarium`** — symbols listed in `velarium.__all__` (see [api-reference.md](api-reference.md)).
- **`velotype`** — symbols listed in `velotype.__all__`, plus the **`velotype`** CLI and `python -m velotype`.

Submodules (`velarium.json_codec`, `velarium.normalize`, `velotype.stubgen`, …) are **stable for advanced use** where documented, but **new code should prefer** top-level imports from `velarium` / `velotype` when those re-exports exist. Batch and watch workflows also expose **`velotype.batch`** helpers (`emit_batch_stubs`, `emit_batch_ir`, and related utilities) used by the CLI; treat them as library entry points for automation.

## IR JSON (`format_version`)

ModelSpec JSON carries a top-level integer **`format_version`** (see [modelspec-ir.md](modelspec-ir.md), [migration-ir.md](migration-ir.md)). **`velarium`** rejects unknown **future** format versions until support is added. Older files **without** `format_version` load as **version 1**.

## Deprecations

Anything removed or intentionally changed before **1.0.0** should ship with a **`DeprecationWarning`** (and changelog + API reference note) in an **earlier** minor when feasible.

**As of 0.8.0**, no pre-1.0 deprecations are active; future deprecations will be listed in [CHANGELOG.md](../CHANGELOG.md) and in [api-reference.md](api-reference.md).

## After 1.0.0

Normal [Semantic Versioning](https://semver.org/spec/v2.0.0.html): **1.y.0** minors add features; **1.0.z** patches fix bugs; **2.0.0** is reserved for intentional breaking API or incompatible IR revisions with a migration path.
