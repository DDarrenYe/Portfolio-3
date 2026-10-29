# Castle Hill

An interactive fantasy-RPG portfolio. The page is a round, tightly packed toon-shaded town
on a turntable, with a castle on a hill in the middle and chibi NPCs around it. Each NPC
will open a section of the portfolio. Move the mouse toward either edge of the screen and
the town turns that way.

**Status:** blockout. The castle, landmarks and filler houses are grey placeholders at their
final sizes. One finished house and the shopkeeper show the target style.

## Run it

```bash
npm install
npm run dev
```

Review a single asset up close with `?look=house_showcase` or `?look=spot_shopkeeper`.

## How it's built

- **Site:** Vite, React, TypeScript, Three.js through React Three Fiber.
- **Look:** every Blender material is a flat colour named `pal_<name>`. The site swaps each
  one for a three-band toon material and adds an ink outline of constant on-screen width
  (`src/scene/toon.ts`). Lighting and outlines live in code, not in Blender.
- **Rotation:** `src/hooks/useEdgeRotation.ts`. The mouse sets the turning speed: still in the
  middle 30% of the screen, up to 0.6 rad/s at the edges. Touch drag and arrow keys work too.
- **Models:** built by Python scripts in `art/scripts/` and exported to `public/models/`.
  The `.blend` files in `art/` are saved alongside, so you can open and tweak them in Blender.

## Rebuild the models

```bash
BLENDER=/path/to/blender npm run models
```

Model conventions (see `art/scripts/lib.py`): 1 Blender unit = 1 town unit, the front of the
town faces −Y, origins sit at each object's base, and empties named `spot_<npc>` mark where
each NPC stands.

## Deploy

Pushes to `main` build and deploy to GitHub Pages (`.github/workflows/deploy.yml`). In the
repo's **Settings → Pages**, set the source to **GitHub Actions** once.
