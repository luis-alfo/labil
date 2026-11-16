"""Exporta la botonera v2 a 3MF bicolor para Bambu Studio.

Dos piezas en un mismo objeto: base (filamento 1) y logo (filamento 2).
El logo solo ocupa la franja superior (z > ALTO_CAJA), así que también se
puede imprimir sin AMS con un único cambio de filamento a esa altura.
Uso: python3 exportar_color.py
"""
import zipfile
import numpy as np
from manifold3d import Manifold
import generar as v1
import generar_v2 as v2

COLOR_BASE = "#FFFFFF"   # fondo
COLOR_LOGO = "#000000"   # logo (negro NocodeHackers)


def piezas():
    total = v2.construir()
    logo = Manifold()
    for forma, (cx, cy), _ in v1.BOTONES:
        logo += Manifold.extrude(forma(v1.FORMA).translate([cx, cy]), v1.ALTO_FORMA).translate(
            [0, 0, v1.ALTO_CAJA])
    return total - logo, logo


def malla_xml(m):
    t = v1.a_trimesh(m)
    assert t.is_watertight
    v = "".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in t.vertices)
    f = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in t.faces)
    return f"<mesh><vertices>{v}</vertices><triangles>{f}</triangles></mesh>", t.volume


def exportar(ruta):
    base, logo = piezas()
    mb, vb = malla_xml(base)
    ml, vl = malla_xml(logo)
    modelo = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
 <metadata name="Application">BambuStudio-01.10.00.00</metadata>
 <resources>
  <basematerials id="9"><base name="fondo" displaycolor="{COLOR_BASE}"/><base name="logo" displaycolor="{COLOR_LOGO}"/></basematerials>
  <object id="1" name="fondo" type="model" pid="9" pindex="0">{mb}</object>
  <object id="2" name="logo" type="model" pid="9" pindex="1">{ml}</object>
  <object id="3" name="botonera_nch_v2" type="model">
   <components><component objectid="1"/><component objectid="2"/></components>
  </object>
 </resources>
 <build><item objectid="3" transform="1 0 0 0 1 0 0 0 1 128 128 0"/></build>
</model>"""
    ajustes = """<?xml version="1.0" encoding="UTF-8"?>
<config>
 <object id="3">
  <metadata key="name" value="botonera_nch_v2"/>
  <metadata key="extruder" value="1"/>
  <part id="1" subtype="normal_part"><metadata key="name" value="fondo"/><metadata key="extruder" value="1"/></part>
  <part id="2" subtype="normal_part"><metadata key="name" value="logo"/><metadata key="extruder" value="2"/></part>
 </object>
</config>"""
    tipos = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="config" ContentType="text/xml"/>
</Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>"""
    with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", tipos)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", modelo)
        z.writestr("Metadata/model_settings.config", ajustes)
    print(f"fondo {vb / 1000 * 1.24:.1f} g, logo {vl / 1000 * 1.24:.1f} g (PLA macizo)")


if __name__ == "__main__":
    exportar("botonera_nch_v2_color.3mf")
