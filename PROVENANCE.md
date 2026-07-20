# Provenance

First public implementation: July 2026.

The repository contains an original rectangle packer, defect collision checks, shared scoring, a step-by-step environment, synthetic fixtures, and regression tests. Defect polygons currently use axis-aligned bounding boxes; that approximation is stated in the README and tested as part of the current contract.

The research idea carried into this project is that heterogeneous material should be an input to allocation rather than something cleaned away first. No SCI-Arc source code or media is used. The public project and contributor credits are recorded in [ATTRIBUTION.md](ATTRIBUTION.md).

The hand-authored layout is a fixture, not empirical evidence. The two automated players are inspectable heuristics, not a novel nesting solver and not AI agents.
