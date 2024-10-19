
# Rambros Workshop - rambros3d.com
# 
# This script is licensed under the Public Domain
# Feel free to do whatever you want with it.
#
# This script was created to calculate
# the total mass of all bodies in the desgin
# in metric and imperial units automatically.
#
# The material densities are derived from the
# material properties of the respective bodies
# in the current design.
#
# This script was created right after winning the first place in:
# TooTallToby's 2024 World Championship Tournament
#
# This script makes the mass calculation easier for multibody designs.
# This could have been handy in the tournament.
#
# Created and sharing this for the TooTallToby fans
#                          &
# Fusion 360 champions of TooTallToby's Tournaments

import adsk.core, adsk.fusion, adsk.cam, traceback

def get_all_bodies(component):
    bodies = []
    for body in component.bRepBodies:
        if body.isSolid:
            bodies.append(body)
    for occurrence in component.occurrences:
        bodies.extend(get_all_bodies(occurrence.component))
    return bodies

def calculate_mass_of_body(body):
    props = body.physicalProperties
    return props.mass

def calculate_mass(total_mass_kg, is_metric):
    """Calculate and format total mass based on unit system."""
    
    output_message = ""
    if is_metric:
        total_mass_g = total_mass_kg * 1000  # Convert kg to grams
        output_message += (
            f"{total_mass_g:.6f} g\n\n"
            f"{total_mass_kg:.6f} kg\n\n"
        )
    else:
        total_mass_lb = total_mass_kg * 2.20462  # Convert kg to pounds
        output_message += (
            f"{total_mass_lb:.6f} lb\n\n"
        )

    return output_message

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        root_comp = design.rootComponent
        
        if not root_comp or (root_comp.bRepBodies.count == 0 and root_comp.occurrences.count == 0):
            ui.messageBox('No bodies or components in the active design.')
            return

        all_bodies = get_all_bodies(root_comp)
        num_solid_bodies = len(all_bodies)
        if num_solid_bodies == 0:
            ui.messageBox('No solid bodies in the active design.')
            return

        total_mass_kg = 0
        for body in all_bodies:
            total_mass_kg += calculate_mass_of_body(body)

        # Check the default length unit to determine if the system is metric
        units_mgr = design.fusionUnitsManager
        default_units = units_mgr.defaultLengthUnits
        is_metric = default_units in ['cm', 'mm', 'm']

        # Create the output message
        output_message = "RamBros3D\n"
        output_message += f"Total Mass of {num_solid_bodies} Solid Bodies:\n\n\n"
        output_message += calculate_mass(total_mass_kg, is_metric)
        output_message += "\nNote: Density is derived from the materials' properties."

        # Display the results
        ui.messageBox(output_message)

    except:
        # Print debug error if mass calculation fails
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



