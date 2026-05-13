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
const textSize = parseFloat(args.size ?? '11')
const recessDepth = parseFloat(args.depth ?? '0.6')
const face = args.face ?? 'back'
const inputStl = args.in ?? 'public/models/key.stl'
const outputStl = args.out ?? `public/models/key-${slug(text)}.stl`
const fontPath =
  args.font ?? 'node_modules/three/examples/fonts/helvetiker_bold.typeface.json'

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
const lineSpacing = textSize * 1.4
const totalExtrude = recessDepth + 0.6 // generous overshoot for a clean boolean

const lineGeoms = []
lines.forEach((line, idx) => {
  const trimmed = line.trim()
  if (!trimmed) return
  const g = new TextGeometry(trimmed, {
    font,
    size: textSize,
    depth: totalExtrude,
    bevelEnabled: false,
    curveSegments: 8,
  })
  g.computeBoundingBox()
  const bb = g.boundingBox
  const cx = (bb.min.x + bb.max.x) / 2
  // Stack lines top-down: line 0 highest, line N lowest. Place each line so its
  // own top sits at -(idx * spacing) and its center X is 0.
  g.translate(-cx, -(idx * lineSpacing) - bb.max.y, -bb.min.z)
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
textGeom.computeBoundingBox()
console.log(`Text bbox: width=${(textGeom.boundingBox.max.x - textGeom.boundingBox.min.x).toFixed(1)}mm height=${(textGeom.boundingBox.max.y - textGeom.boundingBox.min.y).toFixed(1)}mm`)

// --- 4. Position text on chosen face ---
if (face === 'back') {
  // Mirror so it reads correctly when viewed from -Z (outside the back face).
  // Rotate 180° around Y axis: flips X and Z. Text now extrudes toward -Z.
  textGeom.rotateY(Math.PI)
  // After rotation, z range = [-totalExtrude, 0]. We want
  //   z ∈ [kb.min.z - 0.6, kb.min.z + recessDepth]
  // so translate by (kb.min.z + recessDepth).
  textGeom.translate(center.x, center.y, kb.min.z + recessDepth)
} else if (face === 'front') {
  // Reads correctly from +Z already. z range [0, totalExtrude]; we want
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
