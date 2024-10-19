
# Rambros Workshop - rambros3d.com
# 
# This script is licensed under the Public Domain
# Feel free to do whatever you want with it.
#
# This script was created to calculate
# the mass of the selected body
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

def get_unit_system(design):
    """Determine if the unit system is metric."""
    units_mgr = design.fusionUnitsManager
    default_units = units_mgr.defaultLengthUnits
    return default_units in ['cm', 'mm', 'm']

def select_body(ui):
    """Prompt the user to select a body and return it."""
    sel = ui.selectEntity('Select a body', 'Bodies')
    if not sel:
        ui.messageBox('No body selected')
        return None
    return sel.entity

def validate_body(body, ui):
    """Check if the selected entity is a body."""
    if not isinstance(body, adsk.fusion.BRepBody):
        ui.messageBox('Selected entity is not a body')
        return False
    return True

def is_solid_body(body, ui):
    """Check if the selected body is solid."""
    if not body.isSolid:
        ui.messageBox('The selected entity is not a solid body')
        return False
    return True

def get_all_bodies(component):
    """Get all bodies in the component."""
    bodies = []
    for body in component.bRepBodies:
        bodies.append(body)
    for occurrence in component.occurrences:
        bodies.extend(get_all_bodies(occurrence.component))
    return bodies

def get_all_solid_bodies(component):
    """Get all solid bodies in the component."""
    solid_bodies = []
    for body in component.bRepBodies:
        if body.isSolid:
            solid_bodies.append(body)
    for occurrence in component.occurrences:
        solid_bodies.extend(get_all_solid_bodies(occurrence.component))
    return solid_bodies

def calculate_mass(volume_m3, materials, is_metric):
    """Calculate and format mass for each material based on volume."""
    output_message = ""
    for material, density in materials.items():
        mass_kg = density * volume_m3
        if is_metric:
            mass_g = mass_kg * 1000  # Convert kg to grams
            output_message += (
                f"{material}:\n\n"
                f"  {mass_g:.6f} g\n\n"
                f"  {mass_kg:.6f} kg\n\n\n"
            )
        else:
            mass_lb = mass_kg * 2.20462263  # Convert kg to pounds
            output_message += (
                f"{material}:\n\n"
                f"  {mass_lb:.6f} lb\n\n\n"
            )
    return output_message

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        
        # Determine the unit system
        is_metric = get_unit_system(design)

        # Get all bodies in the root component
        root_comp = design.rootComponent
        all_bodies = get_all_bodies(root_comp)
        solid_bodies = get_all_solid_bodies(root_comp)

        # Check if there are any bodies at all
        if not all_bodies:
            ui.messageBox('No bodies in the active design.')
            return

        # Check if there are any solid bodies
        if not solid_bodies:
            ui.messageBox('No solid bodies in the active design.')
            return

        # If there is only one solid body, calculate mass without user selection
        if len(solid_bodies) == 1:
            body = solid_bodies[0]
        else:
            # Select a body if there is more than one solid body
            body = select_body(ui)
            if body is None:
                return

            # Validate the selected body
            if not validate_body(body, ui):
                return

            # Check if the selected body is solid
            if not is_solid_body(body, ui):
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

        # Calculate and display the mass for each material
        output_message = "RamBros3D\n\n"
        output_message += calculate_mass(volume_m3, materials, is_metric)

        # Display the results
        ui.messageBox(output_message.strip())

    except:
        # Print debug error if mass calculation fails
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    pass




