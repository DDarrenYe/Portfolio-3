import { Suspense, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useGLTF } from "@react-three/drei";
import * as THREE from "three";
import { makeOutlineMaterial, toonify } from "../scene/toon";
import { UiLights } from "./UiLights";

const SIGN_URL = `${import.meta.env.BASE_URL}models/sign.glb`;
const PX = 40; // pixels per Blender unit
const PITCH = THREE.MathUtils.degToRad(14); // look down a little so the tops of the beam and board show
const SWING_DEG = 0.9;
const SWING_SECONDS = 7;
const BEAM_OVERHANG = 26; // px the beam runs past the board
// sizes of the parts as modelled in art/scripts/sign.py
const BEAM_LEN = 10;
const BOARD_W = 10;
const BOARD_H = 3.6;
const POST_BELOW = 200; // px of post below the top of the beam

/** Where the DOM put things, in px from the sign's top-left corner. */
type Layout = {
  postLeft: number;
  beamTop: number;
  beamBottom: number;
  left: number;
  top: number;
  width: number;
  height: number;
  canvasW: number;
  canvasH: number;
};

const swingAngle = (t: number, still: boolean) => (still ? 0 : SWING_DEG * Math.sin((t / SWING_SECONDS) * Math.PI * 2));

/** Offset of el inside ancestor, ignoring transforms (so the swing doesn't skew the measurement). */
function offsetWithin(el: HTMLElement, ancestor: HTMLElement) {
  let x = 0;
  let y = 0;
  let node: HTMLElement | null = el;
  while (node && node !== ancestor) {
    x += node.offsetLeft;
    y += node.offsetTop;
    node = node.offsetParent as HTMLElement | null;
  }
  return { x, y };
}

const outlineResolution = { value: new THREE.Vector2(1, 1) };
const signOutline = makeOutlineMaterial(undefined, outlineResolution);

/** The Blender sign, laid out around the DOM text and swung in step with it. */
function SignScene({ layout, swing }: { layout: Layout; swing: React.RefObject<HTMLDivElement> }) {
  const { scene } = useGLTF(SIGN_URL, false, false);
  const { camera, size } = useThree();
  const swingGroup = useRef<THREE.Group>(null);
  const still = useMemo(() => window.matchMedia("(prefers-reduced-motion: reduce)").matches, []);

  const parts = useMemo(() => {
    toonify(scene, 0.04, signOutline);
    const get = (n: string) => scene.getObjectByName(n)!.clone(true);
    return {
      post: get("post"),
      brace: get("brace"),
      beam: get("beam"),
      clamps: [get("clamp"), get("clamp")],
      chains: [get("chain"), get("chain")],
      board: get("board"),
    };
  }, [scene]);

  useLayoutEffect(() => {
    outlineResolution.value.set(size.width, size.height);
    const L = layout;
    const u = (px: number) => px / PX;
    const pivotX = L.left + L.width / 2;
    for (const p of [parts.post, parts.brace]) p.position.set(u(L.postLeft), -u(L.beamTop), 0);
    parts.beam.position.set(u(L.postLeft), -u(L.beamTop), 0);
    parts.beam.scale.x = u(L.left + L.width + BEAM_OVERHANG - L.postLeft) / BEAM_LEN;
    swingGroup.current?.position.set(u(pivotX), -u(L.beamBottom), 0);
    const drop = u(L.top - L.beamBottom);
    [0.2, 0.8].forEach((f, i) => {
      const x = L.left + L.width * f;
      parts.clamps[i].position.set(u(x), -u(L.beamTop), 0.02);
      parts.chains[i].position.set(u(x - pivotX), 0, -0.05);
      parts.chains[i].scale.y = drop;
    });
    parts.board.position.set(u(L.left + L.width / 2 - pivotX), -drop, 0);
    parts.board.scale.set(u(L.width) / BOARD_W, u(L.height) / BOARD_H, 1);

    // camera tilted down by PITCH; the content group is stretched by 1/cos so the board's
    // front face still lines up pixel for pixel with the text on top of it
    const cam = camera as THREE.OrthographicCamera;
    const tx = u(L.canvasW) / 2;
    const ty = -u(L.canvasH) / 2 / Math.cos(PITCH);
    cam.zoom = PX;
    cam.position.set(tx, ty + Math.sin(PITCH) * 50, Math.cos(PITCH) * 50);
    cam.lookAt(tx, ty, 0);
    cam.updateProjectionMatrix();
  }, [layout, parts, camera, size]);

  useFrame(({ clock }) => {
    const deg = swingAngle(clock.elapsedTime, still);
    if (swingGroup.current) swingGroup.current.rotation.z = -THREE.MathUtils.degToRad(deg);
    if (swing.current) swing.current.style.transform = `rotate(${deg}deg)`;
  });

  return (
    <>
      <UiLights />
      <group scale={[1, 1 / Math.cos(PITCH), 1]}>
        <primitive object={parts.post} />
        <primitive object={parts.brace} />
        <primitive object={parts.beam} />
        {parts.clamps.map((c, i) => (
          <primitive key={`c${i}`} object={c} />
        ))}
        <group ref={swingGroup}>
          {parts.chains.map((c, i) => (
            <primitive key={`h${i}`} object={c} />
          ))}
          <primitive object={parts.board} />
        </group>
      </group>
    </>
  );
}

/**
 * The hanging wooden sign: a Blender model drawn with the town's toon shading, sized to the
 * name and buttons laid over it. The text stays real HTML so it's sharp and accessible.
 */
export function Signpost({ children }: { children: ReactNode }) {
  const root = useRef<HTMLElement>(null);
  const beam = useRef<HTMLDivElement>(null);
  const swing = useRef<HTMLDivElement>(null);
  const sign = useRef<HTMLDivElement>(null);
  const [layout, setLayout] = useState<Layout | null>(null);

  useLayoutEffect(() => {
    const measure = () => {
      if (!root.current || !beam.current || !sign.current) return;
      const b = offsetWithin(beam.current, root.current);
      const s = offsetWithin(sign.current, root.current);
      const width = sign.current.offsetWidth;
      const height = sign.current.offsetHeight;
      const beamTop = b.y;
      setLayout({
        postLeft: parseFloat(getComputedStyle(root.current).paddingLeft),
        beamTop,
        beamBottom: beamTop + beam.current.offsetHeight,
        left: s.x,
        top: s.y,
        width,
        height,
        canvasW: s.x + width + BEAM_OVERHANG + 24,
        canvasH: Math.max(beamTop + POST_BELOW + 8, s.y + height + 24),
      });
    };
    measure();
    const ro = new ResizeObserver(measure);
    if (sign.current) ro.observe(sign.current);
    window.addEventListener("resize", measure);
    return () => {
      ro.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, []);

  return (
    <header ref={root} className="signpost">
      {layout && (
        <div className="signpost-canvas" style={{ width: layout.canvasW, height: layout.canvasH }} aria-hidden="true">
          <Canvas orthographic dpr={[1, 2]} gl={{ antialias: true, alpha: true }} camera={{ near: 1, far: 200, zoom: PX }}>
            <Suspense fallback={null}>
              <SignScene layout={layout} swing={swing} />
            </Suspense>
          </Canvas>
        </div>
      )}
      <div className="signpost-arm">
        <div ref={beam} className="signpost-beam" />
        <div ref={swing} className="signpost-swing">
          <div className="signpost-chains" />
          <div ref={sign} className="sign">
            <div className="sign-frame">
              <div className="sign-board">{children}</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

useGLTF.preload(SIGN_URL, false, false);
