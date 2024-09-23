# CalculateMass.py

## Overview
`CalculateMass.py` is a Python script designed to calculate the mass of a selected body in Autodesk Fusion 360, providing results in both metric and imperial units. The script supports steel, aluminum, and ABS materials, with predefined densities, and was created for use used in the **3DCAD esports TOURNAMENT**.

### About the Tournament
Every year, TooTallToby and team host the **WORLD CHAMPIONSHIP OF 3D CAD SPEEDMODELING**.
The 2024 edition was a 16-person 1 vs 1 bracket-style tournament.

## Why this script was created?
Fusion 360's default properties tool is slow; it calculates multiple parameters like moment of inertia and center of mass.
This script focuses solely on mass, giving fast and accurate results.

## Preset Densities
- **Steel**: 7800 kg/m³
- **Aluminum**: 2700 kg/m³
- **ABS**: 1020 kg/m³

## Usage
1. Open a design in Autodesk Fusion 360.
2. Run the script.
3. Select a body to calculate its mass.
4. The mass will be calculated and displayed in either metric or imperial units, depending on the default units of the active design.

### Metric Results:
- Mass in grams (g)
- Mass in kilograms (kg)

### Imperial Results:
- Mass in pounds (lb)

## Requirements
- Autodesk Fusion 360
- Fusion 360 API (`adsk.core`, `adsk.fusion`)

## Installation
1. Download the script file `CalculateMass.py`.
2. Open Fusion 360 and navigate to **Scripts and Add-Ins**.
3. Add the script and run it from the **Scripts** menu.

## License
This script is licensed under the **Public Domain**.

## 3DCAD esports TOURNAMENT
This script was used in the [3DCAD esports TOURNAMENT](https://youtu.be/5SBDwwzF7B0?t=4718).