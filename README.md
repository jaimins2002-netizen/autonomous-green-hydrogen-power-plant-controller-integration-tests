# Autonomous Green Hydrogen Controller — Master Integration Tests

This repository verifies the end-to-end communication path between the three project milestones:

1. **Milestone 1** provides the controller input–output contract and operating ranges.
2. **Milestone 2** provides the core Mamdani fuzzy controller.
3. **Milestone 3** provides testing and UI controller entry points that must remain behaviorally compatible with Milestone 2.

## What Is Tested

The master test suite validates that contract-valid plant inputs can travel through the Milestone 2 controller, the Milestone 3 testing controller, and the Milestone 3 UI controller. It checks that all entry points return finite hydrogen-production commands in the specified `0–10 kg/h` range, agree on nominal behavior, and reduce or maintain output under the high-pressure protection case.

It also verifies that the Milestone 1 I/O specification and the required Milestone 2 and Milestone 3 controller artifacts are present.

## Repository Layout

| Path | Purpose |
|---|---|
| `master_integration_test.py` | Shared loader, contract definitions, and end-to-end evaluation helpers. |
| `tests/test_master_integration.py` | Pytest integration coverage. |
| `dependencies/milestone-1/` | Vendored Milestone 1 I/O specification and source PDF. |
| `dependencies/milestone-2/` | Vendored Milestone 2 controller implementation used by the tests. |
| `dependencies/milestone-3/` | Vendored Milestone 3 testing and UI controller entry points. |
| `.github/workflows/ci.yml` | Automated integration CI on Python 3.11 and 3.12. |

The dependency snapshots are intentionally vendored so the integration test is reproducible and does not require GitHub credentials or network access to sibling repositories during CI.

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

The test suite loads only the controller builders and `evaluate` functions from the milestone source files. Plotting, notebook display, and interactive UI side effects are not executed during automated tests.

## Related Repositories

- [Milestone 1](https://github.com/jaimins2002-netizen/autonomous-green-hydrogen-power-plant-controller-milestone-1)
- [Milestone 2](https://github.com/jaimins2002-netizen/autonomous-green-hydrogen-power-plant-controller-milestone-2)
- [Milestone 3](https://github.com/jaimins2002-netizen/autonomous-green-hydrogen-power-plant-controller-milestone-3)
- [Project website](https://jaimins2002-netizen.github.io/)

## Safety Disclaimer

This repository contains educational simulation tests. It is **not** a certified process-safety system and must not be used to control real hydrogen-production equipment without qualified engineering validation, independent hardware safeguards, regulatory review, and professional oversight.

## License

No license has been specified for this repository.
