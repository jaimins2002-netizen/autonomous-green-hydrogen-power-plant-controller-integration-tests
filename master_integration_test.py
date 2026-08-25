"""End-to-end integration checks for the Green Hydrogen Controller milestones.

Milestone 1 supplies the I/O contract, Milestone 2 supplies the core fuzzy
controller, and Milestone 3 supplies the testing/UI controller entry points.
The source modules are loaded by extracting only imports, controller builders,
and evaluate functions so notebook/demo side effects do not run during tests.
"""
from __future__ import annotations

import ast
import importlib.util
import math
from pathlib import Path
from types import ModuleType
from typing import Callable

ROOT = Path(__file__).resolve().parent
MILESTONE_1 = ROOT / "dependencies/milestone-1"
MILESTONE_2 = ROOT / "dependencies/milestone-2"
MILESTONE_3 = ROOT / "dependencies/milestone-3"

INPUT_RANGES = {
    "power": (0.0, 100.0),
    "flow": (0.0, 20.0),
    "temp": (20.0, 80.0),
    "pressure": (0.0, 100.0),
}

NOMINAL_CASE = {"power": 70.0, "flow": 14.0, "temp": 50.0, "pressure": 35.0}
HIGH_PRESSURE_CASE = {"power": 15.0, "flow": 3.0, "temp": 50.0, "pressure": 85.0}


def _load_controller_functions(source_path: Path) -> tuple[Callable[..., float], ModuleType]:
    """Load build_controller/evaluate without executing demo/UI code."""
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    selected: list[ast.stmt] = []
    has_direct_evaluate = any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'evaluate' for node in tree.body)
    has_run_controller = any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'run_controller' for node in tree.body)
    cutoff_line = min((node.lineno for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'sample_reading' for target in node.targets)), default=10**9)
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names]
            module_name = node.module if isinstance(node, ast.ImportFrom) else ""
            if not module_name.startswith(("ipywidgets", "IPython")) and not any(name.startswith(("ipywidgets", "IPython")) for name in names):
                selected.append(node)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in {"build_controller", "evaluate", "memberships_for", "min_strength", "run_controller"}:
            selected.append(node)
        elif isinstance(node, ast.Assign):
            targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
            if "controller" in targets or (has_run_controller and node.lineno < cutoff_line):
                selected.append(node)
    module_ast = ast.Module(body=selected, type_ignores=[])
    ast.fix_missing_locations(module_ast)
    module = ModuleType(source_path.stem)
    module.__file__ = str(source_path)
    exec(compile(module_ast, str(source_path), "exec"), module.__dict__)
    if has_direct_evaluate:
        return module.__dict__["evaluate"], module
    if has_run_controller:
        def evaluate(power: float, flow: float, temp: float, pressure: float) -> float:
            reading = {
                "renewable_power": power,
                "water_flow": flow,
                "stack_temperature": temp,
                "tank_pressure": pressure,
            }
            _, result = module.__dict__["run_controller"](reading, "centroid", show_output=False)
            return float(result)
        return evaluate, module
    raise KeyError(f"No supported controller entry point found in {source_path}")


def load_milestone2_controller() -> Callable[..., float]:
    path = MILESTONE_2 / "python/Autonomous_Green_Hydrogen_Plant_Controller_Fuzzy.py"
    evaluate, _ = _load_controller_functions(path)
    return evaluate


def load_milestone3_testing_controller() -> Callable[..., float]:
    path = MILESTONE_3 / "python/Phase_4_Testing/phase_4_testing.py"
    evaluate, _ = _load_controller_functions(path)
    return evaluate


def load_milestone3_ui_controller() -> Callable[..., float]:
    path = MILESTONE_3 / "python/Phase_6_UI/phase_6_ui.py"
    evaluate, _ = _load_controller_functions(path)
    return evaluate


def read_milestone1_contract() -> str:
    return (MILESTONE_1 / "docs/Milestone_1_IO_Specification.md").read_text(encoding="utf-8")


def evaluate_end_to_end(case: dict[str, float]) -> dict[str, float]:
    """Pass one contract-valid case through the Milestone 2 and 3 entry points."""
    args = (case["power"], case["flow"], case["temp"], case["pressure"])
    return {
        "milestone_2": load_milestone2_controller()(*args),
        "milestone_3_testing": load_milestone3_testing_controller()(*args),
        "milestone_3_ui": load_milestone3_ui_controller()(*args),
    }


def assert_contract_case(case: dict[str, float]) -> None:
    for field, (lower, upper) in INPUT_RANGES.items():
        value = float(case[field])
        if not lower <= value <= upper:
            raise AssertionError(f"{field}={value} is outside Milestone 1 range [{lower}, {upper}]")


def assert_valid_output(value: float) -> None:
    if not math.isfinite(float(value)) or not 0.0 <= float(value) <= 10.0:
        raise AssertionError(f"Controller output {value!r} is outside the specified 0–10 kg/h range")
