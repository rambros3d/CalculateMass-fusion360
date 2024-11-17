
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
# Future fusion 360 champions of TooTallToby's Tournaments

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
        "ABS": 0.0,
        "Red Oak": 0.0  # Added new material
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
        "ABS": 1020,
        "Red Oak": 570  # Added new material
    }

    for material, density in materials.items():
        total_mass_kg = density * total_volumes[material]
        if is_metric:
            total_mass_g = total_mass_kg * 1000  # Convert kg to grams
            output_message += (
                f"{material}:\n\n"
                f"  {total_mass_g:.6f} g\n\n"
                f"  {total_mass_kg:.6f} kg\n\n"
            )
        else:
            total_mass_lb = total_mass_kg * 2.20462  # Convert kg to pounds
            output_message += (
                f"{material}:\n\n"
                f"  {total_mass_lb:.6f} lb\n\n"
            )
    return output_message

def display_mass_with_material_properties(bodies, is_metric):
    """Display the mass of each body with its name and actual material."""
    output_message = "Mass using actual material properties:\n\n"
    for body in bodies:
        body_name = body.name if body.name else "Unnamed Body"
        material_name = body.material.name if body.material else "Unknown Material"
        mass_kg = calculate_mass_of_body(body)
        if is_metric:
            mass_g = mass_kg * 1000  # Convert kg to grams
            output_message += f"{body_name} - {material_name}\n{mass_g:.6f} g \n{mass_kg:.6f} kg\n\n"
        else:
            mass_lb = mass_kg * 2.20462  # Convert kg to pounds
            output_message += f"{body_name} - {material_name}\n{mass_lb:.6f} lb\n\n"
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

        output_message = f"RamBros 3D: TTT Mass Calculate\n"

        # If no body or component selected, calculate total mass of all bodies
        selected_entities = ui.activeSelections

        # Handle case when one or more bodies are selected
        if selected_entities.count > 0:
            selected_bodies = []
            total_mass_kg = 0.0  # Initialize total mass
            
            for entity in selected_entities:
                if isinstance(entity.entity, adsk.fusion.BRepBody) and entity.entity.isSolid:
                    if entity.entity not in selected_bodies:
                        selected_bodies.append(entity.entity)
                        total_mass_kg += calculate_mass_of_body(entity.entity)  # Add body mass
                elif isinstance(entity.entity, adsk.fusion.Component):
                    component_solid_bodies = get_all_solid_bodies(entity.entity)
                    for body in component_solid_bodies:
                        if body not in selected_bodies:
                            selected_bodies.append(body)
                            total_mass_kg += calculate_mass_of_body(body)  # Add component body mass
                elif isinstance(entity.entity, adsk.fusion.BRepFace):
                    parent_body = entity.entity.body
                    if parent_body.isSolid and parent_body not in selected_bodies:
                        selected_bodies.append(parent_body)
                        total_mass_kg += calculate_mass_of_body(parent_body)  # Add face body mass

            # If multiple bodies are selected
            if len(selected_bodies) > 0:
                output_message += "Mass of the SELECTED bodies:\n\n"
                output_message += calculate_mass_with_preset_densities(selected_bodies, is_metric)
                output_message += "\n" + display_mass_with_material_properties(selected_bodies, is_metric)
                
                # Display the total mass of the selected bodies
                if is_metric:
                    output_message += f"\nTotal Mass of Selected Bodies:\n\n{total_mass_kg * 1000:.6f} g\n\n{total_mass_kg:.6f} kg"
                else:
                    output_message += f"\nTotal Mass of Selected Bodies:\n\n{total_mass_kg * 2.20462:.6f} lb"
                ui.messageBox(output_message)
                return
            else:
                ui.messageBox('Selected bodies are invalid or not solid.')

        # If no specific selection, calculate total mass of all bodies in the design
        else:
            output_message += "Total Mass of All Bodies:\n\n"
            output_message += calculate_mass_with_preset_densities(solid_bodies, is_metric)
            output_message += "\n" + display_mass_with_material_properties(solid_bodies, is_metric)

            # If multiple bodies with different material densities, calculate from material properties
            if num_solid_bodies > 1:
                densities = {body.material.name: body.physicalProperties.density for body in solid_bodies}
                unique_densities = set(densities.values())
                if len(unique_densities) > 1:
                    total_mass_kg = sum(calculate_mass_of_body(body) for body in solid_bodies)
                    if is_metric:
                        output_message += f"\nTotal Mass from Material Properties:\n\n"
                        output_message += f"{total_mass_kg * 1000:.6f} g\n\n"  # Convert to grams
                        output_message += f"{total_mass_kg:.6f} kg"
                    else:
                        output_message += f"\nTotal Mass from Material Properties:\n\n"
                        output_message += f"{total_mass_kg * 2.20462:.6f} lb"  # Convert to pounds

            ui.messageBox(output_message.strip())

    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    pass
