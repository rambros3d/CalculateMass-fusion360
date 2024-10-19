
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
# This script makes the mass calculation easier for any design.
# This could have been handy in the tournament.
#
# Created and sharing this for the TooTallToby fans
#                          &
# Fusion 360 champions of TooTallToby's Tournaments

import adsk.core, adsk.fusion, adsk.cam, traceback

def get_all_solid_bodies(component):
    """Retrieve all solid bodies from the component."""
    solid_bodies = []
    for body in component.bRepBodies:
        if body.isSolid:
            solid_bodies.append(body)
    for occurrence in component.occurrences:
        solid_bodies.extend(get_all_solid_bodies(occurrence.component))
    return solid_bodies

def calculate_mass_of_body(body):
    """Calculate the mass of a body using its physical properties."""
    return body.physicalProperties.mass

def calculate_mass_with_preset_densities(bodies, is_metric):
    """Calculate total mass of bodies using preset material densities."""
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

    output_message = ""
    materials = {
        "Steel": 7800,
        "Aluminum": 2700,
        "ABS": 1020
    }

    for material, density in materials.items():
        total_mass_kg = density * total_volumes[material]
        if is_metric:
            total_mass_g = total_mass_kg * 1000  # Convert kg to grams
            output_message += (
                f"{material}:\n"
                f"  {total_mass_g:.4f} g\n"
                f"  {total_mass_kg:.4f} kg\n\n"
            )
        else:
            total_mass_lb = total_mass_kg * 2.20462  # Convert kg to pounds
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
        root_comp = design.rootComponent

        if not root_comp or (root_comp.bRepBodies.count == 0 and root_comp.occurrences.count == 0):
            ui.messageBox('No bodies or components in the active design.')
            return

        # Get all solid bodies in the active design
        solid_bodies = get_all_solid_bodies(root_comp)
        num_solid_bodies = len(solid_bodies)

        if num_solid_bodies == 0:
            ui.messageBox('No solid bodies in the active design.')
            return

        # Determine the unit system
        units_mgr = design.fusionUnitsManager
        default_units = units_mgr.defaultLengthUnits
        is_metric = default_units in ['cm', 'mm', 'm']

        output_message = f"RamBros 3D: Mass Calculate\n"

        # If there is only one solid body, calculate its mass
        if num_solid_bodies == 1:
            body = solid_bodies[0]
            output_message += f"Mass of the SELECTED body:\n\n"
            output_message += calculate_mass_with_preset_densities([body], is_metric)
            ui.messageBox(output_message)
            return

        # If multiple bodies, check if a body, component, or face is selected
        selected_entity = ui.activeSelections[0].entity if ui.activeSelections.count > 0 else None

        if selected_entity:
            if isinstance(selected_entity, adsk.fusion.BRepBody) and selected_entity.isSolid:
                output_message += f"Mass of the SELECTED body:\n\n"
                output_message += calculate_mass_with_preset_densities([selected_entity], is_metric)
                ui.messageBox(output_message)
                return
            elif isinstance(selected_entity, adsk.fusion.Component):
                # If a component is selected, get its solid bodies
                component_solid_bodies = get_all_solid_bodies(selected_entity)
                if component_solid_bodies:
                    output_message += f"Mass of the SELECTED component:\n\n"
                    output_message += calculate_mass_with_preset_densities(component_solid_bodies, is_metric)
                    ui.messageBox(output_message)
                    return
            elif isinstance(selected_entity, adsk.fusion.BRepFace):
                # If a face is selected, get the parent body and calculate its mass
                parent_body = selected_entity.body
                if parent_body.isSolid:
                    output_message += f"Mass of the SELECTED body (face):\n\n"
                    output_message += calculate_mass_with_preset_densities([parent_body], is_metric)
                    ui.messageBox(output_message)
                    return

        # If no body or component selected, calculate total mass of all bodies
        output_message += "Total Mass of All Bodies:\n\n"
        output_message += calculate_mass_with_preset_densities(solid_bodies, is_metric)

        # If multiple bodies with different material densities, calculate from material properties
        if num_solid_bodies > 1:
            densities = {body.material.name: body.physicalProperties.density for body in solid_bodies}
            unique_densities = set(densities.values())
            if len(unique_densities) > 1:
                total_mass_kg = sum(calculate_mass_of_body(body) for body in solid_bodies)
                output_message += f"\nTotal Mass from Material Properties:\n\n"
                output_message += f"{total_mass_kg:.4f} kg\n"

        # Display the results
        ui.messageBox(output_message.strip())

    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    pass



