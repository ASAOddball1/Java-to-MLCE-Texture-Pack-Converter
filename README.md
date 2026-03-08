# Java-to-MLCE Texture Pack Converter

A desktop GUI tool for converting modern **Java Edition texture packs** into the sprite sheet format used by **Minecraft: Legacy Console Edition (MLCE)**. Instead of manually stitching hundreds of individual PNGs into a single atlas, this tool maps each texture to its correct position automatically and exports a ready-to-use sprite sheet at your chosen resolution.

---

## Features

- **Three sprite sheet targets** — Terrain, Items, and Particles, each with their own tab and layout
- **Auto-Sync** — Point the tool at any Java texture pack folder and it will automatically match every PNG it finds to the correct slot by filename
- **Manual override** — Double-click any entry in the list to hand-pick a specific PNG for that slot
- **Live preview** — Click any mapped entry to instantly preview the texture it will place
- **Multi-resolution output** — Build at **16×**, **32×**, or **64×** with one click; all coordinates scale automatically
- **Terrain mip maps** — Automatically generates `terrainMipMapLevel2.png` (½ size) and `terrainMipMapLevel3.png` (¼ size) alongside the main terrain sheet
- **Animated texture support** — Strips animated textures down to their first frame automatically so nothing breaks in the atlas
- **Search / filter** — Filter any tab's entry list in real time by name
- **Bundled MLCE-exclusive textures** — Several textures that exist only in Legacy Console Edition and have no Java equivalent are included in the repo ready to use

---

## Sprite Sheet Layouts

| Sheet | Grid | 16× size | 32× size | 64× size |
|---|---|---|---|---|
| `terrain.png` | 16 × 32 tiles | 256 × 512 px | 512 × 1024 px | 1024 × 2048 px |
| `items.png` | 16 × 16 tiles | 256 × 256 px | 512 × 512 px | 1024 × 1024 px |
| `particles.png` | 8 × 8 tiles | 128 × 128 px | 256 × 256 px | 512 × 512 px |

---

## JSON Mapping Files

Each sprite sheet is driven by a `.json` file that defines where every tile lives on the atlas. The repo includes pre-built mapping files for the default MLCE layout.

### Format

```json
[
  {
    "Name": "grass_block_top",
    "DisplayName": "Grass Top",
    "X": 0,
    "Y": 0
  },
  {
    "Name": "stone",
    "DisplayName": "Stone",
    "X": 16,
    "Y": 0
  }
]
```

| Field | Description |
|---|---|
| `Name` | Exact filename of the source PNG without extension. Must match a file in your texture pack or the bundled exclusives folder. |
| `DisplayName` | Human-readable label shown in the UI. |
| `X` / `Y` | Position on the sprite sheet in **16× pixel space**. The tool converts these to the correct output coordinates at build time regardless of chosen resolution. |

---

## MLCE-Exclusive Textures

Legacy Console Edition contains a number of textures that were either removed from Java before the texture pack era or never existed in Java at all. These are bundled in the repo so your converted pack is complete without needing to source them manually.

| File | Description |
|---|---|
| `ruby.png` | Ruby — cut item that was replaced by emerald in Java |
| `quiver.png` | Quiver — cut item that never shipped in Java |
| `inventory_overlay.png` | Inventory slot overlay used in MLCE UI |
| `armour_head.png` | Armour UI overlay — helmet slot |
| `armour_chest.png` | Armour UI overlay — chestplate slot |
| `armour_leg.png` | Armour UI overlay — leggings slot |
| `armour_boots.png` | Armour UI overlay — boots slot |
| `spawn_egg_particle.png` | Spawn egg particle texture exclusive to MLCE |
| `firetex.png` | MLCE fire texture variant |
| `lava_flow.png` | MLCE lava flow texture variant |
| `Purple_tex.png` | Purple/chorus-related texture exclusive to MLCE |
| `brown_thing.png` | MLCE-exclusive brown UI element |
| `brown_thing_2.png` | MLCE-exclusive brown UI element variant 2 |
| `brown_thing_3.png` | MLCE-exclusive brown UI element variant 3 |

When you run Auto-Sync, add the folder containing these files as part of your library and they will be matched automatically.

---

## Known Limitations

### Particles Sheet
The particles JSON mapping file is **not yet available**. The Particles tab is present in the tool but cannot be used to generate a sheet until the mapping file is added in a future update.

### Bed Textures
Bed textures **do not convert automatically** and will need to be handled manually. Modern Java Edition resource packs store bed textures as full 3D model skin sheets (e.g. `red_bed.png`, `white_bed.png`) split across the head and foot of the bed as separate files. MLCE instead expects each bed face — top, side, and end for both the head and foot sections — as individual 16×16 tiles placed directly on the items sheet.

Because the layouts are fundamentally different, Auto-Sync cannot extract and remap these correctly from a Java pack. You will need to either:
- **Create your own** bed face tiles manually by cropping and adapting the faces from your Java pack's bed texture
- **Find pre-made** MLCE-format bed tiles that match your pack's style

This is a known issue and proper automatic bed conversion is planned for a future update.

---

## Requirements

- Python 3.9+
- Pillow

```bash
pip install pillow
```

---

## Running the Tool

```bash
python MLCE_Converter.py
```

---

## How to Use

### Step 1 — Select your library
Click **SELECT LIBRARY** and browse to the root folder of a Java Edition texture pack (or any folder containing `.png` files). The tool walks all subfolders automatically. To include the bundled MLCE-exclusive textures, point it at the root of this repo or a folder that contains them alongside your pack files.

### Step 2 — Load a JSON
Click **TERRAIN JSON**, **ITEMS JSON**, or **PARTICLES JSON** and select the corresponding mapping file from this repo. The entry list will populate immediately.

### Step 3 — Map your textures
Click **AUTO-SYNC FROM LIBRARY** on the active tab. The tool scans your library, matches every PNG whose filename equals a `Name` value in the JSON, and fills in all matching slots. A summary dialog tells you how many entries were matched.

For any slot that wasn't matched automatically, double-click the row and browse to the correct PNG manually.

### Step 4 — Choose a resolution
Select **16×**, **32×**, or **64×** from the buttons in the top bar. This controls the size of each tile in the output sheet.

### Step 5 — Build
Click **BUILD ASSETS**. The output PNG is saved to the same folder as the JSON file you loaded. For terrain builds, the two mip map levels are saved there as well.

---

## Repository Contents

| File | Description |
|---|---|
| `MLCE_Converter.py` | Main application source |
| `terrain.json` | MLCE terrain sprite sheet mapping |
| `items.json` | MLCE items sprite sheet mapping |
| `ruby.png` | Bundled MLCE-exclusive texture |
| `quiver.png` | Bundled MLCE-exclusive texture |
| `inventory_overlay.png` | Bundled MLCE-exclusive texture |
| `armour_head.png` | Bundled MLCE-exclusive texture |
| `armour_chest.png` | Bundled MLCE-exclusive texture |
| `armour_leg.png` | Bundled MLCE-exclusive texture |
| `armour_boots.png` | Bundled MLCE-exclusive texture |
| `spawn_egg_particle.png` | Bundled MLCE-exclusive texture |
| `firetex.png` | Bundled MLCE-exclusive texture |
| `lava_flow.png` | Bundled MLCE-exclusive texture |
| `Purple_tex.png` | Bundled MLCE-exclusive texture |
| `brown_thing.png` | Bundled MLCE-exclusive texture |
| `brown_thing_2.png` | Bundled MLCE-exclusive texture |
| `brown_thing_3.png` | Bundled MLCE-exclusive texture |
