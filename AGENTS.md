# Repository Guidelines

## Project Structure & Module Organization

This repository is currently a specification package:

- `docs/specs/` contains the current V1.8 (November 11, 2026) Markdown specifications and referenced SVG figures. `*_STAGING.md` files are design inputs, not contracts.
- `docs/specs/ONCHIP_DATAPATH_ARCH.md` is the authority for port counts, widths, and directions; `DATA_TRANSFER_PROTOCOL.md` defines address, ready, and write-acknowledgment semantics.
- `docs/specs/HUB_NOC.md` defines the L2-side H2C/C2H links and control fabric; `HUB_IDN.md` defines the NI-side 32-byte multicast distributor.
- `docs/specs/MAE_CRU.md` defines L2-to-L2 reduction within MAE, replacing the retired standalone RHUB architecture.
- `docs/hub_spec/` contains derived requirements, contracts, timing, interfaces, and verification plans; `docs/reviews/` contains current conclusions and open issues.
- Historical versions are available through Git, not duplicate baseline directories. Record source conflicts in the current issue ledger rather than silently resolving them in derived contracts.

RTL and testbenches are not present yet. Figure-generation and document-checking utilities live in `docs/specs/_build/`. When RTL implementation begins, use `rtl/`, `tb/` (or `dv/`), `scripts/`, and `build/` or `out/`. Keep specifications in `docs/`.

## Build, Test, and Development Commands

No simulator or build flow is checked in. Use these repository checks:

```text
rg --files
git status --short
git diff --check
```

When RTL is added, provide reproducible commands such as `make sim`, `make lint`, and `make synth`, including tool versions. Do not commit waveforms or simulator caches.

## Coding Style & Naming Conventions

Use SystemVerilog with four-space indentation, explicit widths, one declaration per line, and documented synchronous resets. Name modules and files in `snake_case` (`hub_noc.sv`, `hub_idn.sv`); use `*_tb.sv` for testbenches and `*_pkg.sv` for packages. Preserve current field names such as `en`, `din`, `be`, `addr`, `seg`, `src`, and `ready`; distinguish read-return `vld` from write-acknowledgment `valid`. Do not reintroduce retired VC, credit, flit, `last`, or `nw8` interfaces.

## Testing Guidelines

Add module tests for multicast delivery, full-throughput back-to-back transfers, FIFO/skid backpressure, write-acknowledgment attribution, reset, and fixed-order MAE_CRU reduction. C2H acknowledgment is an untagged valid pulse; H2C and IDN acknowledgments carry `src`. Barrier scheduling belongs to LIC. Name tests by behavior, for example `hub_idn_backpressure_tb.sv`. Record simulator, seed, parameters, and results in the change description. Add coverage targets when the verification framework is selected; do not add hardware error checks beyond the source specifications.

## Commit & Pull Request Guidelines

Use concise imperative subjects with a scope, such as `docs: clarify HUB-UP write-port contract` or `rtl: add HUB-DN credit tracker`. Keep commits focused. Pull requests must describe affected spec sections, validation commands and results, and remaining `待审查`, `待仿真`, or `待标定` items.

## Architecture and Change Discipline

Treat the current `docs/specs/` Markdown as the V1.8 source baseline and `docs/hub_spec/` as derived analysis. Follow the architecture port table, protocol rules, and module contracts together; record inconsistencies in `docs/reviews/open_issues_current.md`. Do not silently change bandwidth, handshake semantics, sideband widths, or ownership boundaries. HUB only transports data/control, forks multicast, and returns acknowledgments; MAE_ENG/CCU count completion, MAE_CRU performs reduction through L2, and LIC schedules dependencies.
