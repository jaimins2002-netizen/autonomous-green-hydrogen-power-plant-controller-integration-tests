from pathlib import Path

import pytest

from master_integration_test import (
    HIGH_PRESSURE_CASE,
    INPUT_RANGES,
    MILESTONE_1,
    MILESTONE_2,
    MILESTONE_3,
    NOMINAL_CASE,
    assert_contract_case,
    assert_valid_output,
    evaluate_end_to_end,
    read_milestone1_contract,
)


@pytest.mark.parametrize(
    "case",
    [
        NOMINAL_CASE,
        {"power": 5.0, "flow": 2.0, "temp": 50.0, "pressure": 20.0},
        {"power": 85.0, "flow": 18.0, "temp": 50.0, "pressure": 25.0},
        HIGH_PRESSURE_CASE,
        {"power": 60.0, "flow": 10.0, "temp": 75.0, "pressure": 35.0},
    ],
)
def test_end_to_end_cases_produce_valid_outputs(case):
    assert_contract_case(case)
    outputs = evaluate_end_to_end(case)
    assert set(outputs) == {"milestone_2", "milestone_3_testing", "milestone_3_ui"}
    for value in outputs.values():
        assert_valid_output(value)


def test_all_controller_entry_points_agree_on_nominal_case():
    outputs = evaluate_end_to_end(NOMINAL_CASE)
    values = list(outputs.values())
    assert max(values) - min(values) < 1e-9, outputs


def test_all_controller_entry_points_agree_on_high_pressure_protection():
    nominal = evaluate_end_to_end(NOMINAL_CASE)
    high_pressure = evaluate_end_to_end(HIGH_PRESSURE_CASE)
    for name in nominal:
        assert high_pressure[name] <= nominal[name], (name, nominal, high_pressure)


def test_milestone_1_contract_is_present_and_mentions_all_signals():
    contract = read_milestone1_contract().lower()
    for phrase in ("renewable power", "water flow rate", "stack temperature", "hydrogen-tank pressure", "hydrogen production rate"):
        assert phrase in contract
    assert "four inputs and one output" in contract


def test_milestone_ranges_are_complete_and_ordered():
    assert set(INPUT_RANGES) == {"power", "flow", "temp", "pressure"}
    for lower, upper in INPUT_RANGES.values():
        assert lower < upper


def test_milestone_artifacts_are_available():
    assert (MILESTONE_1 / "docs/Milestone_1_Source_Specification.pdf").is_file()
    assert (MILESTONE_2 / "python/Autonomous_Green_Hydrogen_Plant_Controller_Fuzzy.py").is_file()
    assert (MILESTONE_3 / "python/Phase_4_Testing/phase_4_testing.py").is_file()
    assert (MILESTONE_3 / "python/Phase_6_UI/phase_6_ui.py").is_file()
