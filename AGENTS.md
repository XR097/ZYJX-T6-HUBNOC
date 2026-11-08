# Repository Guidelines

## Project Structure & Module Organization

This repository is currently a specification package:

- `docs/HUB_NOC.pdf` defines HUB-DN, HUB-UP, HUB-ATT, and HUB-SYNC.
- `docs/HUB_RHUB.pdf` defines cross-core K-split reduction.
- `docs/SPEC_TRANSFER_PROTOCOL_V1.5.pdf` is authoritative for protocol A/B, VC, flit, and credit semantics.
- `docs/DATA_LAYOUT_V1.5.pdf` defines L2/L1/pod storage formats.
- `docs/hub_spec/` contains the M0-M4 trace, contracts, timing, open issues, and verification plan.

RTL, testbench, and scripts are not present yet. When implementation begins, use `rtl/`, `tb/` (or `dv/`), `scripts/`, and `build/` or `out/`. Keep specifications in `docs/`.

## Build, Test, and Development Commands

No simulator or build flow is checked in. Use these repository checks:

```text
rg --files
git status --short
git diff --check
```

When RTL is added, provide reproducible commands such as `make sim`, `make lint`, and `make synth`, including tool versions. Do not commit waveforms or simulator caches.

## Coding Style & Naming Conventions

Use SystemVerilog with four-space indentation, explicit widths, one declaration per line, and documented synchronous resets. Name modules and files in `snake_case` (`hub_dn.sv`, `hub_att.sv`); use `*_tb.sv` for testbenches and `*_pkg.sv` for packages. Preserve V1.5 field names such as `vld`, `last`, `nw8`, `vc`, and credit signals.

## Testing Guidelines

Add module tests for VC isolation, credit return, multicast completion, FIFO backpressure, barrier timeout, and fixed-order R-hub reduction. Name tests by behavior, for example `hub_dn_credit_stall_tb.sv`. Record simulator, seed, parameters, and results in the change description. Add coverage targets when the verification framework is selected.

## Commit & Pull Request Guidelines

Use concise imperative subjects with a scope, such as `docs: clarify HUB-UP write-port contract` or `rtl: add HUB-DN credit tracker`. Keep commits focused. Pull requests must describe affected spec sections, validation commands and results, and remaining `待审查`, `待仿真`, or `待标定` items.

## Architecture and Change Discipline

Treat `SPEC_TRANSFER_PROTOCOL_V1.5.pdf` as protocol authority and the HUB PDFs as module contracts. Do not silently change bandwidth, VC semantics, sideband widths, or ownership boundaries; update the relevant specification and this guide when a contract changes.
