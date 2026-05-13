'use client'

import { Suspense, useMemo } from 'react'
import { Canvas, useLoader } from '@react-three/fiber'
import { Center } from '@react-three/drei'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
import * as THREE from 'three'

function ThumbModel({
  url,
  primary,
  secondary,
}: {
  url: string
  primary: string
  secondary: string
}) {
  const geometry = useLoader(STLLoader, url)

  const { bbox, scale } = useMemo(() => {
    const g = geometry.clone()
    g.computeBoundingBox()
    const box = g.boundingBox!
    const size = new THREE.Vector3()
    box.getSize(size)
    const maxDim = Math.max(size.x, size.y, size.z)
    return { bbox: box, scale: 3.2 / Math.max(maxDim, 0.0001) }
  }, [geometry])

  const material = useMemo(() => {
    const m = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      metalness: 0.15,
      roughness: 0.45,
    })

    m.onBeforeCompile = (shader) => {
      shader.uniforms.uPrimary = { value: new THREE.Color(primary) }
      shader.uniforms.uSecondary = { value: new THREE.Color(secondary) }
      shader.uniforms.uMinY = { value: bbox.min.y }
      shader.uniforms.uMaxY = { value: bbox.max.y }

      shader.vertexShader = shader.vertexShader.replace(
        '#include <common>',
        `#include <common>\nvarying float vLocalY;`
      )
      shader.vertexShader = shader.vertexShader.replace(
        '#include <begin_vertex>',
        `#include <begin_vertex>\nvLocalY = position.y;`
      )

      shader.fragmentShader = shader.fragmentShader.replace(
        '#include <common>',
        `#include <common>
varying float vLocalY;
uniform vec3 uPrimary;
uniform vec3 uSecondary;
uniform float uMinY;
uniform float uMaxY;
`
      )
      shader.fragmentShader = shader.fragmentShader.replace(
        '#include <color_fragment>',
        `#include <color_fragment>
float t = clamp((vLocalY - uMinY) / max(uMaxY - uMinY, 0.0001), 0.0, 1.0);
float k = smoothstep(0.25, 0.75, t);
vec3 blended = mix(uSecondary, uPrimary, k);
diffuseColor.rgb *= blended;
`
      )
    }

    return m
  }, [bbox.min.y, bbox.max.y, primary, secondary])

  return (
    <Center>
      <mesh
        geometry={geometry}
        material={material}
        scale={scale}
        rotation={[-Math.PI / 2, 0, 0]}
      />
    </Center>
  )
}

export function VersionThumbnail({
  url,
  primary,
  secondary,
}: {
  url: string
  primary: string
  secondary: string
}) {
  return (
    <Canvas
      camera={{ position: [4, 3, 5], fov: 35 }}
      dpr={[1, 1.5]}
      gl={{ preserveDrawingBuffer: false }}
    >
      <ambientLight intensity={0.55} />
      <directionalLight position={[4, 6, 4]} intensity={0.9} />
      <directionalLight position={[-3, 2, -2]} intensity={0.3} />
      <Suspense fallback={null}>
        <ThumbModel url={url} primary={primary} secondary={secondary} />
      </Suspense>
    </Canvas>
  )
}
