"""Proyecto Bambu Studio (.3mf) con piezas, filamentos y ajustes de impresión ya asignados.

Sigue el formato que escribe Bambu Studio (src/libslic3r/Format/bbs_3mf.cpp, v02.08.04.61):
modelo principal con componentes -> 3D/Objects/object_1.model, model_settings.config con el
extrusor de cada pieza y project_settings.config con los perfiles completos del sistema.

Necesita `bbl_profiles.py` (resuelve los perfiles oficiales de la A1 con sus `inherits` e
`include`). Ese módulo se perdió con el contenedor de la sesión del 17 nov 2026 y hay que
reescribirlo: ver «Cómo se regenera» en ../APRENDIZAJES.md.
"""
import io
import json
import sys
import zipfile
from datetime import date

import numpy as np
import trimesh

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from bbl_profiles import TAG, resolved  # noqa: E402

APP_VERSION = TAG.lstrip("v")
META_KEYS = {"type", "name", "from", "instantiation", "inherits", "setting_id", "filament_id",
             "compatible_printers", "compatible_printers_condition", "description", "version",
             "renamed_from", "is_custom_defined", "printer_model_id"}


def project_settings(printer, process, filament, colours, overrides):
    m, p, f = resolved("machine", printer), resolved("process", process), resolved("filament", filament)
    n = len(colours)
    cfg = {}
    for src in (m, p):
        cfg.update({k: v for k, v in src.items() if k not in META_KEYS})
    for k, v in f.items():
        if k in META_KEYS:
            continue
        if isinstance(v, list) and len(v) > 1 and k.startswith("filament_dev_"):
            continue  # datos de secado del AMS con varios valores por filamento: no afectan al laminado
        cfg[k] = (v * n if len(v) == 1 else v) if isinstance(v, list) else v
    cfg.update({
        "name": "project_settings", "from": "project", "version": APP_VERSION,
        "printer_settings_id": printer, "print_settings_id": process,
        "filament_settings_id": [filament] * n, "filament_ids": [f.get("filament_id", "GFA00")] * n,
        "filament_colour": colours, "filament_type": ["PLA"] * n,
        "default_filament_profile": [filament],
        "inherits_group": [""] + [""] * n + [""],
    })
    cfg.update(overrides)
    changed_print = ";".join(sorted(k for k in overrides if k in p or k in ("brim_type",)))
    changed_printer = ";".join(sorted(k for k in overrides if k in m or k == "curr_bed_type"))
    cfg["different_settings_to_system"] = [changed_print] + [""] * n + [changed_printer]
    return cfg


def mesh_xml(obj_id, uuid, mesh):
    v = "\n".join(f'     <vertex x="{x:.9g}" y="{y:.9g}" z="{z:.9g}"/>' for x, y, z in mesh.vertices)
    t = "\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in mesh.faces)
    return (f'  <object id="{obj_id}" p:UUID="{uuid}" type="model">\n   <mesh>\n    <vertices>\n{v}\n'
            f'    </vertices>\n    <triangles>\n{t}\n    </triangles>\n   </mesh>\n  </object>\n')


MODEL_HEAD = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
              'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
              'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
              'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n')


def build_3mf(path, title, parts, settings, bed_center, thumbnail_png, plate_meta=None):
    """parts: lista de (nombre, trimesh, extrusor 1..n) o (nombre, trimesh, None, ajustes) para un
    modificador: una pieza invisible que cambia ajustes (p. ej. el relleno) dentro de su volumen.
    bed_center: (x, y) para una pieza, o lista de (x, y) para varias copias (instancias) en la placa.
    plate_meta: metadatos de la placa, p. ej. {"first_layer_print_sequence": "1 2 3"} para que el
    brim salga del filamento 1 (si no, Bambu usa el de menos área en la primera capa)."""
    centres = [bed_center] if isinstance(bed_center[0], (int, float)) else list(bed_center)
    mods = {p[0]: p[3] for p in parts if len(p) > 3}
    parts = [p[:3] for p in parts]
    allv = np.vstack([m.vertices for n, m, _ in parts if n not in mods])
    lo, hi = allv.min(0), allv.max(0)
    centre = (lo + hi) / 2
    parts = [(n, trimesh.Trimesh(m.vertices - centre, m.faces, process=False), e) for n, m, e in parts]
    height = hi[2] - lo[2]
    obj_id = len(parts) + 1
    today = date.today().isoformat()

    sub = MODEL_HEAD + ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n'
    for i, (_, m, _) in enumerate(parts):
        sub += mesh_xml(i + 1, f"{(1 << 16) + i:08x}-81cb-4c03-9d28-80fed5dfa1dc", m)
    sub += " </resources>\n <build/>\n</model>\n"

    comps = "".join(
        f'    <component p:path="/3D/Objects/object_1.model" objectid="{i + 1}" '
        f'p:UUID="{(1 << 16) + i:08x}-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n'
        for i in range(len(parts)))
    meta = {"Application": f"BambuStudio-{APP_VERSION}", "BambuStudio:3mfVersion": "1", "Title": title,
            "CreationDate": today, "ModificationDate": today, "Designer": "", "Description": "", "License": ""}
    main = MODEL_HEAD + "".join(f' <metadata name="{k}">{v}</metadata>\n' for k, v in sorted(meta.items()))
    main += (f' <resources>\n  <object id="{obj_id}" p:UUID="00000001-61cb-4c03-9d28-80fed5dfa1dc" type="model">\n'
             f'   <components>\n{comps}   </components>\n  </object>\n </resources>\n'
             f' <build p:UUID="2c7c17d8-22b5-4d84-8835-1976022ea369">\n'
             + "".join(f'  <item objectid="{obj_id}" p:UUID="{obj_id:08x}-b1ec-4553-aec9-{k:012x}" '
                       f'transform="1 0 0 0 1 0 0 0 1 {cx:.3f} {cy:.3f} {height / 2:.4f}" printable="1"/>\n'
                       for k, (cx, cy) in enumerate(centres))
             + ' </build>\n</model>\n')

    cfg = ['<?xml version="1.0" encoding="UTF-8"?>', "<config>", f'  <object id="{obj_id}">',
           f'    <metadata key="name" value="{title}"/>', '    <metadata key="extruder" value="1"/>',
           f'    <metadata face_count="{sum(len(m.faces) for _, m, _ in parts)}"/>']
    for i, (name, m, ext) in enumerate(parts):
        kind = "modifier_part" if name in mods else "normal_part"
        cfg += [f'    <part id="{i + 1}" subtype="{kind}">',
                f'      <metadata key="name" value="{name}"/>',
                '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>']
        if name in mods:
            cfg += [f'      <metadata key="{k}" value="{v}"/>' for k, v in mods[name].items()]
        else:
            cfg += [f'      <metadata key="extruder" value="{ext}"/>']
        cfg += [
                f'      <mesh_stat face_count="{len(m.faces)}" edges_fixed="0" degenerate_facets="0" '
                'facets_removed="0" facets_reversed="0" backwards_edges="0"/>', "    </part>"]
    cfg += ["  </object>", "  <plate>", '    <metadata key="plater_id" value="1"/>',
            '    <metadata key="plater_name" value=""/>', '    <metadata key="locked" value="false"/>',
            '    <metadata key="thumbnail_file" value="Metadata/plate_1.png"/>',
            *[f'    <metadata key="{k}" value="{v}"/>' for k, v in (plate_meta or {}).items()],
            ]
    for k in range(len(centres)):
        cfg += ["    <model_instance>", f'      <metadata key="object_id" value="{obj_id}"/>',
                f'      <metadata key="instance_id" value="{k}"/>', f'      <metadata key="identify_id" value="{100 + k}"/>',
                "    </model_instance>"]
    cfg += ["  </plate>", "  <assemble>"]
    cfg += [f'   <assemble_item object_id="{obj_id}" instance_id="{k}" transform="1 0 0 0 1 0 0 0 1 '
            f'{cx:.3f} {cy:.3f} {height / 2:.4f}" offset="0 0 0" />' for k, (cx, cy) in enumerate(centres)]
    cfg += ["  </assemble>", "</config>"]

    content_types = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
                     ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
                     ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
                     ' <Default Extension="png" ContentType="image/png"/>\n'
                     ' <Default Extension="gcode" ContentType="text/x.gcode"/>\n</Types>\n')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
            ' <Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>\n'
            '</Relationships>\n')
    model_rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                  ' <Relationship Target="/3D/Objects/object_1.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
                  '</Relationships>\n')

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", main)
        z.writestr("3D/_rels/3dmodel.model.rels", model_rels)
        z.writestr("3D/Objects/object_1.model", sub)
        z.writestr("Metadata/model_settings.config", "\n".join(cfg) + "\n")
        z.writestr("Metadata/project_settings.config", json.dumps(settings, indent=4, ensure_ascii=False))
        z.writestr("Metadata/plate_1.png", thumbnail_png)
