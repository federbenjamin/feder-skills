---
name: blender-to-unity-props
argument-hint: "[props to model]"
description: Model props in Blender and hand them to a Unity project as FBX files that import at rotation 0, scale 1, true size, front toward Unity +Z. Use when an agent needs props, a model, or a placeholder mesh in a Unity project and builds it in Blender (Blender MCP bridge or headless script), or when a Blender FBX lands in Unity rotated, scaled wrong, or facing backwards.
---

# blender-to-unity-props

Goal: each prop reaches Unity as one FBX whose root imports at rotation (0,0,0) and scale 1, at its true size in metres, front toward Unity +Z, with object and material names that Unity code can find. The Blender side makes that boring: the fix for a wrong import is always a changed export or importer setting, never a transform edited in Unity.

## Find out first

- The project's import rules (its rules doc or `AGENTS.md`): where models live, how importer defaults are applied, naming, materials.
- How importer defaults are applied: a default Preset, an `AssetPostprocessor.OnPreprocessModel`, or nothing. With nothing, set the importer settings below on each model.
- Whether `.gitattributes` already sends `*.fbx` and `*.blend` to LFS.
- Whose Blender window holds the MCP bridge, which decides the route.

## Routes

- **MCP bridge you own.** The blender-mcp addon serves `localhost:9876` from whichever Blender window started it. Load its tool schemas, call the scene-info tool first, start a fresh `.blend`, and save it in the staging folder.
- **Headless script.** When the window belongs to someone else, a second agent loading a `.blend` into the bridge replaces their scene. Run Blender in the background instead, which needs no window or bridge:
  `/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python build.py -- <staging dir> <preview dir>`
  Start from [build-template.py](build-template.py) beside this file: it builds geometry in bmesh, exports each asset, renders a workbench preview PNG per asset, writes `stats.json`, and saves the `.blend`. A model built in code reruns after any fix.

## Modelling conventions

- Metres, scene unit scale 1.0.
- Origin at the bottom centre of the asset, where Unity's pivot belongs.
- Rotation 0 and scale 1 on every object, applied.
- Front toward Blender -Y; it lands on Unity +Z.
- One collection per asset; the collection is what gets selected for export.
- Triangulate before export, so the triangle count reported is the count Unity imports.
- A separate named object for each part Unity will move, spin, or parent to (`Board`, `Blades`). Its pivot sits where the behaviour wants it: the hub centre for a spinner, the centre of the front face for a label surface, with that face flat and unobstructed.
- Flat Principled BSDF colours, no textures, a few materials per asset, named to read in Unity (`Wood_Dark`, `Metal_Rust`). A separate material on a region (a label band) lets Unity remap it or put a decal on it.
- Object, FBX file, and prefab share one name.
- Stay inside the triangle budget the brief sets; a low-poly prop runs from tens to about fifteen hundred triangles.

## Export

One call per asset, run with the asset's objects selected:

```python
bpy.ops.export_scene.fbx(
    filepath=path, use_selection=True, object_types={'MESH'},
    axis_forward='-Y', axis_up='Z', use_space_transform=False,
    apply_scale_options='FBX_SCALE_ALL', bake_anim=False)
```

Everything else stays at its default (`global_scale=1.0`, `apply_unit_scale=True`, `bake_space_transform=False`, `use_mesh_modifiers=True`, `mesh_smooth_type='OFF'`, `embed_textures=False`). Blender's own axes plus Use Space Transform off leave the axis conversion to Unity's importer. Unity 6000.6.4f1 imported `FBX_SCALE_ALL` and `FBX_SCALE_UNITS` both at scale 1; use whichever the project's rules name, and `FBX_SCALE_ALL` when they name none.

## Unity import

Settings: Scale Factor 1, Convert Units on, **Bake Axis Conversion on**, Import Cameras and Lights off, and for a static prop Rig None and Import Animation off. Apply them through the project's one default (preset or postprocessor), or on each importer. A default preset does not apply on reimport: apply it by hand to models already imported.

Measured in Unity 6000.6.4f1 with the export above and Bake Axis Conversion on:

- Every FBX root: rotation (0,0,0), scale 1. Child objects: local rotation 0.
- Bounding boxes keep their sizes in metres.
- Blender -Y faces Unity +Z. A board mounted on a post's -Y side sits at local z = +0.11.
- An object thin along Blender Y is thin along Unity local Z, so a spinner whose axle is Blender Y spins about Unity local Z.

With Bake Axis Conversion off, the same files import with every child at local rotation (270, 180, 0), the root of a multi-part model likewise, and the front faces Unity -Z. A root or child at (270, 180, 0) means the importer lost Bake Axis Conversion.

## Staging, then copy

1. Work in a staging folder outside the Unity project and do not open the Unity editor or project while modelling: `<Name>.fbx` per asset, the source `.blend`, and the notes file.
2. Before the first commit of either type, make sure `.gitattributes` lists `*.fbx` and `*.blend` under LFS, and that `git lfs install` has run on the machine.
3. Copy each FBX into the project's models folder. Keep the `.blend` outside `Assets/`: a `.blend` under `Assets/` needs Blender on every machine that opens the project.
4. Every asset travels with its `.meta` file. Move, rename, and delete through the Project window or `AssetDatabase`, so the pair stays together.
5. Unity imports the FBX's material slots by name; remap them to the project's render-pipeline materials.

## Report

Write the notes file the importing agent reads, with the export settings listed once at the top and, per file:

- Bounding box min and max and size, in Blender axes (X right, Y back, Z up) and metres.
- Triangle count, per object when an asset has several.
- Material names.
- Each object with its pivot, and the spin axis or label surface where one exists.
- Anything the brief asked for that was not made.

Name the one check to run first in the editor: import one asymmetric asset (a sign whose board sits on one side) and confirm the root is at rotation 0 and scale 1, the size matches the bounding box, and the front lands on Unity +Z. A mismatch means fix the export or importer and re-export the whole set.
