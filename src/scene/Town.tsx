import { useEffect, useMemo, useRef } from "react";
import { useAnimations, useGLTF } from "@react-three/drei";
import * as THREE from "three";
import { useEdgeRotation } from "../hooks/useEdgeRotation";
import { bakeStatic, toonFor, toonify } from "./toon";

const base = import.meta.env.BASE_URL;
const TOWN_URL = `${base}models/town.glb`;
const SHOPKEEPER_URL = `${base}models/npc_shopkeeper.glb`;

// NPCs that don't have finished models yet stand in as grey pegs at their spots.
const PLACEHOLDER_NPCS = ["king", "blacksmith", "wizard", "adventurer"];

function useSpots(scene: THREE.Object3D) {
  return useMemo(() => {
    scene.updateMatrixWorld(true);
    const spots: Record<string, THREE.Matrix4> = {};
    scene.traverse((o) => {
      if (o.name.startsWith("spot_")) spots[o.name.slice(5)] = o.matrixWorld.clone();
    });
    return spots;
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

function Shopkeeper() {
  const { scene, animations } = useGLTF(SHOPKEEPER_URL);
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

function PlaceholderNpc() {
  const mat = useMemo(() => toonFor(new THREE.MeshStandardMaterial({ color: "#c9ced8", name: "pal_block" })), []);
  return (
    <group>
      <mesh material={mat} position={[0, 0.35, 0]} castShadow>
        <cylinderGeometry args={[0.18, 0.24, 0.6, 12]} />
      </mesh>
      <mesh material={mat} position={[0, 0.92, 0]} castShadow>
        <sphereGeometry args={[0.3, 16, 12]} />
      </mesh>
    </group>
  );
}

type TownProps = {
  /** Name of an object in town.glb to turn to the front and frame, for reviewing one asset. */
  focus?: string | null;
  onFocus?: (point: THREE.Vector3) => void;
};

export function Town({ focus, onFocus }: TownProps) {
  const { scene } = useGLTF(TOWN_URL);
  const spots = useSpots(scene);
  const baked = useMemo(() => bakeStatic(scene), [scene]);
  const turntable = useRef<THREE.Group>(null);
  useEdgeRotation(turntable, !focus);

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
      <Placed matrix={spots.shopkeeper}>
        <Shopkeeper />
      </Placed>
      {PLACEHOLDER_NPCS.map((n) => (
        <Placed key={n} matrix={spots[n]}>
          <PlaceholderNpc />
        </Placed>
      ))}
    </group>
  );
}

useGLTF.preload(TOWN_URL);
useGLTF.preload(SHOPKEEPER_URL);
