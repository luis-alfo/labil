#!/usr/bin/env node
/**
 * Generate a motel-keychain STL with recessed text engraved on the back face.
 *
 *   node scripts/generate-key-stl.mjs --text="Room 26"
 *   node scripts/generate-key-stl.mjs --text="Room|7" --size=11 --depth=0.6
 *   node scripts/generate-key-stl.mjs --text="Suite|A12" --face=front --out=public/models/key-suite-a12.stl
 *
 * Use "|" or "\n" inside --text to split into multiple lines.
 */
import * as THREE from 'three'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
import { STLExporter } from 'three/examples/jsm/exporters/STLExporter.js'
import { Font } from 'three/examples/jsm/loaders/FontLoader.js'
import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry.js'
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js'
import { Brush, Evaluator, SUBTRACTION } from 'three-bvh-csg'
import * as fs from 'node:fs'
import * as path from 'node:path'

function parseArgs(argv) {
  const out = {}
  for (const a of argv) {
    const m = a.match(/^--([^=]+)=(.*)$/)
    if (m) out[m[1]] = m[2]
    else out[a.replace(/^--/, '')] = true
  }
  return out
}
function slug(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
}

const args = parseArgs(process.argv.slice(2))
const text = String(args.text ?? 'Room 26')
const textSize = parseFloat(args.size ?? '7')
const lineSpacingFactor = parseFloat(args['line-spacing'] ?? '1.15')
const recessDepth = parseFloat(args.depth ?? '0.6')
const face = args.face ?? 'back'
const layout = args.layout ?? 'vertical' // 'vertical' = lines along long axis; 'horizontal' = along short axis
const inputStl = args.in ?? 'public/models/key.stl'
const outputStl = args.out ?? `public/models/key-${slug(text)}.stl`
const fontPath =
  args.font ?? 'node_modules/three/examples/fonts/droid/droid_serif_bold.typeface.json'

// --- 1. Load key STL ---
const stlBuf = fs.readFileSync(inputStl)
const ab = stlBuf.buffer.slice(stlBuf.byteOffset, stlBuf.byteOffset + stlBuf.byteLength)
const keyGeom = new STLLoader().parse(ab)
keyGeom.computeBoundingBox()
const kb = keyGeom.boundingBox
const center = new THREE.Vector3()
kb.getCenter(center)
console.log(`Key bbox: ${JSON.stringify({
  x: [kb.min.x.toFixed(2), kb.max.x.toFixed(2)],
  y: [kb.min.y.toFixed(2), kb.max.y.toFixed(2)],
  z: [kb.min.z.toFixed(2), kb.max.z.toFixed(2)],
})}`)

// --- 2. Load font ---
const fontData = JSON.parse(fs.readFileSync(fontPath, 'utf-8'))
const font = new Font(fontData)

// --- 3. Build extruded text geometry from one or more lines ---
const lines = text.split(/\|/).flatMap((l) => l.split(/\\n|\n/))
const lineSpacing = textSize * lineSpacingFactor
const totalExtrude = recessDepth + 0.6 // generous overshoot for a clean boolean

const validLines = lines.map((l) => l.trim()).filter(Boolean)
const lineGeoms = []
validLines.forEach((line, idx) => {
  const g = new TextGeometry(line, {
    font,
    size: textSize,
    depth: totalExtrude,
    bevelEnabled: false,
    curveSegments: 8,
  })
  g.computeBoundingBox()
  const bb = g.boundingBox
  const cx = (bb.min.x + bb.max.x) / 2
  // idx=0 placed at the highest Y. After the rotation/mirror below, idx=0
  // ends up at the LOW X end of the keychain (next to the hole), which is
  // the natural "top" when the keychain is held by the ring.
  g.translate(-cx, -idx * lineSpacing - bb.max.y, -bb.min.z)
  lineGeoms.push(g)
})
if (lineGeoms.length === 0) {
  console.error('No text provided.')
  process.exit(1)
}

let textGeom = lineGeoms.length === 1 ? lineGeoms[0] : mergeGeometries(lineGeoms, false)
if (!textGeom) {
  console.error('mergeGeometries failed — make sure all line geometries share the same attributes.')
  process.exit(1)
}
textGeom.computeBoundingBox()
const tb = textGeom.boundingBox
const tCx = (tb.min.x + tb.max.x) / 2
const tCy = (tb.min.y + tb.max.y) / 2
// Center the whole text block at XY=(0,0) and Z starting at 0
textGeom.translate(-tCx, -tCy, -tb.min.z)

// --- 4. Orient & place text on chosen face ---
//
// Target in STL frame (looking at the back face from outside, ring held UP):
//   - line stacking → along the long X axis, idx=0 next to the ring (low X)
//   - reading direction within each line → along the short Y axis
//   - each letter standing upright with its top pointing toward the ring
//
// TextGeometry's native frame: letters read +X with their tops at +Y, lines
// stacked along Y. For the BACK face we additionally need to mirror the
// geometry so it reads correctly when seen from -Z (otherwise the user reads
// it backwards once the keychain is flipped to look at the engraved side).
//
// For VERTICAL layout, this is achieved with:
//   - scale(-1, 1, 1)   ← mirror X for back-face readability
//   - rotateZ(+π/2)     ← lines now stack along X, letters read in Y
// The composite has determinant -1 (a reflection), so triangle winding must
// be reversed afterwards to keep a valid manifold mesh for CSG.

function reverseWinding(geom) {
  if (geom.index) {
    const arr = geom.index.array
    for (let i = 0; i < arr.length; i += 3) {
      const tmp = arr[i + 1]
      arr[i + 1] = arr[i + 2]
      arr[i + 2] = tmp
    }
    geom.index.needsUpdate = true
  } else {
    const pos = geom.attributes.position.array
    for (let i = 0; i < pos.length; i += 9) {
      for (let j = 0; j < 3; j++) {
        const tmp = pos[i + 3 + j]
        pos[i + 3 + j] = pos[i + 6 + j]
        pos[i + 6 + j] = tmp
      }
    }
    geom.attributes.position.needsUpdate = true
  }
}

if (face === 'back') {
  if (layout === 'vertical') {
    textGeom.scale(-1, 1, 1)
    reverseWinding(textGeom)
    textGeom.rotateZ(Math.PI / 2)
  } else {
    textGeom.scale(-1, 1, 1)
    reverseWinding(textGeom)
  }
  textGeom.computeBoundingBox()
  const fb = textGeom.boundingBox
  console.log(`Text after orient: X span ${(fb.max.x - fb.min.x).toFixed(1)}mm, Y span ${(fb.max.y - fb.min.y).toFixed(1)}mm`)
  const keyXSpan = kb.max.x - kb.min.x
  const keyYSpan = kb.max.y - kb.min.y
  if (fb.max.x - fb.min.x > keyXSpan * 0.85 || fb.max.y - fb.min.y > keyYSpan * 0.85) {
    console.warn('⚠  Text is larger than 85% of the key on at least one axis. Consider lowering --size.')
  }
  // Text now sits in z ∈ [0, totalExtrude] still (Z untouched). Move it so
  // its top face is recessDepth below the back surface and its bottom pokes
  // 0.6 mm outside (clean overshoot for the boolean):
  //   z ∈ [kb.min.z - 0.6, kb.min.z + recessDepth]
  textGeom.translate(center.x, center.y, kb.min.z - 0.6)
} else if (face === 'front') {
  if (layout === 'vertical') {
    textGeom.rotateZ(Math.PI / 2)
  }
  // Text reads correctly from +Z without mirroring. Translate to
  //   z ∈ [kb.max.z - recessDepth, kb.max.z + 0.6]
  textGeom.translate(center.x, center.y, kb.max.z - recessDepth)
} else {
  console.error(`Unknown --face=${face}. Use 'back' or 'front'.`)
  process.exit(1)
}

// --- 5. Boolean subtract: key − text ---
// three-bvh-csg requires both geometries to share the same attribute layout.
// Strip everything except position + recompute normals on both.
function normalize(geom) {
  const stripped = new THREE.BufferGeometry()
  stripped.setAttribute('position', geom.getAttribute('position'))
  if (geom.index) stripped.setIndex(geom.index)
  stripped.computeVertexNormals()
  return stripped
}
const keyClean = normalize(keyGeom)
const textClean = normalize(textGeom)

const keyBrush = new Brush(keyClean)
keyBrush.updateMatrixWorld()
const textBrush = new Brush(textClean)
textBrush.updateMatrixWorld()

const evaluator = new Evaluator()
evaluator.attributes = ['position', 'normal']
const result = evaluator.evaluate(keyBrush, textBrush, SUBTRACTION)
result.geometry.computeBoundingBox()
console.log(`Result triangles: ${result.geometry.attributes.position.count / 3}`)

// --- 6. Export to STL (binary) ---
const mesh = new THREE.Mesh(result.geometry)
const data = new STLExporter().parse(mesh, { binary: true })
const outDir = path.dirname(outputStl)
fs.mkdirSync(outDir, { recursive: true })
const buf = Buffer.from(data.buffer, data.byteOffset, data.byteLength)
fs.writeFileSync(outputStl, buf)
console.log(`✓ Wrote ${outputStl} (${(fs.statSync(outputStl).size / 1024).toFixed(1)} KB)`)
