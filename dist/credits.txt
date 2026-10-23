# Ember Gate — production and source notes

A fictional early-Ming-inspired stronghold for Last Bastion, set in China around 1400. This is the wall environment build, before zombie waves and the upgrade economy. Geometry, dimensions, layout, and defenses are game design choices, not a measured reconstruction of a real monument.

## Architectural references
- Nanjing City Wall Protection and Management Center, official History page: https://english.njcitywall.cn/?obj=lishi — construction 1366–1393; masonry gate arches, barbican arrangements and the moat system.
- State Administration of Cultural Heritage submission, UNESCO World Heritage Centre Tentative List, “City Walls of the Ming and Qing Dynasties”: https://whc.unesco.org/en/tentativelists/5324 — Nanjing early Ming brick construction and the different restoration histories of Chinese city walls. This is a tentative-list submission, not a World Heritage inscription.
- The modern appearance of Xi'an's walls was deliberately not treated as a precise 1400 reference: the cited submission dates the addition of its brick facing to 1568, with further major changes in 1781.
- Official Nanjing reference photos were consulted through the linked history page. They are not bundled or redistributed.

## Material assets actually used
All material texture maps below are CC0 per https://polyhaven.com/license. Source photography by Rob Tuytel, distributed by Poly Haven. Original diffuse and roughness maps are used in the renderer, with color adjustments and bump shading. No Poly Haven website preview renders or logos are republished.
- Castle Brick 01: https://polyhaven.com/a/castle_brick_01 — weathered masonry, desaturated and tinted for the wall; varied scale for stone footings. This is a general masonry surface asset, not a scan of a Chinese monument.
- Cobblestone Floor 04: https://polyhaven.com/a/cobblestone_floor_04 — paving for the approach, wall walk and courtyard.
- Wood Planks Dirt: https://polyhaven.com/a/wood_planks_dirt — doors, bridge, woodwork and supplies.

## Original scene
`art/build_scene.py` constructs original geometry in Blender 4.3.2: battered wall faces, physical crenellations, a vaulted stone gate arch, individual oak door planks and iron fittings, watchtowers, layered timber brackets, lattice windows, curved hip roofs and individual barrel-tile courses, banner cloth folds, braziers, moat bridge, barricades, crates, plants and stones. No third-party mesh was imported. The small gate plaque bears abstract decorative marks, not a claimed historical inscription.

Cycles CPU path tracing provides the static scene lighting, material response and shadows. The renderer projects inspection points and brazier locations into `scene-map.json`, keeping interaction coordinates attached to the modeled scene. The two gate states are separately rendered; the web viewer crossfades them. The web scene is 2.5D, with pan/zoom, inspection, ember glow, optional rain, a night grade and synthesized ambient audio. It is not a freely orbitable 3D scene. The night toggle is a color/brightness grade with extra fire glow, not a new historical lighting reconstruction.

Rebuild the source scene: `blender -b -t 8 --python art/build_scene.py -- --draft`. Finalize and render production states: `blender -b art/ember-gate.blend -t 8 --python art/render_final.py`. The finalizer validates the arch opening and door transforms, recalculates cube normals, and adds broad masonry water stains. Final web assets are WebP conversions of the rendered RGBA PNGs. `art/ember-gate.blend` is a reproducible intermediate, not required to serve the site.

UI font: Barlow Condensed, Jeremy Tribby, SIL Open Font License; https://github.com/google/fonts/tree/main/ofl/barlowcondensed. Georgia/Times are system fallbacks for editorial headings.

The earlier industrial AI-generated concept images are superseded and are not part of this deployed environment.
