---
last_reviewed: 2026-08-27
sidebar_position: 4
---

# Protected Colors & UI Mappings

Two categories of TD colors are **hue-protected** — change their value or saturation but not their hue, because users rely on the hue to read the UI at a glance.

## Operator family colors

Every TouchDesigner operator family has a signature hue. Changing the hue makes ops harder to identify — don't.

| Family | Hue | Notes |
|--------|-----|-------|
| CHOP | Green | |
| DAT | Magenta | |
| MAT | Yellow | |
| POP | Blue | New family — see [Creating & Debugging Themes](creating-themes#operator-family-mappings) |
| SOP | Blue | |
| TOP | Purple | |
| **COMP** | **Neutral gray (exception)** | See below |

Value (brightness) and saturation adjustments are fine — they let the family hues blend with the theme.

### Exception: COMP is neutral gray

COMP has no meaningful hue. COMPs are the most common container type and their color is the **most visible background in the parameter panel header**. Map `--op-comp` to `var(--palette-bg-surface)` so it blends with the theme instead of fighting it.

This is non-obvious — it was discovered by debugging. The COMP family color controls the header bar at the top of the parameter window showing the op name/type. If you tint it, every parameter panel suddenly screams that color.

## Parameter mode colors

Users read parameter binding state from these hues. Don't change them.

| Mode | Hue |
|------|-----|
| Expression | Cyan / teal |
| Override | Green |
| Bind / Export | Purple |
| Constant | Default gray |

Brightness can shift to fit the theme; hue cannot.

---

## Non-obvious UI element → selector mappings

Some TD UI elements aren't obvious from their selector names. Use this table to find the selector for what you're trying to recolor.

| What you see | Selector | Notes |
|--------------|----------|-------|
| Parameter panel header (op name / type bar) | `COMP { color: ... }` | Uses op family color, NOT a dedicated header variable |
| Parameter gadget background | `TUIK2.gadget_bg` | Best as `var(--palette-bg-surface)`, alpha not needed |
| Parameter header strip (? icons row) | `TUIK2.header_bg` | Best as `var(--palette-bg-raised)` |
| Network editor background | `worksheet.bg` | References `--network-bg` |
| Code editor background | `dat.bg.editable` | References `--dat-bg` |
| Playbar strip | `playbar.bg` | References `--playbar-bg` |
| Titlebar (floating windows) | `TUIK2.titlebar_*` | Darken from `--palette-accent-alt` to avoid being too bright |
| Active / pressed buttons | `TUIK2.button_on` | Best as `darken(var(--palette-accent), 0.15)` |
| Timecode / root time display | `TUIK2.root_time` | Darken from `--palette-accent-alt` |

## Known too-bright traps

These TUIK2 surfaces consistently come out too bright if mapped directly from accent variables. Always run them through `darken()`:

| Surface | Recommended treatment |
|---------|----------------------|
| `TUIK2.titlebar_*` | `darken(var(--palette-accent-alt), 0.15–0.25)` |
| `TUIK2.root_time` | `darken(var(--palette-accent-alt), 0.15–0.25)` |
| `TUIK2.button_on` | `darken(var(--palette-accent), 0.15)` |
| `TUIK2.knobindicator_*` | `darken(...)` when the result pops harder than the rest of the UI |

## Light theme gotcha

Light themes need:

- **Inverted gray ramp** — `--gray-00` is dark, `--gray-09` is light
- **Dark DAT editors anyway** — code editors stay dark with hardcoded values, not `var(--palette-bg)`
- **Darker op-family colors** for readability on light backgrounds
- **Dark text** — `--palette-fg` should be dark, `--palette-fg-bright` even darker

See `acronym-light2.css` and `catppuccin-latte.css` for reference implementations.
