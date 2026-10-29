# Castle Hill

Darren Ye's portfolio, as a fantasy-RPG town. The page is a round, tightly packed toon-shaded
town on a turntable, with a castle on a hill in the middle and chibi NPCs around it. Move the
mouse toward either edge of the screen and the town turns that way. Click a townsperson to talk:

| NPC | Where | Opens |
|---|---|---|
| The King | Castle gate | About |
| Shopkeeper | Market stall | Projects (INBTWN, Pacer, Pentimento) |
| Blacksmith | Smithy | Skills |
| Wizard | Wizard tower | Education |
| Adventurer | Guild hall | Adventures |

The nav buttons under the name open the same conversations, for keyboard and touch users.

## Change the words

Everything the NPCs say and every panel's content lives in `src/content/portfolio.ts`, with
the panel layouts in `src/ui/SectionPanel.tsx`.

## Run it

```bash
npm install
npm run dev
```

Review an NPC up close with `?look=spot_king` (or `spot_shopkeeper`, `spot_blacksmith`,
`spot_wizard`, `spot_adventurer`), or start the town turned with `?turn=90`.

## How it's built

- **Site:** Vite, React, TypeScript, Three.js through React Three Fiber.
- **Look:** every Blender material is a flat colour named `pal_<name>`. The site swaps each
  one for a three-band toon material and adds an ink outline of constant on-screen width
  (`src/scene/toon.ts`). Lighting and outlines live in code, not in Blender.
- **Rotation:** `src/hooks/useEdgeRotation.ts`. The mouse sets the turning speed: still in the
  middle 30% of the screen, up to 0.6 rad/s at the edges. Touch drag and arrow keys work too.
- **Models:** built by Python scripts in `art/scripts/` (`town.py` lays out the town,
  `buildings.py` holds the house and landmark builders, `npcs.py` and `chibi.py` the NPCs) and
  exported to `public/models/`. The `.blend` files in `art/` are saved alongside, so you can open
  and tweak them in Blender. `art/optimize.mjs` joins and quantizes the town for the web
  (about 70k triangles, 2.3 MB).

## Rebuild the models

```bash
BLENDER=/path/to/blender npm run models
```

Model conventions (see `art/scripts/lib.py`): 1 Blender unit = 1 town unit, the front of the
town faces −Y, origins sit at each object's base, empties named `spot_<npc>` mark where
each NPC stands, and `smoke_<name>` marks chimneys.

## Deploy

Pushes to `main` build and deploy to GitHub Pages (`.github/workflows/deploy.yml`). In the
repo's **Settings → Pages**, set the source to **GitHub Actions** once.
