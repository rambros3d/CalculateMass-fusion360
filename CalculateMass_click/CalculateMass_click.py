 
# Rambrosteam - rambros3d.com
# 
# This script is licensed under the Public Domain. 
#
# File: CalculateMass.py
#
# This script was created to calculate the mass of a body
# in metric and imperial units automatically.
#
# The preset densities for the materials are:
# Steel: 7800 kg/m³
# Aluminum: 2700 kg/m³
# ABS: 1020 kg/m³
#
# This script was used in the 3DCAD esports TOURNAMENT
# https://youtu.be/5SBDwwzF7B0?t=4718

import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct

        # Check if a design is open
        if not isinstance(design, adsk.fusion.Design):
            ui.messageBox('No active Fusion 360 design')
            return

        # Get the unit system from the active design
        units_mgr = design.fusionUnitsManager
        default_units = units_mgr.defaultLengthUnits

        # Determine if the unit system is metric based on the default length unit
        is_metric = default_units in ['cm', 'mm', 'm']

        # Get the selection
        sel = ui.selectEntity('Select a body', 'Bodies')
        if not sel:
            ui.messageBox('No body selected')
            return

        body = sel.entity

        # Check if the selected entity is a body
        if not isinstance(body, adsk.fusion.BRepBody):
            ui.messageBox('Selected entity is not a body')
            return

        # Get the physical properties of the body
        physical_properties = body.physicalProperties

        # Retrieve volume in cubic centimeters and convert to cubic meters (1 cm³ = 1e-6 m³)
        volume_m3 = physical_properties.volume * 1e-6

        # Define densities for the materials in kg/m³
        materials = {
            "Steel": 7800,
            "Aluminum": 2700,
            "ABS": 1020
        }

        # Prepare the output message
        output_message = ""

        for material, density in materials.items():
            # Calculate mass in kilograms
            mass_kg = density * volume_m3

            if is_metric:
                # Convert mass to grams
                mass_g = mass_kg * 1000  # 1 kg = 1000 grams
                # Append results in metric units
                output_message += (
                    f"{material}:\n\n"
                    f"  {mass_g:.8f} g\n\n"
                    f"  {mass_kg:.8f} kg\n\n\n"
                )
            else:
                # Convert mass to pounds and ounces
                mass_lb = mass_kg * 2.20462263  # 1 kg = 2.20462 pounds
                mass_oz = mass_lb * 16  # 1 pound = 16 ounces
                # Append results in imperial units
                output_message += (
                    f"{material}:\n\n"
                    f"  {mass_lb:.8f} lb\n\n\n"
                )

        # Display the results
        ui.messageBox(output_message.strip())

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    pass

