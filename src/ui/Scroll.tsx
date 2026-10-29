import { Suspense, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Canvas, useThree } from "@react-three/fiber";
import { useGLTF } from "@react-three/drei";
import * as THREE from "three";
import { makeOutlineMaterial, toonify } from "../scene/toon";
import { UiLights } from "./UiLights";

const SCROLL_URL = `${import.meta.env.BASE_URL}models/scroll.glb`;
const PX = 40; // pixels per Blender unit
const SHEET_W = 10; // sheet size as modelled in art/scripts/scroll.py
const SHEET_H = 1;
// room around the text for the rolled ends, which stand taller than the sheet
const PAD_X = 18;
const PAD_Y = 26;

type Layout = { x: number; y: number; w: number; h: number; canvasW: number; canvasH: number };

const outlineResolution = { value: new THREE.Vector2(1, 1) };
const scrollOutline = makeOutlineMaterial(undefined, outlineResolution);

/** The Blender scroll, stretched to fit the text and capped with a rolled end on each side. */
function ScrollScene({ layout }: { layout: Layout }) {
  const { scene } = useGLTF(SCROLL_URL, false, false);
  const { camera, size } = useThree();

  const parts = useMemo(() => {
    toonify(scene, 0.04, scrollOutline);
    const get = (n: string) => scene.getObjectByName(n)!.clone(true);
    return { sheet: get("sheet"), left: get("end_l"), right: get("end_r") };
  }, [scene]);

  useLayoutEffect(() => {
    outlineResolution.value.set(size.width, size.height);
    const u = (px: number) => px / PX;
    const L = layout;
    const cy = -u(L.y + L.h / 2);
    parts.sheet.position.set(u(L.x + L.w / 2), cy, 0);
    parts.sheet.scale.set(u(L.w) / SHEET_W, u(L.h) / SHEET_H, 1);
    // the ends keep their proportions, sized to the sheet's height
    const k = u(L.h) / SHEET_H;
    parts.left.position.set(u(L.x), cy, 0.05);
    parts.right.position.set(u(L.x + L.w), cy, 0.05);
    parts.left.scale.setScalar(k);
    parts.right.scale.setScalar(k);

    const cam = camera as THREE.OrthographicCamera;
    cam.zoom = PX;
    cam.position.set(u(L.canvasW) / 2, -u(L.canvasH) / 2, 50);
    cam.lookAt(u(L.canvasW) / 2, -u(L.canvasH) / 2, 0);
    cam.updateProjectionMatrix();
  }, [layout, parts, camera, size]);

  return (
    <>
      <UiLights />
      <primitive object={parts.sheet} />
      <primitive object={parts.left} />
      <primitive object={parts.right} />
    </>
  );
}

/**
 * A parchment scroll that holds a line of text: a Blender model drawn with the town's toon
 * shading, fitted around real HTML text.
 */
export function Scroll({ children, className = "" }: { children: ReactNode; className?: string }) {
  const wrap = useRef<HTMLDivElement>(null);
  const body = useRef<HTMLParagraphElement>(null);
  const [layout, setLayout] = useState<Layout | null>(null);

  useLayoutEffect(() => {
    const measure = () => {
      if (!wrap.current || !body.current) return;
      setLayout({
        x: body.current.offsetLeft + PAD_X,
        y: body.current.offsetTop + PAD_Y,
        w: body.current.offsetWidth,
        h: body.current.offsetHeight,
        canvasW: wrap.current.offsetWidth + PAD_X * 2,
        canvasH: wrap.current.offsetHeight + PAD_Y * 2,
      });
    };
    measure();
    const ro = new ResizeObserver(measure);
    if (body.current) ro.observe(body.current);
    window.addEventListener("resize", measure);
    return () => {
      ro.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, []);

  return (
    <div ref={wrap} className={`scroll ${className}`}>
      {layout && (
        <div
          className="scroll-canvas"
          style={{ left: -PAD_X, top: -PAD_Y, width: layout.canvasW, height: layout.canvasH }}
          aria-hidden="true"
        >
          <Canvas orthographic dpr={[1, 2]} gl={{ antialias: true, alpha: true }} camera={{ near: 1, far: 200, zoom: PX }}>
            <Suspense fallback={null}>
              <ScrollScene layout={layout} />
            </Suspense>
          </Canvas>
        </div>
      )}
      <p ref={body} className="scroll-body">
        {children}
      </p>
    </div>
  );
}

useGLTF.preload(SCROLL_URL, false, false);
