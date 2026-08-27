---
last_reviewed: 2026-08-27
---

# Creating & Debugging Themes

## New theme from scratch

The recommended path is to derive from the base template:

1. Copy `themes/td-base-template.css` to `themes/my-theme.css`.
2. Edit `SECTION 1: CORE PALETTE` — change the ~20 palette variables to fit your aesthetic.
3. Tune the gray ramp in `SECTION 2` to match the palette's tint.
4. Adjust secondary syntax colors (GLSL, TScript, XML, YAML) and CHOP bar colors if desired.
5. Don't touch protected sections (op families, parameter modes) — they cascade automatically. See [Protected Colors](protected-colors).
6. Point the AcroThemeManager `Themefile` param at the new CSS, hit `Refresh`.

The `OnThemeChange` diff means iterating is fast — save the CSS, the synced DAT picks it up, only the changed colors re-push.

## Monochrome themes

The single-color theme family (`darkroom.css`, `terminal.css`, `amber.css`) follows a consistent pattern. Copy any of them and swap the channel:

- Backgrounds use **near-black with a faint tint** of the chosen color (e.g. `rgba(15, 5, 5, 1)` for the red-tinted darkroom).
- All text / UI uses **only that color's channel** at varying intensities — no other hues are introduced.
- Op families and parameter modes are also monochrome — differentiation comes from brightness only, not hue.
- The lineage `darkroom.css` (red) → `terminal.css` (green) → `amber.css` (orange) is the cleanest reference.

These themes have specific use cases:

| Theme | Use case |
|-------|----------|
| `darkroom.css` (red) | Night-vision / dark-adapted work environments |
| `terminal.css` (green) | VT100 / Apple II nostalgia |
| `amber.css` (orange) | IBM 3270 nostalgia |

## Light themes

Light themes need a few non-obvious adjustments:

| What | Why |
|------|-----|
| Inverted gray ramp (`--gray-00` is dark, `--gray-09` is light) | The cascade assumes 00 = lightest. Inverting keeps the visual hierarchy intact. |
| Dark DAT editors (hardcoded values, NOT `var(--palette-bg)`) | Code editors stay dark even in light themes — easier on the eyes during long edits. |
| Darker op family colors | Default op family colors are calibrated for dark backgrounds; they wash out on white. Drop their value. |
| Dark text (`--palette-fg` is dark, `--palette-fg-bright` even darker) | Inverted contrast direction. |

Reference implementations: `acronym-light2.css` and `catppuccin-latte.css`.

## Operator family mappings

The base template maps op family hues in one place. If TouchDesigner introduces a new family (POPs did in 2024), the mapping has to be extended in the template before any derived theme picks it up.

## Debug: which selector controls *this* UI element?

When you can't figure out which selector drives a specific TD pixel, use the random-color trick:

1. Start from `themes/td-default.css` (the raw flat theme with no variables — every selector is a literal hex).
2. Replace every color with a unique random color using a script (or just edit the values manually for the surfaces you care about).
3. Load the debug theme via `op.ATM.par.Themefile`.
4. Eyeball the UI and match the random color you see to its selector line in the CSS.

`themes/debug.css` ships as a pre-made example.

## Programmatic theme creation

The manager can export the **current** TD state to CSS, which is useful for capturing a hand-tuned theme or starting from TD defaults:

```python
# Export current ui.colors + TUIK2 params to a CSS file
op.ATM.SaveTheme('/path/to/captured.css', name='Captured State')

# Export TD's factory defaults
op.ATM.ExportDefault()  # writes to themes/td-default.css
```

`SaveTheme()` includes TUIK2 RGBA parameters by default; pass `include_tuik2=False` to skip them and emit only `ui.colors`.

## Optional: write TouchColors

The manager can also write a `TouchColors` file alongside `project.folder` that mirrors the current `ui.colors` state, formatted to match TD's install-dir `TouchColors`. The user can then manually copy it to TD's install Config dir so future TD launches start themed — avoids per-attribute `ui.colors` writes on every project start.

Enable the `Writetouchcolors` toggle on the AcroThemeManager component, or call:

```python
op.ATM.WriteTouchColorsFile()
```

A one-shot backup of the original install TouchColors is written to `project.folder/TouchColors.original` the first time, so the truly original bytes are preserved across repeated theme writes.
