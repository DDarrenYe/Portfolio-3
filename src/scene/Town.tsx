import { useEffect, useMemo, useRef, useState } from "react";
import { useFrame, type ThreeEvent } from "@react-three/fiber";
import { Html, useAnimations, useGLTF } from "@react-three/drei";
import * as THREE from "three";
import { sectionFor, SECTIONS, type NpcId } from "../content/portfolio";
import { useEdgeRotation } from "../hooks/useEdgeRotation";
import { Smoke } from "./Smoke";
import { bakeStatic, makeOutlineMaterial, toonify } from "./toon";

const base = import.meta.env.BASE_URL;
const TOWN_URL = `${base}models/town.glb`;
const NPCS = SECTIONS.map((s) => s.npc);
const npcUrl = (name: string) => `${base}models/npc_${name}.glb`;
const INK = new THREE.Color("#2a2d3a");
const HIGHLIGHT = new THREE.Color("#f2b33d");

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

/** Turn that brings a point in town space round to the front, facing the camera. */
const frontAngle = (p: THREE.Vector3) => -Math.atan2(p.x, p.z);

function Placed({ matrix, children }: { matrix?: THREE.Matrix4; children: React.ReactNode }) {
  const ref = useRef<THREE.Group>(null);
  useEffect(() => {
    if (!ref.current || !matrix) return;
    matrix.decompose(ref.current.position, ref.current.quaternion, ref.current.scale);
  }, [matrix]);
  return <group ref={ref}>{children}</group>;
}

type NpcProps = { name: NpcId; active: boolean; onSelect: (npc: NpcId) => void };

function Npc({ name, active, onSelect }: NpcProps) {
  const { scene, animations } = useGLTF(npcUrl(name), false, false);
  const ref = useRef<THREE.Group>(null);
  const [hover, setHover] = useState(false);
  // toonify once per cached model; the outline material lives with it so hover can recolour it
  const outline = useMemo(() => {
    if (!scene.userData.outline) {
      const m = makeOutlineMaterial();
      toonify(scene, 0.045, m);
      scene.userData.outline = m;
    }
    return scene.userData.outline as THREE.ShaderMaterial;
  }, [scene]);
  const { actions } = useAnimations(animations, ref);

  useEffect(() => {
    Object.values(actions)[0]?.reset().play();
  }, [actions]);

  useEffect(() => {
    outline.uniforms.uColor.value.copy(hover || active ? HIGHLIGHT : INK);
  }, [hover, active, outline]);

  useEffect(() => {
    document.body.style.cursor = hover ? "pointer" : "";
    return () => {
      document.body.style.cursor = "";
    };
  }, [hover]);

  const over = (e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation();
    setHover(true);
  };

  return (
    <group
      onPointerOver={over}
      onPointerOut={() => setHover(false)}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(name);
      }}
    >
      <primitive ref={ref} object={scene} />
      {(hover || active) && (
        <Html position={[0, 1.75, 0]} center className="nametag-anchor" zIndexRange={[20, 0]}>
          <span className="nametag">
            {sectionFor(name).speaker}
            <small>{sectionFor(name).label}</small>
          </span>
        </Html>
      )}
    </group>
  );
}

type TownProps = {
  /** Name of a marker in town.glb to turn to the front and frame, for reviewing one asset. */
  focus?: string | null;
  /** The NPC being talked to; the town turns them to the front and stops. */
  active: NpcId | null;
  onSelect: (npc: NpcId) => void;
  onFocus: (point: THREE.Vector3 | null) => void;
  /** Starting rotation in degrees. */
  turn?: number;
};

export function Town({ focus, active, onSelect, onFocus, turn = 0 }: TownProps) {
  const { scene } = useGLTF(TOWN_URL, false, false);
  const { spots, smoke } = useMarkers(scene);
  const baked = useMemo(() => bakeStatic(scene), [scene]);
  const turntable = useRef<THREE.Group>(null);
  const target = useRef<number | null>(null);
  useEdgeRotation(turntable, !focus && !active);

  useEffect(() => {
    if (turntable.current) turntable.current.rotation.y = THREE.MathUtils.degToRad(turn);
  }, [turn]);

  // review mode: snap a marker to the front
  useEffect(() => {
    const marker = focus ? scene.getObjectByName(focus) : undefined;
    if (!marker || !turntable.current) return;
    const p = marker.getWorldPosition(new THREE.Vector3());
    const angle = frontAngle(p);
    turntable.current.rotation.y = angle;
    onFocus(p.applyAxisAngle(new THREE.Vector3(0, 1, 0), angle));
  }, [focus, scene, onFocus]);

  // talking: ease the chosen NPC round to the front and hand the camera their position
  useEffect(() => {
    if (focus) return;
    const m = active ? spots[active] : undefined;
    if (!m || !turntable.current) {
      target.current = null;
      onFocus(null);
      return;
    }
    const p = new THREE.Vector3().setFromMatrixPosition(m);
    const angle = frontAngle(p);
    // take the short way round from wherever the town is now
    const now = turntable.current.rotation.y;
    target.current = now + THREE.MathUtils.euclideanModulo(angle - now + Math.PI, Math.PI * 2) - Math.PI;
    onFocus(p.applyAxisAngle(new THREE.Vector3(0, 1, 0), angle));
  }, [active, spots, focus, onFocus]);

  useFrame((_, delta) => {
    if (target.current === null || !turntable.current) return;
    const r = turntable.current.rotation;
    r.y += (target.current - r.y) * Math.min(1, delta * 4);
  });

  return (
    <group ref={turntable}>
      <primitive object={baked} />
      <Smoke points={smoke} />
      {NPCS.map((n) => (
        <Placed key={n} matrix={spots[n]}>
          <Npc name={n} active={active === n} onSelect={onSelect} />
        </Placed>
      ))}
    </group>
  );
}

useGLTF.preload(TOWN_URL, false, false);
for (const n of NPCS) useGLTF.preload(npcUrl(n), false, false);
