##Get it on Gumroad instead !
![Get it on Gumroad instead!](https://kennithh.gumroad.com/l/UE5-to-UE4-Mannequin-Converter-for-Blender)

![ue5toue4](https://github.com/user-attachments/assets/d7b4d971-662d-494d-9c72-8be4ee05a99b)
# UE5 Mannequin → UE4 Skeleton Converter (Blender scripts)

A Blender script that rebuilds a UE5 mannequin's skeleton to match UE4's standard bone hierarchy — removing UE5's extra corrective/twist bones and merging their skin weight back into the parent bones — so the mesh imports and skins correctly against UE4's SK_Mannequin.
UE5's mannequin isn't a renamed UE4 mannequin — it's built on a bigger
skeleton (~89 bones vs UE4's ~68) with extra corrective/twist bones for
smoother deformation.

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)
## Requirements
- Blender 5 (might work with older, did not test)
- Your UE5 mannequin as an FBX (export it from your UE5 project)

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)
## Steps

1. **Import the source mesh.**
   Blender → File → Import → FBX → your UE5 mannequin file.

2. **Save a backup** of your .blend file (this is mandatory, this can be anywhere).

4. **Run the converter.**

   Scripting -> Open -> `Convert_UE5_to_UE4.py`.
   Check `OUTPUT_PATH` at the top if needed, if not changed it's relative to the .blend file, Run Script.
   It will:
   - merge every non-standard bone's skin weight into its nearest UE4-standard
     parent bone,
   - delete those non-standard bones,
   - export `UE4_compatible_mannequin.fbx` next to your .blend file.

6. **Import into UE4.**
   Import the exported FBX. On the import dialog, set **Skeleton** to your
   project's existing `SK_Mannequin` asset (so it shares the skeleton with
   all your other UE4 content), or leave it blank to create a fresh
   UE4-compatible skeleton asset.
   
   **For Pavlov VR users : "Content\MovementAnimsetPro\UE4_Mannequin\Mesh\UE4_Mannequin_Skeleton"**

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)
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

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)
## Appreciation

[If you appreciate this script and you would like to buy me a coffee☕ PAYPAL.ME](https://paypal.me/KENNITHHH)
