import traceback
import os
import re

from CallbacksExt import CallbacksExt

from AcroVersionExt import AcroVersionExt

from TDStoreTools import StorageManager
from ThemeCSSParser import ThemeCSSParser
TDF = op.TDModules.mod.TDFunctions


# TUIK2 color sections with headers (used for parameter creation and CSS parsing)
TUIK2_SECTIONS = {
    'Button': [
        'button_border_disable', 'button_bordera', 'button_borderb', 'button_disable',
        'button_off', 'button_offroll', 'button_on', 'button_onroll',
        'buttontext_disable', 'buttontext_off', 'buttontext_offroll', 'buttontext_on', 'buttontext_onroll',
    ],
    'Checkbox': [
        'checkbox_border', 'checkbox_border_disable',
    ],
    'Field': [
        'field_disable', 'field_on', 'field_onroll',
    ],
    'Gadget': [
        'gadget_bg', 'gadget_bordera', 'gadget_borderb',
    ],
    'Header': [
        'header_bg', 'header_bordera',
    ],
    'Indicator': [
        'indicator_disable', 'indicator_off', 'indicator_roll',
    ],
    'Knob': [
        'knob_disable', 'knob_off', 'knob_roll',
        'knobindicator_disable', 'knobindicator_off', 'knobindicator_roll',
    ],
    'Label': [
        'label_text', 'label_text_disable',
    ],
    'Operator': [
        'operator_CHOP', 'operator_CHOPfilter', 'operator_CHOPgenerator',
        'operator_COMP', 'operator_COMPfilter', 'operator_COMPgenerator', 'operator_COMPvoid',
        'operator_DAT', 'operator_DATfilter', 'operator_DATgenerator',
        'operator_MAT', 'operator_MATfilter', 'operator_MATgenerator',
        'operator_SOP', 'operator_SOPfilter', 'operator_SOPgenerator',
        'operator_TOP', 'operator_TOPfilter', 'operator_TOPgenerator',
    ],
    'Slider': [
        'slider_bg_disable', 'slider_bg_on', 'slider_bg_onroll', 'slider_range_off',
    ],
    'Template': [
        'template_bordera', 'template_borderb', 'template_off', 'template_offroll',
        'template_on', 'template_onroll',
    ],
    'Titlebar': [
        'titlebar_bordera', 'titlebar_off', 'titlebar_on', 'titlebar_text_off',
    ],
    'Other': [
        'root_time', 'transparent',
    ],
}

# Flat list of all TUIK2 color names (for iteration)
TUIK2_COLORS = [color for colors in TUIK2_SECTIONS.values() for color in colors]

# Path to TUIK2 color component for reading defaults
TUIK2_COLOR_COMP = '/ui/lib/TUIK2/colors/color'


def _tuik2_par_name(color_name):
    """Convert TUIK2 color name to parameter name

    Args:
        color_name: e.g., 'button_off'

    Returns:
        str: Parameter name, e.g., 'Buttonoff'
    """
    # Remove underscores and capitalize first letter only
    name = color_name.replace('_', '').lower()
    return name[0].upper() + name[1:]


class AcroThemeManager(CallbacksExt, AcroVersionExt):

    """ Theme manager for TouchDesigner ui.colors using CSS-based theme files """

    def __init__(self, ownerComp):
        # the component to which this extension is attached
        self.ownerComp = ownerComp

        # CSS parser for theme files
        self._cssParser = ThemeCSSParser()

        # Store previous colors for diffing
        self._previousColors = {}
        self._previousTUIK2Colors = {}
        self._previousOpColors = {}

        # init callbacks
        self.callbackDat = self.ownerComp.par.Callbackdat.eval()
        try:
            CallbacksExt.__init__(self, ownerComp)
        except:
            self.ownerComp.addScriptError(traceback.format_exc() + \
                    "Error in CallbacksExt __init__. See textport.")
            debug("Error initializing callbacks - " + self.ownerComp.path)
            debug(traceback.format_exc())
        # run onInit callback
        try:
            self.DoCallback('onInit', {'ownerComp':self.ownerComp})
        except:
            self.ownerComp.addScriptError(traceback.format_exc() + \
                    "Error in custom onInit callback. See textport.")
            debug(traceback.format_exc())


        # Initialize version tracking mixin (creates Version + Component param pages)
        AcroVersionExt.__init__(self, ownerComp)

        # the component to which data is stored
        self.dataComp = ownerComp.op('data')

        # stored items (persistent across saves and re-initialization):
        storedItems = [
            {'name': 'Data', 'default': None, 'readOnly': False,
                                     'property': True, 'dependable': True},
        ]
        self.stored = StorageManager(self, self.dataComp, storedItems)

        # Ensure TUIK2 parameter page exists
        self._ensureTUIK2Page()

        # Ensure TouchColors parameter page exists
        self._ensureTouchColorsParams()

        # Auto-load theme on init if file exists
        # if self.ThemeDAT and self.ThemeDAT.text:
        #     self.OnThemeChange(self.ThemeDAT)

    # -------------------------------------------------------------------------
    # TUIK2 Parameter Setup
    # -------------------------------------------------------------------------

    def _ensureTUIK2Page(self):
        """Create TUIK2 color parameters if they don't exist"""
        # Check if page already exists and needs rebuilding
        page = None
        needs_rebuild = False
        for p in self.ownerComp.customPages:
            if p.name == 'TUIK2':
                page = p
                # Check if first param is a header (proper structure)
                # If not, we need to rebuild
                first_header = f'Tuik2{list(TUIK2_SECTIONS.keys())[0].lower()}header'
                if not hasattr(self.ownerComp.par, first_header):
                    needs_rebuild = True
                break

        # Destroy and recreate if needs rebuild
        if page and needs_rebuild:
            page.destroy()
            page = None

        if not page:
            page = self.ownerComp.appendCustomPage('TUIK2')

        # Reference to TUIK2 color comp for reading defaults
        color_comp = op(TUIK2_COLOR_COMP)

        # Create parameters for each section with headers
        for section_name, color_names in TUIK2_SECTIONS.items():
            # Add section header if it doesn't exist
            # Parameter names must be uppercase first letter then lowercase only
            header_name = f'Tuik2{section_name.lower()}header'
            if not hasattr(self.ownerComp.par, header_name):
                page.appendHeader(header_name, label=section_name)

            # Create color parameters for this section
            for color_name in color_names:
                par_name = _tuik2_par_name(color_name)

                # Check if parameter already exists
                if not hasattr(self.ownerComp.par, par_name + 'r'):
                    # Get default values from TUIK2 color comp
                    r, g, b, a = 0.5, 0.5, 0.5, 1.0
                    if color_comp:
                        color_top = color_comp.op(color_name)
                        if color_top:
                            r = color_top.par.colorr.eval()
                            g = color_top.par.colorg.eval()
                            b = color_top.par.colorb.eval()
                            a = color_top.par.alpha.eval() if hasattr(color_top.par, 'alpha') else 1.0

                    # Create RGBA parameter (creates 4 float parameters: name + r/g/b/a)
                    pars = page.appendRGBA(par_name, label=color_name)
                    # Set defaults from TUIK2 color comp
                    for p in pars:
                        if p.name.endswith('r'):
                            p.default = r
                            p.val = r
                        elif p.name.endswith('g'):
                            p.default = g
                            p.val = g
                        elif p.name.endswith('b'):
                            p.default = b
                            p.val = b
                        elif p.name.endswith('a'):
                            p.default = a
                            p.val = a

    def _ensureTouchColorsParams(self):
        """Create TouchColors parameters if they don't exist"""
        page = None
        for p in self.ownerComp.customPages:
            if p.name == 'TouchColors':
                page = p
                break

        if not page:
            page = self.ownerComp.appendCustomPage('TouchColors')

        if not hasattr(self.ownerComp.par, 'Writetouchcolors'):
            pars = page.appendToggle(
                'Writetouchcolors', label='Write TouchColors On Load')
            for p in pars:
                p.default = False
                p.val = False

        if not hasattr(self.ownerComp.par, 'Updatetouchcolors'):
            page.appendPulse(
                'Updatetouchcolors', label='Update TouchColors Now')

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def ThemeDAT(self):
        """Reference to the theme TextDAT"""
        return self.ownerComp.op('theme')

    # -------------------------------------------------------------------------
    # Theme Management
    # -------------------------------------------------------------------------
    def onStart(self):
        self.cloneColor()

        if self.ownerComp.par.Fixuionstart.eval():
            self.fixBookmarkButtons()
            self.fixTimeAttributes()
            self.fixTimelineHashrow()
            self.fixTransport()
            self.fixRangebar()
            self.fixFPS()

        if self.ownerComp.par.Loadonstart.eval():
            self.Refresh()

    def cloneColor(self):
        op('/ui/lib/TUIK2/colors/color').par.clone = self.ownerComp.op('color')

    def fixBookmarkButtons(self):
        bookmark_bar = op('/ui/dialogs/bookmark_bar')
        if bookmark_bar:
            for i in range(1,6):
                layout = bookmark_bar.op(f'layout{i}')
                if layout:
                    cell_default = layout.op('cell_default')
                    cell_default.destroy()
                    cell_default = layout.create(selectDAT, 'cell_default')
                    cell_default.python = True
                    cell_default.par.dat.expr = 'op.ATM.op("bookmark/new_cell_default")'
                    
                    table_default = layout.op('table_default')
                    table_default.destroy()
                    table_default = layout.create(selectDAT, 'table_default')
                    table_default.python = True
                    table_default.par.dat.expr = 'op.ATM.op("bookmark/new_table_default")'

                    table_select = layout.op('table_select')
                    table_select.destroy()
                    table_select = layout.create(selectDAT, 'table_select')
                    table_select.python = True
                    table_select.par.dat.expr = 'op.ATM.op("bookmark/new_table_select")'

            layouts = bookmark_bar.op('layouts')
            layout_master = layouts.op('layoutmaster0')
            pane_layout = layout_master.op('panelayout')
            pane_layout.par.vmode = 'fill'
            layout_master.op('label').par.vmode = 'fill'
            cell_default = pane_layout.op('cell_default')
            cell_default.destroy()
            cell_default = pane_layout.create(selectDAT, 'cell_default')
            cell_default.python = True
            cell_default.par.dat.expr = 'op.ATM.op("bookmark/new_cell_default")'

            table_default = pane_layout.op('table_default')
            table_default.destroy()
            table_default = pane_layout.create(selectDAT, 'table_default')
            table_default.python = True
            table_default.par.dat.expr = 'op.ATM.op("bookmark/new_table_default")'

            table_select = pane_layout.op('table_select')
            table_select.destroy()
            table_select = pane_layout.create(selectDAT, 'table_select')
            table_select.python = True
            table_select.par.dat.expr = 'op.ATM.op("bookmark/new_table_select")'

            layouts.op('replicator1').par.recreateall.pulse()

    def fixTimeAttributes(self):
        timeline = op('/ui/dialogs/timeline')
        time_attributes = timeline.op('timeattributes')
        time_attributes.par.bgalpha.reset()
        #time_attributes.op('parentoverride').export = False
        time_attributes.op('color')['gadget_bg', 1] = 'button_border_disable'
        time_attributes.op('parentoverride').par.dat = '/ThemeManager/timeline/parentoverride'

        #timeline.op('emptypanel1/parentoverride').export = False

        time_properties = timeline.op('timeproperties')
        #time_properties.python = True
        time_properties.par.vmode = 'fill'
        #time_properties.par.w = 264

        #set PROPWIDTH
        timeline.op('local/set_variables')['PROPWIDTH', 1] = 266

        attrib_comps = [
            'clip_s',
            'clip_e',
            'range_s',
            'range_e',
            'rate',
            'signature0',
            'signature1',
            'tempo',
            'resetf'
        ]

        for a_comp_name in attrib_comps:
            a_comp = time_attributes.op(a_comp_name)
            if a_comp:
                a_comp.op('color1').destroy()
                new_color = a_comp.create(selectDAT, 'color1')
                new_color.python = True
                new_color.par.dat.expr = 'op.ATM.op("timeline/ta_color")'
                new_color.outputConnectors[0].connect(a_comp.op('color').inputConnectors[0])

    def fixTimelineHashrow(self):
        timeline = op('/ui/dialogs/timeline')
        if timeline:
            newhashrow = timeline.op('newhashrow')
            defaulthash = newhashrow.op('defaulthash')
            defaulthash.destroy()
            defaulthash = newhashrow.create(selectDAT, 'defaulthash')
            defaulthash.python = True
            defaulthash.par.dat.expr = 'op.ATM.op("timeline/hashmarks")'

            defaulthash = newhashrow.op('newhashrow2/defaulthash')
            defaulthash.destroy()
            defaulthash = newhashrow.op('newhashrow2').create(selectDAT, 'defaulthash')
            defaulthash.python = True
            defaulthash.par.dat.expr = 'op.ATM.op("timeline/newhashrow2")'

            defaulthash = newhashrow.op('newhashrow3/defaulthash')
            defaulthash.destroy()
            defaulthash = newhashrow.op('newhashrow3').create(selectDAT, 'defaulthash')
            defaulthash.python = True
            defaulthash.par.dat.expr = 'op.ATM.op("timeline/newhashrow3_1")'

            defaulthash = newhashrow.op('newhashrow3/defaulthash2')
            defaulthash.destroy()
            defaulthash = newhashrow.op('newhashrow3').create(selectDAT, 'defaulthash2')
            defaulthash.python = True
            defaulthash.par.dat.expr = 'op.ATM.op("timeline/newhashrow3_2")'

            newhashrow3 = newhashrow.op('newhashrow3')
            newhashrow3.par.bgcolorr.expr = 'op.ATM.par.Knobdisabler'
            newhashrow3.par.bgcolorg.expr = 'op.ATM.par.Knobdisableg'
            newhashrow3.par.bgcolorb.expr = 'op.ATM.par.Knobdisableb'
            newhashrow3.par.bgalpha.expr = 'op.ATM.par.Knobdisablea'
            newhashrow3.par.borderar.expr = 'op.ATM.par.Buttontextdisabler'
            newhashrow3.par.borderag.expr = 'op.ATM.par.Buttontextdisableg'
            newhashrow3.par.borderab.expr = 'op.ATM.par.Buttontextdisableb'
            newhashrow3.par.borderaalpha.expr = 'op.ATM.par.Buttontextdisablea'




    def fixTransport(self):
        timeline = op('/ui/dialogs/timeline')
        transport = timeline.op('transport')
        frame = transport.op('frame')
        frame.python = True
        frame.par.w.expr = 'op("container1").par.w'
        frame.par.bgcolorr.expr = 'op.ATM.par.Knobdisabler'
        frame.par.bgcolorg.expr = 'op.ATM.par.Knobdisableg'
        frame.par.bgcolorb.expr = 'op.ATM.par.Knobdisableb'
        frame.par.bgalpha.expr = 'op.ATM.par.Knobdisablea'
        frame.par.borderar.expr = 'op.ATM.par.Buttonborderar'
        frame.par.borderag.expr = 'op.ATM.par.Buttonborderag'
        frame.par.borderab.expr = 'op.ATM.par.Buttonborderab'
        frame.par.borderaalpha.expr = 'op.ATM.par.Buttonborderaa'

        timecode = transport.op('timecode')
        timecode.python = True
        timecode.par.display.expr = '1 if op("timedisplay")["index"] == 0 else 0'
        timecode.par.bgcolorr.expr = 'op.ATM.par.Knobdisabler'
        timecode.par.bgcolorg.expr = 'op.ATM.par.Knobdisableg'
        timecode.par.bgcolorb.expr = 'op.ATM.par.Knobdisableb'
        timecode.par.bgalpha.expr = 'op.ATM.par.Knobdisablea'
        timecode.par.borderar.expr = 'op.ATM.par.Buttonborderar'
        timecode.par.borderag.expr = 'op.ATM.par.Buttonborderag'
        timecode.par.borderab.expr = 'op.ATM.par.Buttonborderab'
        timecode.par.borderaalpha.expr = 'op.ATM.par.Buttonborderaa'


        musiccode = transport.op('musiccode')
        musiccode.python = True
        musiccode.par.display.expr = '1 if op("timedisplay")["index"] == 1 else 0'
        musiccode.par.bgcolorr.expr = 'op.ATM.par.Knobdisabler'
        musiccode.par.bgcolorg.expr = 'op.ATM.par.Knobdisableg'
        musiccode.par.bgcolorb.expr = 'op.ATM.par.Knobdisableb'
        musiccode.par.bgalpha.expr = 'op.ATM.par.Knobdisablea'
        musiccode.par.borderar.expr = 'op.ATM.par.Buttonborderar'
        musiccode.par.borderag.expr = 'op.ATM.par.Buttonborderag'
        musiccode.par.borderab.expr = 'op.ATM.par.Buttonborderab'
        musiccode.par.borderaalpha.expr = 'op.ATM.par.Buttonborderaa'

        transport_panel = timeline.op('transportpanel')
        transport_panel.par.borderaalpha = 0

    def fixRangebar(self):
        timeline = op('/ui/dialogs/timeline')
        rangebar = timeline.op('rangebar')
        rangebar.python = True
        rangebar.par.w.expr = 'op("transportpanel").par.w'
        rangebar.par.bgcolorr.expr = 'op.ATM.par.Knobdisabler'
        rangebar.par.bgcolorg.expr = 'op.ATM.par.Knobdisableg'
        rangebar.par.bgcolorb.expr = 'op.ATM.par.Knobdisableb'
        rangebar.par.bgalpha.expr = 'op.ATM.par.Knobdisablea'
        rangebar.par.borderar.expr = 'op.ATM.par.Gadgetborderar'
        rangebar.par.borderag.expr = 'op.ATM.par.Gadgetborderag'
        rangebar.par.borderab.expr = 'op.ATM.par.Gadgetborderab'
        rangebar.par.borderaalpha.expr = 'op.ATM.par.Gadgetborderaa'

        range_start = rangebar.op('range_start')
        range_start.python = True
        range_start.par.h.expr = 'parent().par.h-4'
        range_start.par.bgcolorr.expr = 'op.ATM.par.Sliderbgonr'
        range_start.par.bgcolorg.expr = 'op.ATM.par.Sliderbgong'
        range_start.par.bgcolorb.expr = 'op.ATM.par.Sliderbgonb'
        range_start.par.bgalpha.expr = 'op.ATM.par.Sliderbgona'
        range_start.par.borderar.expr = 'op.ATM.par.Gadgetborderar'
        range_start.par.borderag.expr = 'op.ATM.par.Gadgetborderag'
        range_start.par.borderab.expr = 'op.ATM.par.Gadgetborderab'
        range_start.par.borderaalpha.expr = 'op.ATM.par.Gadgetborderaa'
        range_start.par.repositionxmax.expr = 'op("range_end").par.x - op("range_end").par.w - 2'

        range_end = rangebar.op('range_end')
        range_end.python = True
        range_end.par.h.expr = 'parent().par.h-4'
        range_end.par.bgcolorr.expr = 'op.ATM.par.Sliderbgonr'
        range_end.par.bgcolorg.expr = 'op.ATM.par.Sliderbgong'
        range_end.par.bgcolorb.expr = 'op.ATM.par.Sliderbgonb'
        range_end.par.bgalpha.expr = 'op.ATM.par.Sliderbgona'
        range_end.par.borderar.expr = 'op.ATM.par.Gadgetborderar'
        range_end.par.borderag.expr = 'op.ATM.par.Gadgetborderag'
        range_end.par.borderab.expr = 'op.ATM.par.Gadgetborderab'
        range_end.par.borderaalpha.expr = 'op.ATM.par.Gadgetborderaa'

        range_end.par.repositionxmin.expr = 'op("range_start").par.x + op("range_start").par.w + 2'
        range_end.par.repositionxmax.expr = 'parent().par.w - me.par.w -3'

    def fixFPS(self):
        mainmanu = op('/ui/dialogs/mainmenu')
        fps = mainmanu.op('fps1')
        fps.par.borderar.expr = 'op.ATM.par.Gadgetborderar'
        fps.par.borderag.expr = 'op.ATM.par.Gadgetborderag'
        fps.par.borderab.expr = 'op.ATM.par.Gadgetborderab'
        fps.par.borderaalpha.expr = 'op.ATM.par.Gadgetborderaa'


    def OnThemeChange(self, dat):
        """Called by DAT Execute when theme CSS file changes"""
        if not dat or not dat.text:
            return

        try:
            # Parse CSS theme file
            newColors = self._cssParser.parse(dat.text)
        except Exception as e:
            #debug(f'AcroThemeManager: CSS parse error - {e}')
            return

        if not newColors:
            #debug('AcroThemeManager: No valid colors parsed from theme')
            return

        # Separate colors by type
        tuik2_colors = {}
        op_colors = {}
        ui_colors = {}

        for key, rgba in newColors.items():
            if key.startswith('TUIK2.'):
                tuik2_colors[key[6:]] = rgba  # Strip 'TUIK2.' prefix
            elif key.startswith('op.') and '.par.' in key:
                op_colors[key] = rgba
            else:
                ui_colors[key] = rgba

        # Apply ui.colors
        if ui_colors:
            if not self._previousColors:
                # First load - apply everything
                self._applyAllColors(ui_colors)
            else:
                # Diff and apply only changes
                self._applyChangedColors(ui_colors)

            # Optionally export a TouchColors file to the project folder.
            # User can copy it to TD's install Config dir so future TD
            # launches start themed (avoids per-attribute ui.colors writes).
            write_par = getattr(self.ownerComp.par, 'Writetouchcolors', None)
            if write_par is not None and write_par.eval():
                self.WriteTouchColorsFile(ui_colors=ui_colors)

        # Apply TUIK2 colors to parameters
        if tuik2_colors:
            self._applyTUIK2Colors(tuik2_colors)

        # Apply op shortcut colors
        if op_colors:
            self._applyOpColors(op_colors)

        self._previousColors = ui_colors.copy()
        self._previousTUIK2Colors = tuik2_colors.copy()
        self._previousOpColors = op_colors.copy()

        # Fire callback
        self.DoCallback('onThemeLoaded', {
            'ownerComp': self.ownerComp,
            'colors': ui_colors,
            'tuik2Colors': tuik2_colors,
            'opColors': op_colors,
            'count': len(ui_colors) + len(tuik2_colors) + len(op_colors)
        })

    def _applyAllColors(self, colors):
        """Apply all colors, checking ui.colors first to skip redundant writes"""
        count = 0
        skipped = 0
        for key, rgb in colors.items():
            try:
                # Only use RGB (first 3 values), ui.colors doesn't support alpha
                new_color = tuple(rgb[:3])
                current = ui.colors[key]
                # Check if already matches (with tolerance for float precision)
                if self._colorsMatch(current, new_color):
                    skipped += 1
                else:
                    ui.colors[key] = new_color
                    count += 1
            except Exception as e:
                debug(f'AcroThemeManager: Failed to set {key}: {e}')
        #debug(f'AcroThemeManager: Applied {count} colors, skipped {skipped} unchanged')

    def _colorsMatch(self, a, b, tolerance=0.01):
        """Check if two RGB tuples match within tolerance"""
        return (abs(a[0] - b[0]) < tolerance and
                abs(a[1] - b[1]) < tolerance and
                abs(a[2] - b[2]) < tolerance)

    def _applyChangedColors(self, newColors):
        """Apply only colors that changed from previous theme parse"""
        count = 0
        for key, rgb in newColors.items():
            oldRgb = self._previousColors.get(key)
            if oldRgb != rgb:
                try:
                    # Only use RGB (first 3 values), ui.colors doesn't support alpha
                    ui.colors[key] = tuple(rgb[:3])
                    count += 1
                except Exception as e:
                    debug(f'AcroThemeManager: Failed to set {key}: {e}')
        # if count > 0:
        #     debug(f'AcroThemeManager: Updated {count} changed colors')

    def _applyTUIK2Colors(self, colors):
        """Apply TUIK2 colors to ThemeManager parameters

        Args:
            colors: dict of {color_name: [r, g, b, a]} without TUIK2. prefix
        """
        count = 0
        for color_name, rgba in colors.items():
            par_name = _tuik2_par_name(color_name)

            # Check if parameter exists
            par_r = getattr(self.ownerComp.par, par_name + 'r', None)
            if par_r is None:
                debug(f'AcroThemeManager: Unknown TUIK2 color: {color_name}')
                continue

            # Set RGBA values
            r, g, b = rgba[0], rgba[1], rgba[2]
            a = rgba[3] if len(rgba) > 3 else 1.0

            self.ownerComp.par[par_name + 'r'] = r
            self.ownerComp.par[par_name + 'g'] = g
            self.ownerComp.par[par_name + 'b'] = b
            self.ownerComp.par[par_name + 'a'] = a
            count += 1

        # if count > 0:
        #     debug(f'AcroThemeManager: Applied {count} TUIK2 colors')

    def _applyOpColors(self, colors):
        """Apply colors to component parameters via op shortcuts

        Args:
            colors: dict of {'op.SHORTCUT.par.Parname': [r, g, b, a]}
        """
        count = 0
        for key, rgba in colors.items():
            # Parse key: 'op.AW.par.Tabcolor'
            match = re.match(r'^op\.([A-Z][A-Z0-9_]*?)\.par\.([A-Za-z0-9]+)$', key)
            if not match:
                debug(f'AcroThemeManager: Invalid op color key: {key}')
                continue

            shortcut = match.group(1)  # 'MCW'
            par_base = match.group(2)  # 'Tabcolor'

            # Resolve op shortcut dynamically
            comp = getattr(op, shortcut, None)
            if comp is None:
                debug(f'AcroThemeManager: Unknown op shortcut: op.{shortcut}')
                continue

            # Verify it's a component with parameters
            if not hasattr(comp, 'par'):
                debug(f'AcroThemeManager: op.{shortcut} has no parameters')
                continue

            # Check parameter exists (via 'r' suffix)
            if not hasattr(comp.par, par_base + 'r'):
                debug(f'AcroThemeManager: Parameter not found: op.{shortcut}.par.{par_base}r')
                continue

            # Apply RGBA values
            r, g, b = rgba[0], rgba[1], rgba[2]
            a = rgba[3] if len(rgba) > 3 else 1.0

            try:
                comp.par[par_base + 'r'] = r
                comp.par[par_base + 'g'] = g
                comp.par[par_base + 'b'] = b
                comp.par[par_base + 'a'] = a
                count += 1
            except Exception as e:
                debug(f'AcroThemeManager: Failed to set op.{shortcut}.par.{par_base}: {e}')

        # if count > 0:
        #     debug(f'AcroThemeManager: Applied {count} op shortcut colors')

    def Refresh(self):
        """Force full refresh from theme file"""
        self._previousColors = {}
        self._previousTUIK2Colors = {}
        self._previousOpColors = {}
        if self.ThemeDAT:
            self.OnThemeChange(self.ThemeDAT)

    def SaveTheme(self, filepath=None, name="Custom Theme", include_tuik2=True):
        """Export current ui.colors and TUIK2 parameters to CSS file

        Args:
            filepath: Output path (uses Themefile parameter if None)
            name: Theme name for header comment
            include_tuik2: Include TUIK2 color parameters in export
        """
        # Collect all ui.colors
        colors = {}
        for key in ui.colors:
            r, g, b = ui.colors[key]
            colors[key] = [r, g, b]

        # Collect TUIK2 colors from parameters
        if include_tuik2:
            for color_name in TUIK2_COLORS:
                par_name = _tuik2_par_name(color_name)
                par_r = getattr(self.ownerComp.par, par_name + 'r', None)
                if par_r is not None:
                    r = self.ownerComp.par[par_name + 'r'].eval()
                    g = self.ownerComp.par[par_name + 'g'].eval()
                    b = self.ownerComp.par[par_name + 'b'].eval()
                    a = self.ownerComp.par[par_name + 'a'].eval()
                    colors[f'TUIK2.{color_name}'] = [r, g, b, a]

        # Format as CSS
        css_content = self._cssParser.format_css(colors, name=name)

        path = filepath or self.ownerComp.par.Themefile.eval()
        if path:
            with open(path, 'w') as f:
                f.write(css_content)
            debug(f'AcroThemeManager: Saved theme to {path}')
        else:
            debug('AcroThemeManager: No theme file path specified')

    def _touchColorsSourcePath(self):
        """TD's install-dir TouchColors file (read-only baseline)"""
        return os.path.normpath(
            os.path.join(app.binFolder, '..', 'Config', 'TouchColors'))

    def _touchColorsOutputPath(self):
        """Where we write the modified TouchColors file (project folder)"""
        return os.path.normpath(
            os.path.join(project.folder, 'TouchColors'))

    def _touchColorsBackupPath(self):
        """One-shot backup of the original install TouchColors (project folder).
        Written only if it doesn't already exist — preserves the truly original
        bytes even across repeated theme writes."""
        return os.path.normpath(
            os.path.join(project.folder, 'TouchColors.original'))

    def WriteTouchColorsFile(self, ui_colors=None, output_path=None):
        """Export a TouchColors file to the project folder for the user to
        copy into TD's install Config dir.

        Reads TD's install TouchColors as a baseline, overrides keys present
        in ui_colors, and writes the result to output_path. Original line
        endings (CRLF/LF), trailing newline, ordering, key coverage, and
        unrelated lines are preserved byte-for-byte from the source.

        The output is written to the project folder (no admin needed). The
        user can manually copy it to:
            C:/Program Files/Derivative/TouchDesigner/Config/TouchColors

        Args:
            ui_colors:   dict of {key: (r, g, b)} to override. If None,
                         snapshots current ui.colors.
            output_path: override output location. Defaults to
                         {project.folder}/TouchColors.

        Returns:
            bool: True on successful write or no-op match, False on failure.
        """
        source_path = self._touchColorsSourcePath()
        if output_path is None:
            output_path = self._touchColorsOutputPath()

        if not os.path.exists(source_path):
            debug(f'AcroThemeManager: Source TouchColors not found at '
                  f'{source_path}')
            return False

        if ui_colors is None:
            ui_colors = {}
            for key in ui.colors:
                ui_colors[key] = tuple(ui.colors[key])

        try:
            with open(source_path, 'rb') as f:
                original = f.read()
        except Exception as e:
            debug(f'AcroThemeManager: Failed to read source TouchColors: {e}')
            return False

        # One-shot: capture the install file's original bytes the first time
        # we write. Idempotent — never overwrites an existing backup, since
        # by then the source may already be a previously-applied theme.
        backup_path = self._touchColorsBackupPath()
        if not os.path.exists(backup_path):
            try:
                with open(backup_path, 'wb') as f:
                    f.write(original)
                debug(f'AcroThemeManager: Saved original TouchColors backup to '
                      f'{backup_path}')
            except Exception as e:
                debug(f'AcroThemeManager: Failed to write backup '
                      f'{backup_path}: {e}')

        # Detect line ending style — preserve exactly
        line_ending = b'\r\n' if b'\r\n' in original else b'\n'
        lines = original.split(line_ending)

        overrides = 0
        seen_keys = set()
        new_lines = []

        for line in lines:
            try:
                text = line.decode('utf-8')
            except UnicodeDecodeError:
                new_lines.append(line)
                continue

            if not text:
                new_lines.append(line)
                continue

            parts = text.split('\t')
            if len(parts) < 4:
                new_lines.append(line)
                continue

            key = parts[0]
            if key not in ui_colors:
                new_lines.append(line)
                continue

            seen_keys.add(key)
            rgb = ui_colors[key]
            r = float(rgb[0]) if len(rgb) > 0 else 0.0
            g = float(rgb[1]) if len(rgb) > 1 else 0.0
            b = float(rgb[2]) if len(rgb) > 2 else 0.0
            new_lines.append(
                f'{key}\t{r:g}\t{g:g}\t{b:g}'.encode('utf-8'))
            overrides += 1

        new_data = line_ending.join(new_lines)

        # Sanity: line count must match exactly
        if new_data.count(line_ending) != original.count(line_ending):
            debug('AcroThemeManager: Refusing to write TouchColors — '
                  'line count mismatch.')
            return False

        # No-op short-circuit when output already matches
        if os.path.exists(output_path):
            try:
                with open(output_path, 'rb') as f:
                    existing = f.read()
                if existing == new_data:
                    debug(f'AcroThemeManager: TouchColors output already up '
                          f'to date at {output_path}')
                    return True
            except Exception:
                pass

        try:
            with open(output_path, 'wb') as f:
                f.write(new_data)
        except Exception as e:
            debug(f'AcroThemeManager: Failed to write {output_path}: {e}')
            return False

        skipped = [k for k in ui_colors if k not in seen_keys]
        debug(f'AcroThemeManager: Wrote {overrides} colors to {output_path} '
              f'({len(skipped)} ui.colors keys not present in TouchColors). '
              f'Copy to {source_path} to apply at next TD launch.')
        return True

    def ExportDefault(self):
        """Export TD default colors to a CSS file"""
        # Reset to defaults first
        ui.colors.resetToDefaults()

        # Save to themes folder
        repo_path = self.ownerComp.par.Repopath.eval()
        path = f"{repo_path}/themes/td-default.css"

        # Create themes directory if needed
        themes_dir = f"{repo_path}/themes"
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)

        self.SaveTheme(path, name="TouchDesigner Default")
        debug(f'AcroThemeManager: Exported TD defaults to {path}')

    def ResetToDefaults(self):
        """Reset all ui.colors to TouchDesigner defaults"""
        ui.colors.resetToDefaults()
        self._previousColors = {}
        self._previousTUIK2Colors = {}

        # Reset TUIK2 parameters to values from color comp
        color_comp = op(TUIK2_COLOR_COMP)
        for color_name in TUIK2_COLORS:
            par_name = _tuik2_par_name(color_name)
            par_r = getattr(self.ownerComp.par, par_name + 'r', None)
            if par_r is not None:
                # Get values from TUIK2 color comp
                r, g, b, a = 0.5, 0.5, 0.5, 1.0
                if color_comp:
                    color_top = color_comp.op(color_name)
                    if color_top:
                        r = color_top.par.colorr.eval()
                        g = color_top.par.colorg.eval()
                        b = color_top.par.colorb.eval()
                        a = color_top.par.alpha.eval() if hasattr(color_top.par, 'alpha') else 1.0
                self.ownerComp.par[par_name + 'r'] = r
                self.ownerComp.par[par_name + 'g'] = g
                self.ownerComp.par[par_name + 'b'] = b
                self.ownerComp.par[par_name + 'a'] = a

        debug('AcroThemeManager: Reset to TD defaults')

    # -------------------------------------------------------------------------
    # Pulse Handlers
    # -------------------------------------------------------------------------

    def pulse_Editextension(self):
        """Open extension for editing"""
        self.ownerComp.op('AcroThemeManager').par.edit.pulse()

    def pulse_Loadtheme(self):
        """Force reload theme from file"""
        self.Refresh()

    def pulse_Savetheme(self):
        """Save current colors to theme file"""
        self.SaveTheme()

    def pulse_Exportdefault(self):
        """Export TD default colors to themes folder"""
        self.ExportDefault()

    def pulse_Resettodefaults(self):
        """Reset ui.colors to TD defaults"""
        self.ResetToDefaults()

    def pulse_Updatetouchcolors(self):
        """Manually export current ui.colors to a TouchColors file in the
        project folder"""
        self.WriteTouchColorsFile()
