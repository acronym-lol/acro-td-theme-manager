---
last_reviewed: 2026-08-27
sidebar_position: 6
---

# Themes Library

Every theme that ships in `themes/`. All listed themes derive from `td-base-template.css` unless marked as legacy or standalone.

## System / template

| File | Description |
|------|-------------|
| `td-default.css` | Raw TD defaults (flat hex, no variables). Reference / debugging only. |
| `td-default-variables.css` | TD defaults reorganized with CSS variables. |
| `td-base-template.css` | Template for creating new themes (palette system). |
| `debug.css` | Every color randomized for UI element identification — see [creating-themes#debug](creating-themes#debug-which-selector-controls-this-ui-element). |

## Popular code-editor themes

Adapted from common code-editor palettes.

| File | Description |
|------|-------------|
| `dracula.css` | Dracula — purple bg, pink / green / yellow / orange accents |
| `gruvbox.css` | Gruvbox — warm earthy retro groove |
| `tokyo-night.css` | Tokyo Night — deep blue-purple, vibrant balanced accents |
| `monokai.css` | Monokai — classic Sublime Text, warm olive bg, hot pink / green |
| `nord.css` | Nord — arctic blue, cool Polar Night / Snow Storm / Frost / Aurora |
| `solarized-dark.css` | Solarized Dark — scientific teal-tinted palette |
| `one-dark.css` | One Dark — Atom editor default, muted professional |
| `everforest.css` | Everforest — green-based, warm and soft |
| `rose-pine.css` | Rosé Pine — deep purple, gold / pink / foam accents |
| `kanagawa.css` | Kanagawa — Japanese ink-wash, inspired by Hokusai |

## Catppuccin family

| File | Description |
|------|-------------|
| `catppuccin-mocha.css` | Mocha — darkest, pastel accents |
| `catppuccin-macchiato.css` | Macchiato — darker |
| `catppuccin-frappe.css` | Frappé — medium dark |
| `catppuccin-latte.css` | Latte — light (softened); reference light-theme implementation |

## Brand themes

| File | Description |
|------|-------------|
| `acronym-dark2.css` | Acronym brand dark — warm core, marigold accents |
| `acronym-light2.css` | Acronym brand light — warm stone, softened; reference light-theme implementation |

## Specialty / creative

| File | Description |
|------|-------------|
| `rainbow.css` | Rainbow — neon rainbow overdose, rainbow gray ramp |
| `catnap.css` | Catnap — cat-vision blues / greens / grays, twilight palette |
| `darkroom.css` | Darkroom — red-only night vision, preserves dark adaptation (see [Monochrome themes](creating-themes#monochrome-themes)) |
| `terminal.css` | Terminal — green phosphor CRT (VT100 / Apple II) |
| `amber.css` | Amber — amber phosphor CRT (IBM 3270) |
| `banana.css` | Banana — banana-themed, ripeness gradient CHOP bars |
| `abyss.css` | Abyss — deep ocean bioluminescence |
| `synthwave.css` | Synthwave — 80s retrowave neon, hot pink / electric blue |
| `bubblegum.css` | Bubblegum — aggressively, relentlessly pink |
| `retro-chrome.css` | Retro Chrome — late-90s desktop OS, silver chrome / navy / teal |
| `high-vis.css` | High Vis — accessibility / WCAG AAA, colorblind-friendly |

## Legacy

Earlier (pre-base-template) themes. They still work but may differ visually from their modern equivalents.

| File | Replaced by |
|------|-------------|
| `acronym-dark.css` | `acronym-dark2.css` |
| `acronym-light.css` | `acronym-light2.css` |
| `dark-gold.css` | (standalone — no replacement) |
| `light-mode.css` | (standalone — no replacement) |
