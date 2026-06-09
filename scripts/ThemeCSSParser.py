"""CSS Theme Parser for AcroThemeManager

Parses valid CSS theme files with variable support for TouchDesigner ui.colors.

Supported color formats:
    - Hex codes: #FF5500 or #F50 (3 or 6 digit)
    - HSL: hsl(180, 50%, 50%) (hue 0-360, saturation/lightness 0-100%)
    - RGB 0-255: rgb(128, 128, 128)
    - RGBA 0-255: rgba(128, 128, 128, 0.8) (alpha 0-1)
    - RGB floats: 0.5 0.5 0.5 (legacy format, still supported)
    - RGBA floats: 0.5 0.5 0.5 0.8 (legacy format with alpha)

Supported functions:
    - var(--name): Reference a CSS variable
    - lighten(color, amount): Increase HSV Value by amount (0.0-1.0)
    - darken(color, amount): Decrease HSV Value by amount (0.0-1.0)

Example (valid CSS format):
    :root {
        --bg-dark: #1a1a1a;
        --text-primary: hsl(54, 100%, 50%);
    }

    dat.bg.editable { color: var(--bg-dark); }
    dat.bg.hilite { color: lighten(var(--bg-dark), 0.1); }
    dat.python.strings { color: #F19768; }

    /* TUIK2 colors use RGBA for alpha support */
    TUIK2.button_off { color: rgba(54, 57, 64, 1); }
"""
import re
import colorsys


class ThemeCSSParser:
    """Parses CSS theme files with variable support and color functions"""

    def __init__(self):
        self.variables = {}  # --name: [r, g, b] or raw string before resolution
        self.colors = {}     # ui.colors key: [r, g, b]

    def parse(self, css_text):
        """Parse CSS text and return resolved colors dict

        Args:
            css_text: CSS theme file content

        Returns:
            dict: {color_key: [r, g, b], ...} with all variables resolved
        """
        self.variables = {}
        self.colors = {}

        # Remove comments
        css_text = self._remove_comments(css_text)

        # Extract :root variables (keep as raw strings initially)
        self._parse_root_block(css_text)

        # Extract color declarations
        self._parse_declarations(css_text)

        # Resolve all values (variables first, then color declarations)
        self._resolve_all()

        return self.colors

    def _remove_comments(self, text):
        """Remove /* */ and // comments"""
        # Remove block comments
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        # Remove line comments
        text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
        return text

    def _parse_root_block(self, text):
        """Extract variables from :root { } block"""
        match = re.search(r':root\s*\{([^}]*)\}', text)
        if match:
            block = match.group(1)
            # Parse --variable: value; (keep value as raw string)
            for m in re.finditer(r'(--[\w-]+)\s*:\s*([^;]+);?', block):
                name = m.group(1)
                value = m.group(2).strip()
                self.variables[name] = value

    def _parse_declarations(self, text):
        """Extract color declarations outside :root block

        Supports two formats:
        - New (valid CSS): selector { color: value; }
        - Legacy: selector: value;
        """
        # Remove :root block to avoid re-parsing
        text = re.sub(r':root\s*\{[^}]*\}', '', text)

        # First try new format: selector { color: value; }
        for m in re.finditer(r'([\w.-]+)\s*\{\s*color\s*:\s*([^;}]+);?\s*\}', text):
            key = m.group(1).strip()
            value = m.group(2).strip()
            self.colors[key] = value

        # Also support legacy format: selector: value;
        # (for backwards compatibility during transition)
        for m in re.finditer(r'([\w.-]+)\s*:\s*([^;{\n]+);', text):
            key = m.group(1).strip()
            value = m.group(2).strip()
            # Skip if already parsed from rule block, or if it's a CSS property
            if key not in self.colors and not key.startswith('--') and key != 'color':
                self.colors[key] = value

    def _resolve_all(self):
        """Resolve all variables and color declarations to RGB values"""
        # First resolve variables to RGB (they might reference other variables)
        for name, value in list(self.variables.items()):
            if isinstance(value, str):
                resolved = self._resolve_value(value)
                self.variables[name] = resolved  # May be None if unresolvable

        # Then resolve color declarations
        for key, value in list(self.colors.items()):
            if isinstance(value, str):
                resolved = self._resolve_value(value)
                if resolved:
                    self.colors[key] = resolved
                else:
                    # Invalid or unresolvable value - remove entry
                    del self.colors[key]

    def _resolve_value(self, value):
        """Resolve a value that may contain var(), lighten(), darken()

        Args:
            value: Raw string value like "var(--bg)", "lighten(#FF0000, 0.1)", "#FF5500"

        Returns:
            list: [r, g, b] floats or None if unresolvable
        """
        if not isinstance(value, str):
            return value  # Already resolved

        value = value.strip()

        # Handle lighten(color, amount) / darken(color, amount)
        match = re.match(r'(lighten|darken)\s*\(\s*(.+?)\s*,\s*([\d.]+)\s*\)', value)
        if match:
            func, color_arg, amount = match.groups()
            # Color arg might be var(--name) or direct color
            color = self._resolve_value(color_arg)
            if color:
                return self._adjust_brightness(color, float(amount), func == 'lighten')
            return None

        # Handle var(--name)
        match = re.match(r'var\s*\(\s*(--[\w-]+)\s*\)', value)
        if match:
            var_name = match.group(1)
            var_value = self.variables.get(var_name)
            if var_value is None:
                return None
            # Recursively resolve if it's still a string
            if isinstance(var_value, str):
                return self._resolve_value(var_value)
            return var_value

        # Direct color value
        return self._parse_color(value)

    def _parse_color(self, value):
        """Parse any color format to [r, g, b] floats (0-1)

        Args:
            value: Color string in hex, hsl, rgb(), or RGB float format

        Returns:
            list: [r, g, b] as floats (0.0-1.0), or None if invalid
        """
        if not isinstance(value, str):
            return value if isinstance(value, list) else None

        value = value.strip()

        # Hex: #RGB or #RRGGBB
        if value.startswith('#'):
            return self._parse_hex(value)

        # HSL: hsl(h, s%, l%)
        match = re.match(r'hsl\s*\(\s*([\d.]+)\s*,\s*([\d.]+)%?\s*,\s*([\d.]+)%?\s*\)', value)
        if match:
            h = float(match.group(1)) / 360  # Hue: 0-360 -> 0-1
            s = float(match.group(2)) / 100  # Saturation: 0-100% -> 0-1
            l = float(match.group(3)) / 100  # Lightness: 0-100% -> 0-1
            # Note: colorsys uses HLS order (Hue, Lightness, Saturation)
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return [r, g, b]

        # RGBA 0-255: rgba(128, 128, 128, 0.8) - alpha is 0-1
        match = re.match(r'rgba\s*\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)', value)
        if match:
            r = float(match.group(1)) / 255
            g = float(match.group(2)) / 255
            b = float(match.group(3)) / 255
            a = float(match.group(4))  # Alpha is already 0-1
            return [r, g, b, a]

        # RGB 0-255: rgb(128, 128, 128)
        match = re.match(r'rgb\s*\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)', value)
        if match:
            r = float(match.group(1)) / 255
            g = float(match.group(2)) / 255
            b = float(match.group(3)) / 255
            return [r, g, b]

        # RGBA floats (legacy): 0.5 0.5 0.5 0.8 or 0.5, 0.5, 0.5, 0.8
        parts = re.split(r'[\s,]+', value)
        if len(parts) >= 4:
            try:
                return [float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])]
            except ValueError:
                pass

        # RGB floats (legacy): 0.5 0.5 0.5 or 0.5, 0.5, 0.5
        if len(parts) >= 3:
            try:
                return [float(parts[0]), float(parts[1]), float(parts[2])]
            except ValueError:
                pass

        return None

    def _parse_hex(self, value):
        """Parse #RGB or #RRGGBB to [r, g, b] floats

        Args:
            value: Hex color string like "#FF5500" or "#F50"

        Returns:
            list: [r, g, b] as floats (0.0-1.0), or None if invalid
        """
        hex_str = value.lstrip('#')

        # Expand 3-digit hex to 6-digit
        if len(hex_str) == 3:
            hex_str = ''.join(c * 2 for c in hex_str)

        if len(hex_str) == 6:
            try:
                r = int(hex_str[0:2], 16) / 255
                g = int(hex_str[2:4], 16) / 255
                b = int(hex_str[4:6], 16) / 255
                return [r, g, b]
            except ValueError:
                pass

        return None

    def _adjust_brightness(self, rgb, amount, lighten=True):
        """Adjust brightness via HSV Value channel

        Args:
            rgb: [r, g, b] floats (0-1)
            amount: Amount to adjust (0.0-1.0)
            lighten: True to increase brightness, False to decrease

        Returns:
            list: [r, g, b] with adjusted brightness
        """
        r, g, b = rgb
        h, s, v = colorsys.rgb_to_hsv(r, g, b)

        if lighten:
            v = min(1.0, v + amount)
        else:
            v = max(0.0, v - amount)

        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return [r, g, b]

    def _rgb_to_hex(self, rgb):
        """Convert [r, g, b] floats (0-1) to #RRGGBB hex string

        Args:
            rgb: [r, g, b] as floats (0.0-1.0)

        Returns:
            str: Hex color string like "#FF5500"
        """
        r = int(round(rgb[0] * 255))
        g = int(round(rgb[1] * 255))
        b = int(round(rgb[2] * 255))
        # Clamp to valid range
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return f'#{r:02X}{g:02X}{b:02X}'

    def _rgba_to_css(self, rgba):
        """Convert [r, g, b, a] floats (0-1) to rgba(r, g, b, a) CSS string

        Args:
            rgba: [r, g, b, a] as floats (0.0-1.0)

        Returns:
            str: CSS rgba string like "rgba(128, 128, 128, 0.8)"
        """
        r = int(round(rgba[0] * 255))
        g = int(round(rgba[1] * 255))
        b = int(round(rgba[2] * 255))
        a = rgba[3] if len(rgba) > 3 else 1.0
        # Clamp RGB to valid range
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        a = max(0.0, min(1.0, a))
        return f'rgba({r}, {g}, {b}, {a})'

    # TUIK2 section mapping for organized CSS output
    TUIK2_SECTION_MAP = {
        'button': 'Button', 'buttontext': 'Button',
        'checkbox': 'Checkbox',
        'field': 'Field',
        'gadget': 'Gadget',
        'header': 'Header',
        'indicator': 'Indicator',
        'knob': 'Knob', 'knobindicator': 'Knob',
        'label': 'Label',
        'operator': 'Operator',
        'slider': 'Slider',
        'template': 'Template',
        'titlebar': 'Titlebar',
        'root': 'Other', 'transparent': 'Other',
    }

    def _get_tuik2_section(self, color_name):
        """Get TUIK2 section name for a color"""
        # color_name is like 'button_off', 'buttontext_on', etc.
        for prefix, section in self.TUIK2_SECTION_MAP.items():
            if color_name.startswith(prefix):
                return section
        return 'Other'

    def format_css(self, colors, name="Custom Theme", variables=None):
        """Format colors dict as valid CSS theme file

        Args:
            colors: dict of {key: [r, g, b]}
            name: Theme name for header comment
            variables: Optional dict of {--name: [r, g, b]} for :root block

        Returns:
            str: Formatted CSS theme content with rule blocks and hex colors
        """
        lines = [f'/* Theme: {name} */\n']

        # Add variables block if provided
        if variables:
            lines.append('\n:root {\n')
            for var_name, rgb in sorted(variables.items()):
                hex_color = self._rgb_to_hex(rgb)
                lines.append(f'    {var_name}: {hex_color};\n')
            lines.append('}\n')

        # Separate TUIK2 colors from regular colors
        tuik2_colors = {}
        regular_colors = {}
        for key, rgb in colors.items():
            if key.startswith('TUIK2.'):
                tuik2_colors[key] = rgb
            else:
                regular_colors[key] = rgb

        # Group regular colors by prefix
        groups = {}
        for key, rgb in regular_colors.items():
            prefix = key.split('.')[0] if '.' in key else 'other'
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append((key, rgb))

        # Write regular colors organized by prefix
        for prefix in sorted(groups.keys()):
            lines.append(f'\n/* {prefix} */\n')
            for key, color in sorted(groups[prefix]):
                color_str = self._rgb_to_hex(color)
                lines.append(f'{key} {{ color: {color_str}; }}\n')

        # Group TUIK2 colors by section
        if tuik2_colors:
            lines.append('\n/* ========== TUIK2 UI Colors ========== */\n')
            tuik2_sections = {}
            for key, rgba in tuik2_colors.items():
                color_name = key[6:]  # Strip 'TUIK2.' prefix
                section = self._get_tuik2_section(color_name)
                if section not in tuik2_sections:
                    tuik2_sections[section] = []
                tuik2_sections[section].append((key, rgba))

            # Write TUIK2 colors organized by section
            section_order = ['Button', 'Checkbox', 'Field', 'Gadget', 'Header',
                           'Indicator', 'Knob', 'Label', 'Operator', 'Slider',
                           'Template', 'Titlebar', 'Other']
            for section in section_order:
                if section in tuik2_sections:
                    lines.append(f'\n/* TUIK2 {section} */\n')
                    for key, color in sorted(tuik2_sections[section]):
                        color_str = self._rgba_to_css(color)
                        lines.append(f'{key} {{ color: {color_str}; }}\n')

        return ''.join(lines)
