
# Rambros Workshop - rambros3d.com
# 
# This script is licensed under the Public Domain
# Feel free to do whatever you want with it.
#
# This script was created to calculate
# the total mass of all bodies in the desgin
# in metric and imperial units automatically.
#
# The preset densities for the materials are:
# Steel: 7800 kg/m³
# Aluminum: 2700 kg/m³
# ABS: 1020 kg/m³
#
# This script was used in:
# TooTallToby's 2024 World Championship Tournament

import adsk.core, adsk.fusion, adsk.cam, traceback

def get_all_solid_bodies(component):
    bodies = []
    for body in component.bRepBodies:
        if body.isSolid:
            bodies.append(body)
    for occurrence in component.occurrences:
        bodies.extend(get_all_solid_bodies(occurrence.component))
    return bodies

def calculate_total_volume(bodies):
    total_volumes = {
        "Steel": 0.0,
        "Aluminum": 0.0,
        "ABS": 0.0
    }
    for body in bodies:
        physical_properties = body.physicalProperties
        volume_m3 = physical_properties.volume * 1e-6  # Convert from cm³ to m³
        for material in total_volumes:
            total_volumes[material] += volume_m3
    return total_volumes

def calculate_mass(total_volumes, is_metric):
    materials = {
        "Steel": 7800,
        "Aluminum": 2700,
        "ABS": 1020
    }
    output_message = ""
    for material, density in materials.items():
        total_mass_kg = density * total_volumes[material]
        if is_metric:
            total_mass_g = total_mass_kg * 1000  # Convert kg to grams
            output_message += (
                f"{material}:\n\n"
                f"  {total_mass_g:.4f} g\n\n"
                f"  {total_mass_kg:.4f} kg\n\n\n"
            )
        else:
            total_mass_lb = total_mass_kg * 2.20462263  # Convert kg to pounds
            output_message += (
                f"{material}:\n"
                f"  {total_mass_lb:.4f} lb\n\n"
            )
    return output_message

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct

        # Get the unit system from the active design
        units_mgr = design.fusionUnitsManager
        default_units = units_mgr.defaultLengthUnits
        is_metric = default_units in ['cm', 'mm', 'm']

        # Get root component
        root_comp = design.rootComponent

        # Check if there are any bodies or occurrences in the active design
        if not root_comp or (root_comp.bRepBodies.count == 0 and root_comp.occurrences.count == 0):
            ui.messageBox('No bodies or components in the active design.')
            return

        # Get all solid bodies in the design
        solid_bodies = get_all_solid_bodies(root_comp)

        # Check for solid bodies
        if len(solid_bodies) == 0:
            ui.messageBox('No solid bodies in the active design')
            return

        # Calculate total volumes for each material
        total_volumes = calculate_total_volume(solid_bodies)

        # Prepare output message
        output_message = "RamBros3D\n"
        output_message += f"Total Mass of {len(solid_bodies)} Solid Bodies:\n\n"

        # Calculate and display the total mass for each material
        output_message += calculate_mass(total_volumes, is_metric)

        # Display the results
        ui.messageBox(output_message.strip())

    except:
        # Print debug error if mass calculation fails
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
