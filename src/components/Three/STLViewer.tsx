'use client'

import { Suspense, useMemo, useRef, useEffect } from 'react'
import { Canvas, useLoader, useFrame } from '@react-three/fiber'
import { OrbitControls, Center, ContactShadows, Environment } from '@react-three/drei'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
import * as THREE from 'three'

type STLModelProps = {
  url: string
  primary: string
  secondary: string
  blendMode: 'gradient' | 'split'
  rotate: boolean
}

function STLModel({ url, primary, secondary, blendMode, rotate }: STLModelProps) {
  const geometry = useLoader(STLLoader, url)
  const meshRef = useRef<THREE.Mesh>(null)

  const { bbox, center } = useMemo(() => {
    const g = geometry.clone()
    g.computeBoundingBox()
    const box = g.boundingBox!
    const c = new THREE.Vector3()
    box.getCenter(c)
    return { bbox: box, center: c }
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
      shader.uniforms.uBlend = { value: blendMode === 'gradient' ? 1 : 0 }

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
uniform float uBlend;
`
      )

      shader.fragmentShader = shader.fragmentShader.replace(
        '#include <color_fragment>',
        `#include <color_fragment>
float t = clamp((vLocalY - uMinY) / max(uMaxY - uMinY, 0.0001), 0.0, 1.0);
float gradT = smoothstep(0.25, 0.75, t);
float splitT = step(0.5, t);
float k = mix(splitT, gradT, uBlend);
vec3 blended = mix(uSecondary, uPrimary, k);
diffuseColor.rgb *= blended;
`
      )

      m.userData.shader = shader
    }

    return m
  }, [bbox.min.y, bbox.max.y, blendMode, primary, secondary])

  useEffect(() => {
    const shader = material.userData.shader
    if (!shader) return
    shader.uniforms.uPrimary.value.set(primary)
    shader.uniforms.uSecondary.value.set(secondary)
    shader.uniforms.uBlend.value = blendMode === 'gradient' ? 1 : 0
  }, [primary, secondary, blendMode, material])

  useFrame((_, delta) => {
    if (rotate && meshRef.current) {
      meshRef.current.rotation.y += delta * 0.4
    }
  })

  // Scale geometry to fit nicely in the viewport
  const scale = useMemo(() => {
    const size = new THREE.Vector3()
    bbox.getSize(size)
    const maxDim = Math.max(size.x, size.y, size.z)
    return 3.5 / Math.max(maxDim, 0.0001)
  }, [bbox])

  return (
    <Center>
      <mesh
        ref={meshRef}
        geometry={geometry}
        material={material}
        scale={scale}
        rotation={[-Math.PI / 2, 0, 0]}
        castShadow
        receiveShadow
      />
    </Center>
  )
}

type STLViewerProps = {
  url: string
  primary: string
  secondary: string
  blendMode?: 'gradient' | 'split'
  rotate?: boolean
  background?: string
}

export function STLViewer({
  url,
  primary,
  secondary,
  blendMode = 'gradient',
  rotate = false,
  background = 'transparent',
}: STLViewerProps) {
  return (
    <Canvas
      shadows
      camera={{ position: [5, 4, 6], fov: 35 }}
      style={{ background, width: '100%', height: '100%' }}
      dpr={[1, 2]}
    >
      <ambientLight intensity={0.45} />
      <directionalLight
        position={[5, 8, 5]}
        intensity={1.1}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <directionalLight position={[-4, 3, -2]} intensity={0.35} />

      <Suspense fallback={null}>
        <STLModel
          url={url}
          primary={primary}
          secondary={secondary}
          blendMode={blendMode}
          rotate={rotate}
        />
        <ContactShadows
          position={[0, -1.6, 0]}
          opacity={0.35}
          scale={10}
          blur={2.5}
          far={4}
        />
        <Environment preset="apartment" />
      </Suspense>

      <OrbitControls
        enablePan={false}
        minDistance={3}
        maxDistance={15}
        autoRotate={false}
      />
    </Canvas>
  )
}
