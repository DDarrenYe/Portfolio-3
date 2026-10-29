import { useEffect, useMemo, useRef } from "react";
import { useAnimations, useGLTF } from "@react-three/drei";
import * as THREE from "three";
import { useEdgeRotation } from "../hooks/useEdgeRotation";
import { Smoke } from "./Smoke";
import { bakeStatic, toonify } from "./toon";

const base = import.meta.env.BASE_URL;
const TOWN_URL = `${base}models/town.glb`;
const NPCS = ["shopkeeper", "king", "blacksmith", "wizard", "adventurer"] as const;
const npcUrl = (name: string) => `${base}models/npc_${name}.glb`;

/** Marker empties from Blender: spot_<npc> for where each NPC stands, smoke_<name> for chimneys. */
function useMarkers(scene: THREE.Object3D) {
  return useMemo(() => {
    scene.updateMatrixWorld(true);
    const spots: Record<string, THREE.Matrix4> = {};
    const smoke: THREE.Vector3[] = [];
    let houses = 0;
    scene.traverse((o) => {
      if (o.name.startsWith("spot_")) spots[o.name.slice(5)] = o.matrixWorld.clone();
      if (!o.name.startsWith("smoke_")) return;
      // every landmark smokes, but only one house chimney in three, so the sky stays readable
      const isHouse = /^smoke_(inner|outer)_/.test(o.name);
      if (!isHouse || houses++ % 3 === 0) smoke.push(o.getWorldPosition(new THREE.Vector3()));
    });
    return { spots, smoke };
  }, [scene]);
}

function Placed({ matrix, children }: { matrix?: THREE.Matrix4; children: React.ReactNode }) {
  const ref = useRef<THREE.Group>(null);
  useEffect(() => {
    if (!ref.current || !matrix) return;
    matrix.decompose(ref.current.position, ref.current.quaternion, ref.current.scale);
  }, [matrix]);
  return <group ref={ref}>{children}</group>;
}

function Npc({ name }: { name: string }) {
  const { scene, animations } = useGLTF(npcUrl(name), false, false);
  const ref = useRef<THREE.Group>(null);
  const model = useMemo(() => {
    toonify(scene, 0.045);
    return scene;
  }, [scene]);
  const { actions } = useAnimations(animations, ref);
  useEffect(() => {
    Object.values(actions)[0]?.reset().play();
  }, [actions]);
  return <primitive ref={ref} object={model} />;
}

type TownProps = {
  /** Name of an object in town.glb to turn to the front and frame, for reviewing one asset. */
  focus?: string | null;
  onFocus?: (point: THREE.Vector3) => void;
  /** Starting rotation in degrees. */
  turn?: number;
};

export function Town({ focus, onFocus, turn = 0 }: TownProps) {
  const { scene } = useGLTF(TOWN_URL, false, false);
  const { spots, smoke } = useMarkers(scene);
  const baked = useMemo(() => bakeStatic(scene), [scene]);
  const turntable = useRef<THREE.Group>(null);
  useEdgeRotation(turntable, !focus);

  useEffect(() => {
    if (turntable.current) turntable.current.rotation.y = THREE.MathUtils.degToRad(turn);
  }, [turn]);

  useEffect(() => {
    const target = focus ? scene.getObjectByName(focus) : undefined;
    if (!target || !turntable.current) return;
    const p = target.getWorldPosition(new THREE.Vector3());
    // turn the town so the object sits at the front, then hand its new position to the camera
    const angle = -Math.atan2(p.x, p.z);
    turntable.current.rotation.y = angle;
    onFocus?.(p.applyAxisAngle(new THREE.Vector3(0, 1, 0), angle));
  }, [focus, scene, onFocus]);

  return (
    <group ref={turntable}>
      <primitive object={baked} />
      <Smoke points={smoke} />
      {NPCS.map((n) => (
        <Placed key={n} matrix={spots[n]}>
          <Npc name={n} />
        </Placed>
      ))}
    </group>
  );
}

// Models are uncompressed for now, so skip the Draco and meshopt decoders (and their downloads).
useGLTF.preload(TOWN_URL, false, false);
for (const n of NPCS) useGLTF.preload(npcUrl(n), false, false);
