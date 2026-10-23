# Last Bastion — Ember Gate

A buildless, responsive 2.5D wall viewer for an early-Ming-inspired zombie defense game. Deployable assets live in `dist/`. No API keys, external runtime services or WebGL are needed.

Controls: drag to pan; scroll or pinch to zoom; E toggles gates; I toggles inspection points; H clean view; R resets; N dusk/night; W rain. All primary functions also have visible buttons. Art & sources includes the historical references and links to the CC0 materials actually used.

See `art/production-notes.md` for sources and reconstruction details. `art/build_scene.py` is the deterministic Blender scene builder. This build establishes the environment; waves, combat, and the upgrade economy are not implemented.
