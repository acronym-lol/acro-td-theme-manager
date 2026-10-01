---
last_reviewed: 2026-08-27
sidebar_label: 'API Reference'
---

# AcroThemeManager — UI Theming

## Overview

`AcroThemeManager` applies CSS-based themes to TouchDesigner's UI. It provides a single source of truth for color across three different theming surfaces:

1. **`ui.colors`** — TD's built-in keyed color table for the network editor, parameter dialog, code editors, etc.
2. **TUIK2 widget colors** — the parameterized color palette used by the bundled UIK2 widget library at `/ui/lib/TUIK2`.
3. **Component shortcut params** — RGBA parameters on any component reachable through an `op.SHORTCUT` global, allowing themes to skin custom UIs.

Themes are written as CSS files. A custom parser (`ThemeCSSParser`) resolves variables, lighten/darken modifiers, and mixed color formats. The manager component lives at `/AcroThemeManager` and is exposed as `op.ATM`. It inherits from `CallbacksExt` and `AcroVersionExt`, so it carries the standard Component / Version pages.

---

## Architecture

```
themes/<name>.css → ThemeCSSParser → resolved RGBA dict
                                       │
                  ┌────────────────────┼─────────────────────┐
                  ▼                    ▼                     ▼
            ui.colors[*]      ThemeManager.par.*       op.SHORTCUT.par.*
            (RGB only)         (RGBA TUIK2 pars)        (RGBA op pars)
```

- The active theme is whichever CSS file is loaded into the manager's `theme` TextDAT (`Themefile` parameter).
- A DAT Execute on the `theme` DAT calls `OnThemeChange` whenever the file content changes.
- Each call diffs the new colors against the previously-applied set so that only changed values are written.

---

## Parameters

### Theme Page

| Parameter | Type | Description |
|-----------|------|-------------|
| `Themefile` | `file` | Path to the active CSS theme file. The `theme` DAT loads this file and triggers `OnThemeChange`. |
| `Loadonstart` | `toggle` | If on, the manager re-applies the active theme during `onStart` — guarantees `ui.colors` reflects the theme even if the file was edited externally. |
| `Fixuionstart` | `toggle` | If on, runs the bundled set of TD UI fix-ups during `onStart` (bookmark buttons, time attributes, hashrow, transport, rangebar, FPS display). These rebuild parts of TD's stock UI that don't honor `ui.colors` cleanly. |
| `Loadtheme` | `pulse` | Force-reload the theme from disk and re-apply all colors, bypassing the diff cache. |
| `Savetheme` | `pulse` | Export current `ui.colors` and TUIK2 parameter values back out to the configured `Themefile`. |
| `Exportdefault` | `pulse` | Reset `ui.colors` to TD defaults and write them to `themes/td-default.css`. |
| `Resettodefaults` | `pulse` | Reset all `ui.colors` and TUIK2 parameters to TD defaults without touching the theme file. |

### TUIK2 Page

The TUIK2 page is built procedurally by `_ensureTUIK2Page()` — one section header per widget category, plus an RGBA parameter for every TUIK2 color slot. Defaults are pulled from the live TUIK2 color comp at `/ui/lib/TUIK2/colors/color`.

The full set of color slots is grouped into the following sections:

| Section | Colors |
|---------|--------|
| **Button** | `button_border_disable`, `button_bordera`, `button_borderb`, `button_disable`, `button_off`, `button_offroll`, `button_on`, `button_onroll`, `buttontext_disable`, `buttontext_off`, `buttontext_offroll`, `buttontext_on`, `buttontext_onroll` |
| **Checkbox** | `checkbox_border`, `checkbox_border_disable` |
| **Field** | `field_disable`, `field_on`, `field_onroll` |
| **Gadget** | `gadget_bg`, `gadget_bordera`, `gadget_borderb` |
| **Header** | `header_bg`, `header_bordera` |
| **Indicator** | `indicator_disable`, `indicator_off`, `indicator_roll` |
| **Knob** | `knob_disable`, `knob_off`, `knob_roll`, `knobindicator_disable`, `knobindicator_off`, `knobindicator_roll` |
| **Label** | `label_text`, `label_text_disable` |
| **Operator** | `operator_CHOP`, `operator_COMP`, `operator_DAT`, `operator_MAT`, `operator_SOP`, `operator_TOP` (plus `*filter` and `*generator` variants, and `operator_COMPvoid`) |
| **Slider** | `slider_bg_disable`, `slider_bg_on`, `slider_bg_onroll`, `slider_range_off` |
| **Template** | `template_bordera`, `template_borderb`, `template_off`, `template_offroll`, `template_on`, `template_onroll` |
| **Titlebar** | `titlebar_bordera`, `titlebar_off`, `titlebar_on`, `titlebar_text_off` |
| **Other** | `root_time`, `transparent` |

Each TUIK2 color slot creates four parameters with suffixes `r`, `g`, `b`, `a`. Parameter names follow the convention `Buttonoff` (the slot name with underscores stripped and only the first letter capitalized). The naming convention is implemented by the `_tuik2_par_name()` helper.

### TouchColors Page

| Parameter | Type | Description |
|-----------|------|-------------|
| `Writetouchcolors` | `toggle` | If on, every theme load also exports a `TouchColors` file to the project folder using current `ui.colors`. The user manually copies this file to TD's `Config/TouchColors` to make the theme apply at the next TD launch. |
| `Updatetouchcolors` | `pulse` | Manually export current `ui.colors` to the project folder's `TouchColors` file. |

---

## CSS Parser Capabilities

`ThemeCSSParser` understands a deliberate subset of CSS, focused on what's useful for theme palettes.

### Supported

- `var(--name)` — CSS variable references, recursively resolved.
- `lighten(color, amount)` — increase HSV value by amount (0.0–1.0).
- `darken(color, amount)` — decrease HSV value by amount (0.0–1.0).
- `var()` inside `lighten()` / `darken()`.
- Color formats: `#RRGGBB`, `#RGB`, `hsl(h, s%, l%)`, `rgb(r, g, b)`, `rgba(r, g, b, a)`, float tuples (`0.5 0.5 0.5`).

### Not Supported

- `calc()` and arithmetic.
- Chained transforms — `lighten(darken(...), ...)` does not work.
- Negative amounts — use `darken()` instead of `lighten(..., -0.1)`.
- Channel extraction from `var()` inside `rgba()` — `rgba(var(--c), 0.5)` will not work.

---

## CSS Theme Structure

A theme file has two sections:

1. **`:root { … }`** — palette variables.
2. **Selector rules** — map TD's internal color names to variables.

### Selector Naming

| Target | Selector example | Notes |
|--------|------------------|-------|
| `ui.colors` keys | `dat.bg.editable { color: var(--dat-bg); }` | Uses TD's dotted color path verbatim. |
| TUIK2 colors | `TUIK2.button_off { color: var(--accent); }` | Lowercased except for op-family names (`TUIK2.operator_CHOP`). |
| Op shortcut params | `op.AW.par.Tabcolor { color: var(--accent); }` | Maps to four parameters: `Tabcolorr`, `Tabcolorg`, `Tabcolorb`, `Tabcolora`. |

Alpha is stripped automatically when writing to `ui.colors` (TD core does not store alpha). It is preserved for TUIK2 and op-shortcut writes.

### Color Application Categories

When `OnThemeChange` runs, parsed colors are split by selector prefix:

| Prefix | Target | Application Method |
|--------|--------|--------------------|
| `TUIK2.*` | TUIK2 widget params on the manager component | `_applyTUIK2Colors` |
| `op.SHORTCUT.par.*` | RGBA parameters on the resolved component shortcut | `_applyOpColors` |
| anything else | `ui.colors[key]` | `_applyAllColors` / `_applyChangedColors` |

Subsequent loads diff against the prior parse so unchanged values aren't re-written, which keeps `ui.colors` writes cheap.

### Omitted Sections Reset

A theme is not required to define every key, but anything the *previous* theme set and the new one omits is restored rather than left in place — otherwise switching themes would silently inherit stale colors from the one before it.

| Category | Restored to |
|----------|-------------|
| `TUIK2.*` | The parameter's own default (seeded from `/ui/lib/TUIK2/colors/color`). |
| `op.SHORTCUT.par.*` | The value in `themes/td-base-template.css`. |

Op shortcut parameters use the base template rather than their own parameter defaults, which are transparent black — resetting to those would black out the widget and macro list UI. This makes the base template the canonical list of themable op keys: it drives both this reset and what `SaveTheme()` exports.

---

## API Reference

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `ThemeDAT` | `DAT` | Reference to the manager's internal `theme` TextDAT. |

### Methods

| Method | Arguments | Returns | Description |
|--------|-----------|---------|-------------|
| `OnThemeChange(dat)` | `dat: DAT` | `None` | Called by the DAT Execute when the theme file content changes. Parses, splits by category, applies, and fires the `onThemeLoaded` callback. |
| `Refresh()` | — | `None` | Force a full re-parse and re-apply. Clears the diff cache so every color is rewritten. |
| `SaveTheme(filepath=None, name='Custom Theme', include_tuik2=True, include_op=True)` | `str?, str, bool, bool` | `None` | Write current `ui.colors` (and optionally the TUIK2 and `op.SHORTCUT` parameters) back out as a CSS file. Defaults to the configured `Themefile`. |
| `ExportDefault()` | — | `None` | Reset `ui.colors` to TD defaults and `op.SHORTCUT` parameters to their base template values, then save them as `themes/td-default.css` under the manager's `Repopath`. |
| `ResetToDefaults()` | — | `None` | Reset `ui.colors` and TUIK2 parameter values to TD defaults, and `op.SHORTCUT` parameters to their base template values. Does not touch the theme file. |
| `WriteTouchColorsFile(ui_colors=None, output_path=None)` | `dict?, str?` | `bool` | Export a `TouchColors` file to the project folder using current (or supplied) `ui.colors`. Preserves the install file's line endings, ordering, and unrelated lines byte-for-byte; only the keys present in `ui_colors` are overridden. Idempotent — writes a one-time `TouchColors.original` backup the first time it runs. |

### Internal Methods

| Method | Description |
|--------|-------------|
| `_ensureTUIK2Page()` | Build (or rebuild) the TUIK2 parameter page. Idempotent — checks for each header and RGBA parameter before creating. |
| `_ensureTouchColorsParams()` | Build the TouchColors page if missing. Idempotent. |
| `_applyAllColors(colors)` | Apply every `ui.colors` key, skipping ones that already match within a 0.01 tolerance. |
| `_applyChangedColors(newColors)` | Apply only `ui.colors` keys whose values differ from the previously-applied set. |
| `_applyTUIK2Colors(colors)` | Write RGBA values to the TUIK2 parameters on the manager. |
| `_applyOpColors(colors)` | Resolve `op.SHORTCUT` and write RGBA values to the named component parameter. Logs and skips if the shortcut or parameter cannot be found. |
| `_colorsMatch(a, b, tolerance=0.01)` | Float-tolerant comparison used by `_applyAllColors`. |
| `cloneColor()` | Clone the manager's internal `color` comp into TD's TUIK2 color comp at `/ui/lib/TUIK2/colors/color`. Called from `onStart`. |

---

## TouchColors File Export

TD's install-dir `Config/TouchColors` file is read at TD launch to seed `ui.colors`. Writing to this file requires admin permission on Windows, so the manager exports a copy to the project folder instead. The user can manually copy it to:

```
C:/Program Files/Derivative/TouchDesigner/Config/TouchColors
```

The first time the manager writes the project copy, it also stashes a verbatim backup of the install file at `{project.folder}/TouchColors.original`. The backup is one-shot — repeated writes never overwrite it, so the truly original bytes are preserved even after multiple theme switches.

The export refuses to write if the resulting line count diverges from the original, guarding against accidental destruction of the file's structure.

---

## TD UI Fix-Ups (`Fixuionstart`)

When `Fixuionstart` is on, `onStart` runs a series of helpers that rewrite parts of TD's stock UI to honor `ui.colors` more cleanly. These are mostly bookmark, timeline, and transport-related fixes:

| Helper | What it touches |
|--------|-----------------|
| `fixBookmarkButtons` | `/ui/dialogs/bookmark_bar` — replaces cell/table defaults with select DATs pointing at the manager's `bookmark/` palette. |
| `fixTimeAttributes` | `/ui/dialogs/timeline/timeattributes` — overrides background alpha and re-routes the color table. |
| `fixTimelineHashrow` | `/ui/dialogs/timeline/newhashrow` — re-maps hash-row defaults to the manager's `timeline/` palette. |
| `fixTransport` | `/ui/dialogs/timeline/transport` — wires frame, timecode, and music code to manager parameters. |
| `fixRangebar` | `/ui/dialogs/timeline/rangebar` — wires the range bar and its handles to manager parameters. |
| `fixFPS` | `/ui/dialogs/mainmenu/fps1` — wires the FPS display borders to manager parameters. |

The fixes are intentionally one-shot — they reach into TD's UI tree and replace operators, so re-running them is wasteful but safe (the destroy-and-create pattern is idempotent in effect).

---

## Custom Callbacks

The manager dispatches the standard `CallbacksExt` lifecycle plus one theme-specific callback. Implement them in the manager's external `Callbackdat`:

| Callback | Info Keys | Purpose |
|----------|-----------|---------|
| `onInit` | `ownerComp` | Fired during extension init. |
| `onStart` | — | Fired by TD's project start hook. The manager runs its UI fix-ups here. |
| `onThemeLoaded` | `ownerComp`, `colors`, `tuik2Colors`, `opColors`, `count` | Fired after every successful `OnThemeChange`. Use this to trigger downstream UI cooks or re-cloning. |

---

## Bundled Themes

The repository's `themes/` folder ships with a curated set of CSS files. They fall into a few groups:

| Group | Examples |
|-------|----------|
| **System / template** | `td-default.css`, `td-default-variables.css`, `td-base-template.css`, `debug.css` |
| **Code editor classics** | `dracula.css`, `gruvbox.css`, `tokyo-night.css`, `monokai.css`, `nord.css`, `solarized-dark.css`, `one-dark.css`, `everforest.css`, `rose-pine.css`, `kanagawa.css` |
| **Catppuccin family** | `catppuccin-mocha.css`, `catppuccin-macchiato.css`, `catppuccin-frappe.css`, `catppuccin-latte.css` |
| **Brand / specialty** | `acronym-dark.css`, `acronym-light.css`, `rainbow.css`, `catnap.css`, `darkroom.css`, `terminal.css`, `amber.css`, `banana.css`, `abyss.css`, `synthwave.css`, `bubblegum.css`, `retro-chrome.css`, `high-vis.css`, `cyberpunk.css` |

The "code editor classics" and "Catppuccin family" themes are independent color interpretations of publicly documented palettes; see [`ATTRIBUTIONS.md`](../ATTRIBUTIONS.md) for credits. They are not affiliated with or endorsed by the original projects.

To author a new theme, copy `td-base-template.css`, change the ~20 core palette variables in the first section, and adjust the gray ramp in the second section. The base template's protected sections (op family colors, parameter mode colors) cascade automatically.

---

## Tag Discovery

Like every `AcroVersionExt` component, the theme manager carries both `tox_managed` and `version_tracking` tags and is discoverable via `root.findChildren(tags=['version_tracking'])`.
