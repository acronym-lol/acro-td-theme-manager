# Acro TD Theme Manager

CSS-based theme application for TouchDesigner — applies palettes to `ui.colors`, TUIK2 component params, and op-shortcut params from a single `.css` file.

## What it does

`AcroThemeManager` (`/AcroThemeManager`, shortcut `op.ATM`, extension `ext.AcroThemeManager`) reads a CSS theme file, resolves CSS variables and `lighten()`/`darken()` modifiers, and pushes the resulting colors into TouchDesigner's three theming surfaces:

```
Theme CSS file → ThemeCSSParser → AcroThemeManager → TD ui.colors / TUIK2 params / op.* params
```

| Surface | What it controls |
|---------|------------------|
| `ui.colors` | Core TD colors — network editor, code editors, parameter labels, etc. |
| `TUIK2.*` | TUIK2 widget colors (button states, fields, gadgets, sliders) |
| `op.SHORTCUT.par.X` | Custom component parameters keyed via global shortcuts (e.g. `op.AW.par.Wcbg`) |

A diff is computed on reload — only changed colors are re-pushed, so re-applying the active theme is cheap.

## Quick start

```python
# Force-reload the active theme from disk
op.ATM.Refresh()

# Save current colors (ui + TUIK2 params) to a CSS file
op.ATM.SaveTheme('/path/to/custom.css', name='My Custom Theme')

# Reset everything to TouchDesigner defaults
op.ATM.ResetToDefaults()

# Export TD defaults as a CSS file (for reference / debugging)
op.ATM.ExportDefault()
```

Theme files live in `modules/acro-td-theme-manager/themes/`. The active theme is picked via the `Themefile` parameter on the manager.

## Where to go next

- **[API Reference](theme-manager)** — `AcroThemeManager` class: parameters, properties, every public method.
- **[CSS Format & Parser](theme-format)** — Supported CSS syntax, color formats, selector naming rules.
- **[Base Template & Core Palette](base-template)** — `td-base-template.css` structure, the ~20 core palette variables, how the cascade works.
- **[Protected Colors & UI Mappings](protected-colors)** — Operator family colors and parameter mode colors that must not have hue changes. Reference table of non-obvious TD UI element selectors.
- **[Creating & Debugging Themes](creating-themes)** — Recipes for monochrome / light themes, the `debug.css` random-color trick for locating selectors.
- **[Themes Library](themes-library)** — Catalog of every theme that ships with the module.

## Installation

```bash
git subtree add --prefix=modules/acro-td-theme-manager https://github.com/acronym-lol/acro-td-theme-manager.git main --squash
```

`setup.ps1` / `setup.sh` register `ACRO_TD_THEME_MANAGER` pointing at the module on disk.
