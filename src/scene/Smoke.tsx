import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { outlineGeometry, outlineMaterial, toonFor } from "./toon";

const PUFFS = 3;
const RISE = 1.3; // units a puff climbs before it vanishes
const SPEED = 0.28; // cycles per second

const puffGeometry = new THREE.IcosahedronGeometry(0.26, 1);
const puffOutline = outlineGeometry(puffGeometry);
const puffMaterial = toonFor(new THREE.MeshStandardMaterial({ color: "#ffffff", name: "pal_smoke" }));

/** Round toon puffs drifting up from each chimney, like the steam in the reference. */
export function Smoke({ points }: { points: THREE.Vector3[] }) {
  const puffs = useRef<THREE.Group[]>([]);
  const offsets = useMemo(() => points.map((_, i) => (i * 0.37) % 1), [points]);
  const reduce = useMemo(() => window.matchMedia("(prefers-reduced-motion: reduce)").matches, []);

  useFrame(({ clock }) => {
    const t = reduce ? 0.5 : clock.elapsedTime;
    puffs.current.forEach((g, k) => {
      if (!g) return;
      const chimney = Math.floor(k / PUFFS);
      const phase = (t * SPEED + offsets[chimney] + (k % PUFFS) / PUFFS) % 1;
      // grow, then shrink away at the top, since toon materials can't fade
      const s = Math.sin(phase * Math.PI) * (0.6 + phase * 0.8);
      g.position.set(Math.sin(phase * 5 + chimney) * 0.12, phase * RISE, Math.cos(phase * 4 + chimney) * 0.08);
      g.scale.setScalar(Math.max(s, 0.001));
    });
  });

  return (
    <>
      {points.map((p, i) => (
        <group key={i} position={p}>
          {Array.from({ length: PUFFS }, (_, j) => (
            <group key={j} ref={(g) => (puffs.current[i * PUFFS + j] = g!)}>
              <mesh geometry={puffGeometry} material={puffMaterial} />
              <mesh geometry={puffOutline} material={outlineMaterial} />
            </group>
          ))}
        </group>
      ))}
    </>
  );
}
