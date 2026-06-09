# CSS Format & Parser

Themes are written as standard CSS with a few targeted extensions. `ThemeCSSParser` (`scripts/ThemeCSSParser.py`) resolves the file into a flat `{selector: [r, g, b, a]}` dict that `AcroThemeManager` distributes to TD.

## File structure

A theme is two sections:

1. **`:root { ... }` block** — CSS variable definitions. This is your palette.
2. **Selector rules** — Map TD's internal color names to variables via `color:`.

```css
:root {
    --bg-dark: #1a1a1a;
    --text-primary: hsl(54, 100%, 50%);
}

dat.bg.editable     { color: var(--bg-dark); }
dat.bg.hilite       { color: lighten(var(--bg-dark), 0.1); }
TUIK2.button_off    { color: rgba(0.4, 0.4, 0.4, 1.0); }
op.AW.par.Wcbg      { color: var(--bg-dark); }
```

## Color formats

| Form | Example | Notes |
|------|---------|-------|
| Hex 6-digit | `#FF5500` | |
| Hex 3-digit | `#F50` | Expanded to `#FF5500` |
| HSL | `hsl(180, 50%, 50%)` | Hue 0–360, saturation/lightness 0–100% |
| RGB 0–255 | `rgb(128, 128, 128)` | |
| RGBA 0–255 | `rgba(128, 128, 128, 0.8)` | Alpha 0–1 |
| Float tuple (RGB) | `0.5 0.5 0.5` | Legacy form, still supported |
| Float tuple (RGBA) | `0.5 0.5 0.5 0.8` | Legacy form with alpha |

## Functions

| Function | Behavior |
|----------|----------|
| `var(--name)` | Look up a CSS variable. Resolution is recursive — variables can reference other variables. |
| `lighten(color, amount)` | Increase HSV value by `amount` (0.0–1.0). |
| `darken(color, amount)` | Decrease HSV value by `amount` (0.0–1.0). |

`var()` is allowed inside `lighten()` / `darken()`, so chains like `darken(var(--accent), 0.15)` work as expected.

## NOT supported

- `calc()` or any arithmetic
- Chaining functions: `lighten(darken(...), ...)` doesn't resolve — the inner result isn't fed back through the parser
- Negative amounts — use `darken()` instead of `lighten(..., -0.1)`
- Extracting channels from `var()` to compose into `rgba()` — e.g. `rgba(var(--color), 0.5)` won't work because `var(--color)` returns a single resolved value, not three RGB channels

## Selector naming

The parser groups parsed colors into three buckets based on selector pattern:

| Bucket | Pattern | Where it lands |
|--------|---------|----------------|
| `ui.colors` | `category.element.state` | `ui.colors['category.element.state']` |
| `TUIK2` | `TUIK2.element_state` | RGBA params on the AcroThemeManager component |
| `op.*` | `op.SHORTCUT.par.Parname` | Custom params on the comp at `op.SHORTCUT` |

### Examples

```css
/* ui.colors — most TD UI */
dat.bg.editable        { color: var(--dat-bg); }
parms.button.bg.loc    { color: var(--button-bg); }
worksheet.bg           { color: var(--network-bg); }

/* TUIK2 — widget library colors */
TUIK2.button_off       { color: var(--button-off); }
TUIK2.button_on        { color: darken(var(--accent), 0.15); }
TUIK2.gadget_bg        { color: var(--palette-bg-surface); }

/* op.* — custom-component params */
op.AW.par.Wcbg         { color: var(--bg-dark); }
op.AM.par.Macrolistbg  { color: var(--palette-bg-surface); }
```

### TUIK2 operator selectors — case sensitive

The TUIK2 operator-family selectors use **UPPERCASE** family names:

```css
TUIK2.operator_CHOP    /* ✓ */
TUIK2.operator_chop    /* ✗ won't match */
TUIK2.operator_COMP
TUIK2.operator_DAT
TUIK2.operator_TOP
TUIK2.operator_SOP
TUIK2.operator_MAT
TUIK2.operator_POP
```

## Alpha handling

- **`ui.colors`** — TD core ignores alpha. The parser strips it before pushing.
- **`TUIK2.*`** — Alpha is preserved. TUIK2 params are RGBA.
- **`op.*`** — Alpha is preserved. Each op shortcut param is RGBA on the target comp.

## Diff-on-reload

`AcroThemeManager.OnThemeChange()` compares the newly parsed colors against the cached previous values and only re-pushes the changed entries. This makes reloading the active theme very cheap, and live-editing a CSS file (sync DAT picks up the change) feels instant.
