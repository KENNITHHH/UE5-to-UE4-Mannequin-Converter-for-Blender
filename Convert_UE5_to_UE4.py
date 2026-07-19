"""
Convert_UE5_to_UE4.py

Converts an imported UE5 mannequin (Manny/Quinn) armature + mesh so it uses
the standard UE4 mannequin bone hierarchy.

WHAT IT ACTUALLY DOES (important to understand before running):
UE5's mannequin keeps the same core bone names as UE4 (pelvis, spine_01-03,
thigh_l, upperarm_l, etc.) but adds ~20+ extra corrective/twist bones that
don't exist in UE4 (things like upperarm_twist_01_l, thigh_twist_01_l, extra
spine correctives, etc). Renaming alone won't make this UE4-compatible -
those extra bones have to be deleted and whatever skin weight they were
carrying has to be folded back into their nearest UE4-standard parent bone,
or the mesh will visibly cave in / stretch wherever those bones had weight.

This script:
  1. Reads the armature hierarchy and finds the nearest KEEP_BONES ancestor
     for every bone that isn't itself in KEEP_BONES.
  2. For every mesh using this armature, merges each non-standard bone's
     vertex group weights into that ancestor's vertex group (additive),
     then deletes the non-standard vertex group.
  3. Removes the non-standard bones from the armature (Blender automatically
     reparents any remaining children to the removed bone's parent).
  4. Exports the result as an FBX ready to import into a UE4 project.

BEFORE YOU RUN THIS:
  - Save your .blend file / work on a copy. This script mutates the mesh
    and armature.
  - This only rebuilds the SKELETON + skinning. It does not retarget
    existing UE5 animations onto the result - for that you still use UE4's
    Skeletal Mesh retargeting or IK Retargeter, targeting this new mesh's
    skeleton (which will now match UE4's).

HOW TO RUN:
  1. Blender > File > Import > FBX > your UE5 mannequin.
  2. Scripting tab > Open > this file.
  3. Adjust ARMATURE_NAME / OUTPUT_PATH below if needed.
  4. Click "Run Script".
  5. Check the console for a summary, inspect the mesh in Weight Paint mode
     around former twist-bone areas (shoulders, forearms, thighs) before
     trusting the result.
  6. In Unreal, import the exported FBX. On the import dialog, set
     "Skeleton" to your project's existing UE4 SK_Mannequin skeleton asset
     (or leave blank to create a new UE4-compatible skeleton asset).
"""

import bpy

ARMATURE_NAME = None          # None = auto-detect the single armature in the scene
OUTPUT_PATH = "//UE4_compatible_mannequin.fbx"  # relative to the .blend file

KEEP_BONES = {
    "root", "pelvis",
    "spine_01", "spine_02", "spine_03", "neck_01", "head",
    "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",
    "thumb_01_l", "thumb_02_l", "thumb_03_l",
    "index_01_l", "index_02_l", "index_03_l",
    "middle_01_l", "middle_02_l", "middle_03_l",
    "ring_01_l", "ring_02_l", "ring_03_l",
    "pinky_01_l", "pinky_02_l", "pinky_03_l",
    "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",
    "thumb_01_r", "thumb_02_r", "thumb_03_r",
    "index_01_r", "index_02_r", "index_03_r",
    "middle_01_r", "middle_02_r", "middle_03_r",
    "ring_01_r", "ring_02_r", "ring_03_r",
    "pinky_01_r", "pinky_02_r", "pinky_03_r",
    "thigh_l", "calf_l", "foot_l", "ball_l",
    "thigh_r", "calf_r", "foot_r", "ball_r",
    "ik_foot_root", "ik_foot_l", "ik_foot_r",
    "ik_hand_root", "ik_hand_gun", "ik_hand_l", "ik_hand_r",
}


def find_armature():
    if ARMATURE_NAME:
        obj = bpy.data.objects.get(ARMATURE_NAME)
        if obj is None or obj.type != 'ARMATURE':
            raise RuntimeError(f"'{ARMATURE_NAME}' is not a valid armature object")
        return obj
    armatures = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    if len(armatures) == 0:
        raise RuntimeError("No armature found in the scene.")
    if len(armatures) > 1:
        names = ", ".join(a.name for a in armatures)
        raise RuntimeError(
            f"Multiple armatures found ({names}). Set ARMATURE_NAME explicitly."
        )
    return armatures[0]


def find_meshes_using_armature(arm_obj):
    meshes = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object == arm_obj:
                meshes.append(obj)
                break
    return meshes


def nearest_kept_ancestor(bone_name, parent_of):
    """Walk up the parent chain until we hit a bone that's in KEEP_BONES."""
    current = parent_of.get(bone_name)
    visited = set()
    while current is not None:
        if current in KEEP_BONES:
            return current
        if current in visited:
            break  # safety against malformed data
        visited.add(current)
        current = parent_of.get(current)
    return "root"  # fallback; root should always be in KEEP_BONES


def merge_vertex_group(mesh_obj, src_name, dst_name):
    """Add src group's weights into dst group (creating dst if needed), then
    remove src group."""
    vgroups = mesh_obj.vertex_groups
    src = vgroups.get(src_name)
    if src is None:
        return
    dst = vgroups.get(dst_name)
    if dst is None:
        dst = vgroups.new(name=dst_name)

    src_idx = src.index
    for v in mesh_obj.data.vertices:
        src_weight = None
        for g in v.groups:
            if g.group == src_idx:
                src_weight = g.weight
                break
        if src_weight is None or src_weight <= 0.0:
            continue
        # additive merge into destination, clamped to 1.0
        existing = 0.0
        try:
            existing = dst.weight(v.index)
        except RuntimeError:
            existing = 0.0
        new_weight = min(1.0, existing + src_weight)
        dst.add([v.index], new_weight, 'REPLACE')

    vgroups.remove(src)


def main():
    arm_obj = find_armature()
    bones = arm_obj.data.bones
    parent_of = {b.name: (b.parent.name if b.parent else None) for b in bones}

    remove_bones = [name for name in parent_of if name not in KEEP_BONES]
    if not remove_bones:
        print("No non-standard bones found - armature already matches the "
              "UE4 bone set. Skipping merge step.")
    else:
        mapping = {name: nearest_kept_ancestor(name, parent_of) for name in remove_bones}
        print(f"Found {len(remove_bones)} non-standard bone(s) to merge/remove:")
        for name, target in mapping.items():
            print(f"  {name}  ->  merged into  {target}")

        mesh_objs = find_meshes_using_armature(arm_obj)
        if not mesh_objs:
            print("WARNING: no mesh found using this armature - skipping weight merge, "
                  "only the skeleton will be trimmed.")
        for mesh_obj in mesh_objs:
            print(f"Merging vertex groups on mesh '{mesh_obj.name}'...")
            for src_name, dst_name in mapping.items():
                merge_vertex_group(mesh_obj, src_name, dst_name)

        # Remove the now-unused bones from the armature.
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = arm_obj.data.edit_bones
        # Deepest bones first, so parent-of-parent chains collapse cleanly.
        def depth(name):
            d = 0
            cur = parent_of.get(name)
            while cur is not None:
                d += 1
                cur = parent_of.get(cur)
            return d
        for name in sorted(remove_bones, key=depth, reverse=True):
            eb = edit_bones.get(name)
            if eb is not None:
                edit_bones.remove(eb)
        bpy.ops.object.mode_set(mode='OBJECT')

    remaining = {b.name for b in arm_obj.data.bones}
    missing_from_ue4 = KEEP_BONES - remaining
    if missing_from_ue4:
        print("\nNOTE: these standard UE4 bones were not found in your source "
              "armature and will be absent from the export:")
        print("  " + ", ".join(sorted(missing_from_ue4)))
        print("  (Fine if you don't need them - e.g. some UE5 exports omit the "
              "ik_ bones - but check finger/IK chains if animations look wrong.)")

    print(f"\nExporting to {OUTPUT_PATH} ...")
    bpy.ops.export_scene.fbx(
        filepath=bpy.path.abspath(OUTPUT_PATH),
        use_selection=False,
        add_leaf_bones=False,
        bake_anim=False,
        armature_nodetype='NULL',
        object_types={'ARMATURE', 'MESH'},
    )
    print("Done. Import this FBX into your UE4 project and assign it to the "
          "existing SK_Mannequin skeleton asset (or create a new one).")


main()
