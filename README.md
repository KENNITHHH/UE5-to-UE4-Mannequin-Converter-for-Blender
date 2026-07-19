# UE5 Mannequin → UE4 Skeleton Converter (Blender scripts)

UE5's mannequin isn't a renamed UE4 mannequin — it's built on a bigger
skeleton (~89 bones vs UE4's ~68) with extra corrective/twist bones for
smoother deformation.

## Requirements
- Blender 3.x or 4.x (free)
- Your UE5 mannequin as an FBX (export it from your UE5 project)

## Steps

1. **Import the source mesh.**
   Blender → File → Import → FBX → your UE5 mannequin file.

2. **Save a backup** of your .blend file (this is mandatory, this can be anywhere).

4. **Run the converter.**
   Open `Convert_UE5_to_UE4.py`, check `OUTPUT_PATH` at the top, Run Script.
   It will:
   - merge every non-standard bone's skin weight into its nearest UE4-standard
     parent bone,
   - delete those non-standard bones,
   - export `UE4_compatible_mannequin.fbx` next to your .blend file.

5. **Import into UE4.**
   Import the exported FBX. On the import dialog, set **Skeleton** to your
   project's existing `SK_Mannequin` asset (so it shares the skeleton with
   all your other UE4 content), or leave it blank to create a fresh
   UE4-compatible skeleton asset.
   
   **For Pavlov VR users : "Content\MovementAnimsetPro\UE4_Mannequin\Mesh\UE4_Mannequin_Skeleton"**

## Limitations, honestly

- The `KEEP_BONES` list here matches the long-standing, well documented UE4
  `SK_Mannequin` bone set. If your specific UE5 export uses different naming
  for some core bone, the diagnostic script in step 2 will catch it — fix
  `KEEP_BONES` before running the converter, not after.
- Vertex weight merging here is a straightforward additive merge, which is
  the standard "collapse a corrective bone into its parent" approach, but
  it isn't a substitute for a human eyeballing the result on tricky meshes
  (breast/cloth correctives, if present, are the most likely to need a
  manual touch-up).
- This isn't PERFECT but it is usable.
