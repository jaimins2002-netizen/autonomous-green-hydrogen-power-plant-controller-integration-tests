# Milestone 1 Input–Output Specification

The supplied Milestone 1 PDF defines a Mamdani fuzzy controller with **four inputs and one output**.

| Signal | Type | Range | Linguistic terms |
|---|---|---:|---|
| Renewable power | Input | 0–100 kW | Low, Medium, High |
| Water flow rate | Input | 0–20 L/min | Low, Medium, High |
| Stack temperature | Input | 20–80 °C | Low, Normal, High |
| Hydrogen-tank pressure | Input | 0–100 bar | Low, Medium, High |
| Hydrogen production rate | Output | 0–10 kg/h | Off, Low, Medium, High |

The Phase 3 core notebook uses the triangular membership points and 11 expert rules from the supplied specification. Phase 4 passes all four inputs into the controller for at least 10 combinations. Phase 5 analyses how the output changes with those four parameters. Phase 6 exposes the same four parameters as live controls and displays the resulting production command and fired rules.

The high-pressure input is safety-critical: the controller should reduce production as tank pressure approaches the high-pressure region. This project remains an educational simulation and is not a certified process-safety system.
