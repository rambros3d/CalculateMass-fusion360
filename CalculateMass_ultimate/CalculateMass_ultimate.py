
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

import adsk.core, adsk.fusion, traceback
import platform
import subprocess

APP_NAME = 'Calculate Mass Ultimate'
CMD_ID = 'RamBros_CalculateMassUltimateCmd'
CMD_NAME = 'Calculate Mass Ultimate'
CMD_DESCRIPTION = 'Calculate mass for selected or all solid bodies.'
WORKSPACE_ID = 'FusionSolidEnvironment'
ICON_FOLDER = ''
PANEL_IDS_TO_ADD = ['SolidInspectPanel']

handlers = []
command_state = {"copy_map": {}}

def log_lifecycle(app, action):
    try:
        app.log(f'{APP_NAME}: {action}')
    except Exception:
        pass

def get_target_panel(ui):
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    if not workspace:
        return None, None

    panel = workspace.toolbarPanels.itemById('SolidInspectPanel')
    if panel:
        return workspace, panel

    for candidate in workspace.toolbarPanels:
        name = (candidate.name or '').lower()
        panel_id = (candidate.id or '').lower()
        if 'inspect' in name or 'inspect' in panel_id:
            return workspace, candidate

    return workspace, None

def get_candidate_panels(workspace):
    panels = []
    if not workspace:
        return panels

    # 1) Explicit known IDs first.
    for panel_id in PANEL_IDS_TO_ADD:
        panel = workspace.toolbarPanels.itemById(panel_id)
        if panel and panel not in panels:
            panels.append(panel)

    # 2) Dynamic match for localized/variant Inspect panel naming.
    for panel in workspace.toolbarPanels:
        name = (panel.name or '').lower()
        panel_id = (panel.id or '').lower()
        if 'inspect' in name or 'inspect' in panel_id:
            if panel not in panels:
                panels.append(panel)

    return panels

def get_all_solid_bodies(component):
    """Retrieve all solid bodies from the component."""
    solid_bodies = []
    for body in component.bRepBodies:
        if body.isSolid:
            solid_bodies.append(body)
    for occurrence in component.occurrences:
        solid_bodies.extend(get_all_solid_bodies(occurrence.component))
    return solid_bodies

def is_metric_document(design):
    units_mgr = design.fusionUnitsManager
    default_units = units_mgr.defaultLengthUnits
    return default_units in ['cm', 'mm', 'm']

def format_display_mass(mass_kg, is_metric):
    if is_metric:
        return f"{mass_kg * 1000.0:.6f}", 'g'
    return f"{mass_kg * 2.20462263:.6f}", 'lbs'

def sanitize_id(text):
    safe = ''.join(ch if ch.isalnum() else '_' for ch in text)
    return safe.strip('_') or 'item'

def copy_to_clipboard(text):
    system = platform.system()
    if system == 'Darwin':
        subprocess.run(['pbcopy'], input=text.encode('utf-8'), check=True)
        return
    if system == 'Windows':
        subprocess.run(['cmd', '/c', 'clip'], input=text.encode('utf-16le'), check=True)
        return
    subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)

def collect_target_bodies(ui, root_comp):
    selected_entities = ui.activeSelections
    if selected_entities.count == 0:
        all_bodies = get_all_solid_bodies(root_comp)
        return all_bodies, f'All bodies ({len(all_bodies)})'

    selected_bodies = []
    for entity in selected_entities:
        if isinstance(entity.entity, adsk.fusion.BRepBody) and entity.entity.isSolid:
            if entity.entity not in selected_bodies:
                selected_bodies.append(entity.entity)
        elif isinstance(entity.entity, adsk.fusion.Component):
            component_solid_bodies = get_all_solid_bodies(entity.entity)
            for body in component_solid_bodies:
                if body not in selected_bodies:
                    selected_bodies.append(body)
        elif isinstance(entity.entity, adsk.fusion.BRepFace):
            parent_body = entity.entity.body
            if parent_body.isSolid and parent_body not in selected_bodies:
                selected_bodies.append(parent_body)

    return selected_bodies, f'Selected bodies ({len(selected_bodies)})'

def build_mass_report_data(bodies):
    preset_volumes = {"Steel": 0.0, "6061 Aluminum": 0.0, "ABS": 0.0, "American Cherry": 0.0}
    preset_densities = {"Steel": 7800, "6061 Aluminum": 2700, "ABS": 1020, "American Cherry": 570}
    actual_material_totals = {}
    total_mass_kg = 0.0

    for body in bodies:
        props = body.physicalProperties
        volume_m3 = props.volume * 1e-6
        for material in preset_volumes:
            preset_volumes[material] += volume_m3

        material_name = body.material.name if body.material else "Unknown Material"
        body_mass_kg = props.mass
        total_mass_kg += body_mass_kg
        actual_material_totals[material_name] = actual_material_totals.get(material_name, 0.0) + body_mass_kg

    preset_totals = {name: preset_densities[name] * preset_volumes[name] for name in preset_volumes}
    return preset_totals, actual_material_totals, total_mass_kg

def add_copyable_total_row(inputs, total_mass_kg, is_metric):
    mass_number, mass_unit = format_display_mass(total_mass_kg, is_metric)
    table = inputs.addTableCommandInput('total_table', '', 2, '4:1')
    table.hasGrid = False

    total_text = inputs.addTextBoxCommandInput(
        'total_txt',
        '',
        f'Total: {mass_number} {mass_unit}',
        1,
        True
    )
    button_id = 'copy_total'
    copy_btn = inputs.addBoolValueInput(button_id, 'Copy', False, '', False)
    command_state["copy_map"][button_id] = mass_number
    table.addCommandInput(total_text, 0, 0)
    table.addCommandInput(copy_btn, 0, 1)

def add_copyable_mass_rows(inputs, title, mass_map, prefix, is_metric):
    inputs.addTextBoxCommandInput(
        f'{prefix}_title',
        '',
        f'<b>{title}</b>',
        1,
        True
    )

    table = inputs.addTableCommandInput(f'{prefix}_table', '', 2, '4:1')
    table.hasGrid = False

    row_index = 0
    for material, mass_kg in mass_map.items():
        mass_number, mass_unit = format_display_mass(mass_kg, is_metric)
        material_id = sanitize_id(material)
        material_text = inputs.addTextBoxCommandInput(
            f'{prefix}_txt_{material_id}',
            '',
            f'<b>{material}</b>: {mass_number} {mass_unit}',
            1,
            True
        )
        button_id = f'copy_{prefix}_{material_id}'
        copy_btn = inputs.addBoolValueInput(button_id, 'Copy', False, '', False)
        command_state["copy_map"][button_id] = mass_number
        table.addCommandInput(material_text, row_index, 0)
        table.addCommandInput(copy_btn, row_index, 1)
        row_index += 1

class MassCommandExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        pass

class MassInputChangedHandler(adsk.core.InputChangedEventHandler):
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            changed_input = adsk.core.InputChangedEventArgs.cast(args).input
            copy_text = command_state["copy_map"].get(changed_input.id)
            if not copy_text:
                return

            copy_to_clipboard(copy_text)
        except Exception:
            ui = adsk.core.Application.get().userInterface
            if ui:
                ui.messageBox('Copy failed:\n{}'.format(traceback.format_exc()))

class MassCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        ui = None
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            cmd = args.command
            if hasattr(cmd, 'setDialogInitialSize'):
                cmd.setDialogInitialSize(520, 520)
            if hasattr(cmd, 'isOKButtonVisible'):
                cmd.isOKButtonVisible = False
            if hasattr(cmd, 'cancelButtonText'):
                cmd.cancelButtonText = 'Dismiss'

            on_execute = MassCommandExecuteHandler()
            cmd.execute.add(on_execute)
            handlers.append(on_execute)

            on_input_changed = MassInputChangedHandler()
            cmd.inputChanged.add(on_input_changed)
            handlers.append(on_input_changed)

            design = app.activeProduct
            root_comp = design.rootComponent
            if not root_comp or (root_comp.bRepBodies.count == 0 and root_comp.occurrences.count == 0):
                ui.messageBox('No bodies or components in the active design.')
                return

            bodies, scope_label = collect_target_bodies(ui, root_comp)
            if len(bodies) == 0:
                ui.messageBox('No valid solid bodies found.')
                return

            preset_totals, actual_totals, total_mass_kg = build_mass_report_data(bodies)
            is_metric = is_metric_document(design)

            command_state["copy_map"] = {}
            inputs = cmd.commandInputs
            inputs.addTextBoxCommandInput('scope', '', f'Scope: {scope_label}', 1, True)
            add_copyable_total_row(inputs, total_mass_kg, is_metric)

            add_copyable_mass_rows(inputs, 'Preset Density Estimate', preset_totals, 'preset', is_metric)
            add_copyable_mass_rows(inputs, 'Actual Totals By Material', actual_totals, 'actual', is_metric)

        except Exception:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        log_lifecycle(app, 'loaded')

        existing_def = ui.commandDefinitions.itemById(CMD_ID)
        if existing_def:
            existing_def.deleteMe()

        cmd_def = ui.commandDefinitions.addButtonDefinition(
            CMD_ID,
            CMD_NAME,
            CMD_DESCRIPTION,
            ICON_FOLDER
        )

        on_created = MassCommandCreatedHandler()
        cmd_def.commandCreated.add(on_created)
        handlers.append(on_created)

        workspace, panel = get_target_panel(ui)
        if not workspace:
            raise RuntimeError(f'Workspace not found: {WORKSPACE_ID}')
        if not panel:
            raise RuntimeError('Inspect toolbar panel not found in target workspace.')

        created_panels = []
        for target_panel in get_candidate_panels(workspace):
            control = target_panel.controls.itemById(CMD_ID)
            if not control:
                control = target_panel.controls.addCommand(cmd_def)
                # Promote in standard panels so it behaves like a normal command.
                control.isPromotedByDefault = True
                control.isPromoted = True
                created_panels.append(target_panel.id)
            else:
                created_panels.append(target_panel.id)

        if not created_panels:
            raise RuntimeError('Could not add command to an Inspect toolbar panel.')

        # Keep the module alive if Fusion runs this through a script-like lifecycle.
        adsk.autoTerminate(False)

    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        log_lifecycle(app, 'unloaded')

        workspace, panel = get_target_panel(ui)
        if workspace:
            for target_panel in get_candidate_panels(workspace):
                control = target_panel.controls.itemById(CMD_ID)
                if control:
                    control.deleteMe()
            if panel:
                control = panel.controls.itemById(CMD_ID)
                if control:
                    control.deleteMe()

        cmd_def = ui.commandDefinitions.itemById(CMD_ID)
        if cmd_def:
            cmd_def.deleteMe()
    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
