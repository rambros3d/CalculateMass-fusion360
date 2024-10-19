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

        # Get all components in the design
        root_comp = design.rootComponent
        all_bodies = root_comp.bRepBodies

        # Check if there are any bodies in the design
        if all_bodies.count == 0:
            ui.messageBox('No bodies in the active design')
            return

        # Define densities for the materials in kg/m³
        materials = {
            "Steel": 7800,
            "Aluminum": 2700,
            "ABS": 1020
        }

        # Initialize a dictionary to store total volume for each material
        total_volumes = {material: 0.0 for material in materials}

        # Loop through all bodies to accumulate volumes
        for body in all_bodies:
            # Get the physical properties of the body
            physical_properties = body.physicalProperties

            # Retrieve volume in cubic centimeters and convert to cubic meters (1 cm³ = 1e-6 m³)
            volume_m3 = physical_properties.volume * 1e-6

            # Accumulate volume for each material
            for material in materials:
                total_volumes[material] += volume_m3

        # Prepare the output message including the number of bodies
        output_message = f"Total Mass of all Bodies: {all_bodies.count}\n\n"

        # Calculate and display the total mass for each material
        for material, density in materials.items():
            # Calculate total mass in kilograms
            total_mass_kg = density * total_volumes[material]

            if is_metric:
                # Convert mass to grams
                total_mass_g = total_mass_kg * 1000  # 1 kg = 1000 grams
                # Append results in metric units
                output_message += (
                    f"{material}:\n\n"
                    f"  {total_mass_g:.8f} g\n\n"
                    f"  {total_mass_kg:.8f} kg\n\n\n"
                )
            else:
                # Convert mass to pounds and ounces
                total_mass_lb = total_mass_kg * 2.20462263  # 1 kg = 2.20462 pounds
                # Append results in imperial units
                output_message += (
                    f"{material}:\n"
                    f"  {total_mass_lb:.8f} lb\n\n"
                )

        # Display the results
        ui.messageBox(output_message.strip())

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    pass

