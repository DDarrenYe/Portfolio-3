import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import type * as THREE from "three";
import { getNight } from "../scene/DayNight";

/** Lighting for the 3D pieces of the UI (sign, scroll): warm key light that dims a little at night. */
export function UiLights() {
  const hemi = useRef<THREE.HemisphereLight>(null);
  const sun = useRef<THREE.DirectionalLight>(null);

  useFrame(() => {
    // dim a little after dark, but stay readable
    const n = getNight();
    if (sun.current) sun.current.intensity = 2.3 - n * 0.9;
    if (hemi.current) hemi.current.intensity = 1.9 - n * 0.5;
  });

  return (
    <>
      <hemisphereLight ref={hemi} args={["#f4f1ea", "#7f9fcc", 1.9]} />
      <directionalLight ref={sun} color="#fff3dc" intensity={2.3} position={[-4, 8, 10]} />
    </>
  );
}
