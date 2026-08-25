# Converted from phase_6_ui.ipynb

# # Phase 6 — Interactive UI
# 
# Run this notebook to open a simple interactive fuzzy-controller UI with four sliders and an output command.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def build_controller():
    power = ctrl.Antecedent(np.arange(0, 101, 1), 'power')
    flow = ctrl.Antecedent(np.arange(0, 21, 1), 'flow')
    temp = ctrl.Antecedent(np.arange(20, 81, 1), 'temp')
    pressure = ctrl.Antecedent(np.arange(0, 101, 1), 'pressure')
    rate = ctrl.Consequent(np.arange(0, 10.01, 0.01), 'rate')
    
    for variable, terms in [
        (power, {'low': [0, 0, 50], 'medium': [25, 50, 75], 'high': [50, 100, 100]}),
        (flow, {'low': [0, 0, 10], 'medium': [5, 10, 15], 'high': [10, 20, 20]}),
        (pressure, {'low': [0, 0, 50], 'medium': [25, 50, 75], 'high': [50, 100, 100]}),
        (temp, {'low': [20, 20, 40], 'normal': [30, 50, 70], 'high': [60, 80, 80]}),
    ]:
        for label, points in terms.items():
            variable[label] = fuzz.trimf(variable.universe, points)
    for label, points in {'off': [0, 0, 2], 'low': [1, 3, 5], 'medium': [4, 6, 8], 'high': [7, 10, 10]}.items():
        rate[label] = fuzz.trimf(rate.universe, points)
    rules = [
        ctrl.Rule(power['high'] & flow['high'] & pressure['low'] & temp['normal'], rate['high']),
        ctrl.Rule(power['high'] & flow['low'] & pressure['low'] & temp['normal'], rate['medium']),
        ctrl.Rule(power['medium'] & flow['medium'] & pressure['low'] & temp['normal'], rate['medium']),
        ctrl.Rule(power['medium'] & flow['low'] & pressure['low'] & temp['normal'], rate['medium']),
        ctrl.Rule(power['low'] & flow['high'] & pressure['low'] & temp['normal'], rate['medium']),
        ctrl.Rule(power['low'] & flow['medium'] & pressure['low'] & temp['normal'], rate['low']),
        ctrl.Rule(power['low'] & flow['low'] & pressure['low'] & temp['normal'], rate['low']),
        ctrl.Rule(power['high'] & flow['high'] & pressure['medium'] & temp['normal'], rate['high']),
        ctrl.Rule(power['high'] & flow['medium'] & pressure['medium'] & temp['normal'], rate['medium']),
        ctrl.Rule(power['low'] & flow['low'] & pressure['high'] & temp['normal'], rate['off']),
        ctrl.Rule(power['medium'] & temp['high'], rate['low']),
    ]
    return ctrl.ControlSystem(rules)

controller = build_controller()

def evaluate(power, flow, temp, pressure):
    sim = ctrl.ControlSystemSimulation(controller)
    sim.input['power'] = power
    sim.input['flow'] = flow
    sim.input['temp'] = temp
    sim.input['pressure'] = pressure
    sim.compute()
    return float(sim.output['rate'])

import ipywidgets as widgets
from IPython.display import display, clear_output

power = widgets.FloatSlider(value=70, min=0, max=100, step=1, description='Power (kW)', continuous_update=False)
flow = widgets.FloatSlider(value=14, min=0, max=20, step=0.5, description='Water (L/min)', continuous_update=False)
temp = widgets.FloatSlider(value=50, min=20, max=80, step=1, description='Stack temp (°C)', continuous_update=False)
pressure = widgets.FloatSlider(value=35, min=0, max=100, step=1, description='Tank pressure (bar)', continuous_update=False)
button = widgets.Button(description='Run controller', button_style='success')
output = widgets.Output()

def run_ui(_=None):
    rate = evaluate(power.value, flow.value, temp.value, pressure.value)
    status = 'PROTECTION / VERIFY INTERLOCKS' if pressure.value >= 80 else ('DERATED — HIGH TEMPERATURE' if temp.value >= 70 else 'NORMAL FUZZY COMMAND')
    with output:
        clear_output(wait=True)
        print(f'Recommended production rate: {rate:.2f} kg/h')
        print(status)

button.on_click(run_ui)
display(widgets.VBox([widgets.HTML('<h2>Green Hydrogen Fuzzy Controller</h2>'), power, flow, temp, pressure, button, output]))
run_ui()
