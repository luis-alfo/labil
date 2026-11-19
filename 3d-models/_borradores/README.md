# Borradores (archivo)

Aquí están los borradores de diseño del soporte de estropajo que **no son versiones**:
según la regla de Luis, solo cuenta como versión lo que se ha impreso (V1 = `sponge-holder`,
V2 = `el-secadero-v2`).

| Carpeta | Qué es |
|---|---|
| `estropajero-v3/` | Borrador anterior a El Secadero V2 (bastidor + bandeja). |
| `estropajero-v4/` | Otro borrador (brazo + colgador + bandeja + llave). |

- Se conservan por las lecciones de sus `APRENDIZAJES.md`.
- No se publican: el despliegue (`.github/workflows/pages.yml`) solo ejecuta
  `3d-models/<carpeta>/generate_stl.py` en el primer nivel, y esto está un nivel más abajo.
  Sus salidas se quitaron de `docs/`.
- Sus `generate_stl.py` calculan la raíz del repo con `HERE.parents[1]`, así que
  desde aquí ya no apuntan bien a `docs/`. Si algún día se recuperan, hay que ajustar
  esa línea (o sacar la carpeta de nuevo a `3d-models/`).
- Los nombres «V3» y «V4» vienen de la conversación; no son versiones impresas.
