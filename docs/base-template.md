---
last_reviewed: 2026-08-27
---

# Base Template & Core Palette

`themes/td-base-template.css` is the canonical starting point for new themes. It declares ~20 "core palette" variables that cascade — via `var()` / `lighten()` / `darken()` — into every TD UI surface. The other ~700 individual selectors derive from those 20 values.

To create a new theme:

1. Copy `td-base-template.css` and rename it.
2. Change the `SECTION 1: CORE PALETTE` variables (~20 values).
3. Adjust the gray ramp in `SECTION 2` to match your palette's tint.
4. Update secondary syntax colors (GLSL, TScript, XML, YAML) if desired.
5. Update CHOP bar colors, jive / textport / splitpane accents.
6. Protected sections (op families, parameter modes) cascade automatically — don't change hues there.

## Core palette variables

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
| `--palette-tuik-accent` | TUIK2 button accent (TD default orange `#BF8148`) |
| `--palette-border` | Default border / outline |
| `--palette-keyword` | Syntax: keywords |
| `--palette-function` | Syntax: function names |
| `--palette-string` | Syntax: string literals |
| `--palette-number` | Syntax: numeric literals |
| `--palette-comment` | Syntax: comments |
| `--palette-error` | Errors, critical alerts |
| `--palette-warning` | Warnings |
| `--palette-success` | Success, play state |
| `--palette-info` | Information, links |

## Gray ramp (`SECTION 2`)

A 10-step gray ramp from `--gray-00` (lightest) → `--gray-09` (darkest). Used wherever the palette needs intermediate tones without committing to a specific accent.

For **dark themes**: `--gray-00` is your white, `--gray-09` is your black (default direction).

For **light themes**: invert — `--gray-00` is the deepest dark, `--gray-09` is paper-white. See [Creating & Debugging Themes](creating-themes#light-themes) for details.

## Cascade direction

Selectors should read from the palette via `var()`, not from hex literals. This means a theme can be retuned by editing the 20-ish palette values rather than walking the file.

```css
/* good — derives from palette */
dat.bg.editable     { color: var(--palette-bg); }
dat.bg.hilite       { color: var(--palette-bg-highlight); }

/* bad — hard-coded; won't follow palette tweaks */
dat.bg.editable     { color: #1a1a1a; }
dat.bg.hilite       { color: #2a2a2a; }
```

Hardcoded literals are appropriate **only** for hue-protected surfaces (op families, parameter mode indicators) — see [Protected Colors](protected-colors).
