# CLAUDE.md — acro-td-theme-manager

## Overview

Theme system for TouchDesigner. Provides CSS-based color theming with a custom parser, theme manager extension, and a library of themes.

## Architecture

```
Theme CSS file → ThemeCSSParser.py → AcroThemeManager.py → TD ui.colors / TUIK2 params / op.* params
```

- **ThemeCSSParser** (`scripts/ThemeCSSParser.py`) — Parses CSS theme files into resolved RGB color values
- **AcroThemeManager** (`scripts/AcroThemeManager.py`) — Applies parsed colors to TouchDesigner's UI system
- **Themes** (`themes/`) — CSS files defining color schemes

## CSS Parser Capabilities

### Supported Features
- `var(--name)` — CSS variable references (recursive resolution supported)
- `lighten(color, amount)` — Increases HSV Value by amount (0.0–1.0)
- `darken(color, amount)` — Decreases HSV Value by amount (0.0–1.0)
- `var()` inside `lighten()`/`darken()` — fully supported (recursive)
- Color formats: `#RRGGBB`, `#RGB`, `hsl(h, s%, l%)`, `rgb(r, g, b)`, `rgba(r, g, b, a)`, float tuples (`0.5 0.5 0.5`)

### NOT Supported
- `calc()` or mathematical operations
- Chaining functions: `lighten(darken(...), ...)` does NOT work
- Negative amounts — use `darken()` instead of `lighten()` with negative values
- Extracting channels from `var()` for use inside `rgba()` — e.g. `rgba(var(--color), 0.5)` won't work

### Color Application
- Colors are separated into 3 categories: `ui.colors` (core TD), `TUIK2.*` (UI2 widgets), `op.*` (component parameters)
- Alpha channel is stripped for `ui.colors` (TD core doesn't support alpha)
- TUIK2 colors are stored as RGBA parameters on the ThemeManager component
- Theme diffs are computed on reload — only changed colors are reapplied

## Theme File Structure

Themes use two sections:

1. **`:root {}` block** — CSS variable definitions (the palette)
2. **Selector rules** — Map TD's internal color names to variables (e.g., `dat.bg.editable { color: var(--dat-bg); }`)

### Selector Name Format
- Core TD colors: `category.element.state` (e.g., `parms.button.bg.loc`)
- TUIK2 colors: `TUIK2.element_state` (e.g., `TUIK2.button_off`)
- Component params: `op.SHORTCUT.par.Parname` (e.g., `op.AW.par.Wcbg`)

### TUIK2 Operator Selectors — Case Sensitive
The TUIK2 operator selectors use UPPERCASE family names:
```
TUIK2.operator_CHOP    (not TUIK2.operator_chop)
TUIK2.operator_COMP
TUIK2.operator_DAT
```

## Base Template System (`td-base-template.css`)

The base template provides ~20 "core palette" variables that cascade to the entire theme via `var()`/`lighten()`/`darken()`. To create a new theme:

1. Copy `td-base-template.css` and rename it
2. Change the `SECTION 1: CORE PALETTE` variables (~20 values)
3. Adjust the gray ramp in `SECTION 2` to match your palette's tint
4. Update secondary syntax colors (GLSL, TScript, XML, YAML) if desired
5. Update CHOP bar colors, jive/textport/splitpane accents
6. Protected sections (op families, parameter modes) cascade automatically

### Core Palette Variables

| Variable | Purpose |
|----------|---------|
| `--palette-bg` | Main background (network editor, code editors) |
| `--palette-bg-dark` | Darkest areas (near-black) |
| `--palette-bg-surface` | Panels, menubar, parameter backgrounds |
| `--palette-bg-raised` | Elevated surfaces (button strips, headers) |
| `--palette-bg-highlight` | Selection, current line, hover |
| `--palette-fg` | Primary text |
| `--palette-fg-bright` | Emphasized text |
| `--palette-fg-muted` | Secondary text, disabled, comments |
| `--palette-fg-dim` | Very dim separators, hints |
| `--palette-accent` | Primary accent (scrollbar, active highlights) |
| `--palette-accent-alt` | Secondary accent (knobs, titlebars) |
| `--palette-accent-alt-bright` | Bright secondary accent (timeline, time indicators) |
| `--palette-tuik-accent` | TUIK2 button accent (TD default orange #BF8148) |
| `--palette-border` | Default border/outline |
| `--palette-keyword` | Syntax: keywords |
| `--palette-function` | Syntax: function names |
| `--palette-string` | Syntax: string literals |
| `--palette-number` | Syntax: numeric literals |
| `--palette-comment` | Syntax: comments |
| `--palette-error` | Errors, critical alerts |
| `--palette-warning` | Warnings |
| `--palette-success` | Success, play state |
| `--palette-info` | Information, links |

## Protected Colors — Rules

### Operator Family Colors
**DO NOT change hues** — users identify operator types by color at a glance.
- CHOP = green, DAT = magenta, MAT = yellow, POP = blue, SOP = blue, TOP = purple
- Value (brightness) and saturation adjustments are OK

**EXCEPTION: COMP is neutral gray** — it has no meaningful hue. COMPs are the most common container type and their color is the most visible background in the parameter panel header. Map `--op-comp` to `var(--palette-bg-surface)` so it blends with the theme. This was discovered by debugging — the COMP family color controls the header bar at the top of the parameter window showing the op name/type.

### Parameter Mode Colors
**DO NOT change hues** — users rely on these to identify parameter binding state:
- Expression = cyan/teal
- Override = green
- Bind/Export = purple
- Constant = default gray

## Key UI Element Mappings

Some TD UI elements are not obvious from their selector names:

| What you see | Selector | Notes |
|-------------|----------|-------|
| Parameter panel header (op name/type bar) | `COMP { color: ... }` | Uses op family color, NOT a dedicated header variable |
| Parameter gadget background | `TUIK2.gadget_bg` | Best as `var(--palette-bg-surface)`, alpha not needed |
| Parameter header strip (? icons row) | `TUIK2.header_bg` | Best as `var(--palette-bg-raised)` |
| Network editor background | `worksheet.bg` | References `--network-bg` |
| Code editor background | `dat.bg.editable` | References `--dat-bg` |
| Playbar strip | `playbar.bg` | References `--playbar-bg` |
| Titlebar (floating windows) | `TUIK2.titlebar_*` | Darken from `--palette-accent-alt` to avoid being too bright |
| Active/pressed buttons | `TUIK2.button_on` | Best as `darken(var(--palette-accent), 0.15)` |
| Timecode/root time display | `TUIK2.root_time` | Darken from `--palette-accent-alt` |

### Known Issues
- `--tuik2-titlebar-*` and `--tuik2-root-time` tend to be too bright if derived directly from accent colors — always use `darken()` on these (0.15–0.25)
- `--tuik2-button-on` similarly needs darkening (0.15) from the accent to avoid overwhelming the UI
- `--tuik2-knobindicator-*` can also pop too hard — darken if needed per theme
- Light themes need inverted gray ramps AND dark DAT editors (code editors stay dark even in light themes)

## Creating Monochrome Themes

For single-color themes (like darkroom, terminal, amber), copy an existing monochrome theme and swap color channels. The pattern:
- All backgrounds use near-black with a faint tint of the chosen color
- All text/UI uses only that color's channel at varying intensities
- Op families and parameter modes are also monochrome (brightness-only differentiation)
- The `darkroom.css` (red) → `terminal.css` (green) → `amber.css` (orange) lineage shows the pattern

## Creating Light Themes

Light themes need special handling:
- **Inverted gray ramp** — lighter values at low numbers (gray-05 = lightest)
- **Dark DAT editors** — code editors stay dark with hardcoded values, not `var(--palette-bg)`
- **Darker op family colors** for readability on light backgrounds
- **Dark text** — `--palette-fg` should be dark, `--palette-fg-bright` even darker
- See `acronym-light2.css` and `catppuccin-latte.css` for examples

## Debugging Themes

To identify which selector controls a specific UI element:

1. Copy `td-default.css` (the raw flat theme with no variables)
2. Replace every color with a unique random color using a script
3. Load the debug theme and visually match the color to the selector
4. See `themes/debug.css` for an example

## Theme Files

### System / Template
| File | Description |
|------|-------------|
| `td-default.css` | Raw TD defaults (flat hex, no variables) |
| `td-default-variables.css` | TD defaults reorganized with CSS variables |
| `td-base-template.css` | Template for creating new themes (palette system) |
| `debug.css` | Every color randomized for UI element identification |

### Popular Code Editor Themes (built from base template)
| File | Description |
|------|-------------|
| `dracula.css` | Dracula — purple bg, pink/green/yellow/orange accents |
| `gruvbox.css` | Gruvbox — warm earthy retro groove |
| `tokyo-night.css` | Tokyo Night — deep blue-purple, vibrant balanced accents |
| `monokai.css` | Monokai — classic Sublime Text, warm olive bg, hot pink/green |
| `nord.css` | Nord — arctic blue, cool Polar Night/Snow Storm/Frost/Aurora |
| `solarized-dark.css` | Solarized Dark — scientific teal-tinted palette |
| `one-dark.css` | One Dark — Atom editor default, muted professional |
| `everforest.css` | Everforest — green-based, warm and soft |
| `rose-pine.css` | Rosé Pine — deep purple, gold/pink/foam accents |
| `kanagawa.css` | Kanagawa — Japanese ink-wash, inspired by Hokusai |

### Catppuccin Family (built from base template)
| File | Description |
|------|-------------|
| `catppuccin-mocha.css` | Catppuccin Mocha — darkest, pastel accents |
| `catppuccin-macchiato.css` | Catppuccin Macchiato — darker |
| `catppuccin-frappe.css` | Catppuccin Frappé — medium dark |
| `catppuccin-latte.css` | Catppuccin Latte — light (softened) |

### Brand Themes (built from base template)
| File | Description |
|------|-------------|
| `acronym-dark2.css` | Acronym brand dark — warm core, marigold accents |
| `acronym-light2.css` | Acronym brand light — warm stone, softened |

### Specialty / Creative Themes (built from base template)
| File | Description |
|------|-------------|
| `lisafrank2.css` | Lisa Frank — neon rainbow overdose, rainbow gray ramp |
| `catnap.css` | Catnap — cat-vision blues/greens/grays, twilight palette |
| `darkroom.css` | Darkroom — red-only night vision, preserves dark adaptation |
| `terminal.css` | Terminal — green phosphor CRT (VT100/Apple II) |
| `amber.css` | Amber — amber phosphor CRT (IBM 3270) |
| `banana.css` | Banana — banana-themed, ripeness gradient CHOP bars |
| `abyss.css` | Abyss — deep ocean bioluminescence |
| `synthwave.css` | Synthwave — 80s retrowave neon, hot pink/electric blue |
| `barbie.css` | Barbie — aggressively, relentlessly pink |
| `high-vis.css` | High Vis — accessibility/WCAG AAA, colorblind-friendly |

### Legacy (pre-template, may be replaced)
| File | Description |
|------|-------------|
| `acronym-dark.css` | Old Acronym dark (replace with acronym-dark2.css) |
| `acronym-light.css` | Old Acronym light (replace with acronym-light2.css) |
| `lisa-frank.css` | Old Lisa Frank (replace with lisafrank2.css) |
| `dark-gold.css` | Dark with gold accents (standalone) |
| `light-mode.css` | Light theme (standalone) |
