import { Suspense, useEffect, useState } from "react";
import * as THREE from "three";
import { Canvas, useThree } from "@react-three/fiber";
import { useProgress } from "@react-three/drei";
import { ErrorBoundary } from "./ErrorBoundary";
import { Town } from "./scene/Town";
import { outlineUniforms } from "./scene/toon";

const TARGET: [number, number, number] = [0, 1.2, 0];
const ELEVATION = (37 * Math.PI) / 180;

// ?look=house_showcase or ?look=spot_shopkeeper frames a single asset for review
const LOOK = new URLSearchParams(window.location.search).get("look");

/** Fixed isometric-style camera; zoom keeps the whole disc in frame at any window size. */
function CameraRig({ focus }: { focus: THREE.Vector3 | null }) {
  const { camera, size } = useThree();
  useEffect(() => {
    const dist = 60;
    const t = focus ? [focus.x, focus.y + (LOOK?.startsWith("spot_") ? 0.6 : 1.4), focus.z] : TARGET;
    camera.position.set(t[0], t[1] + Math.sin(ELEVATION) * dist, t[2] + Math.cos(ELEVATION) * dist);
    camera.lookAt(t[0], t[1], t[2]);
    const fit = Math.min(size.width / 28, size.height / 23);
    camera.zoom = focus ? fit * (LOOK?.startsWith("spot_") ? 9 : 3.6) : fit;
    camera.updateProjectionMatrix();
  }, [camera, size, focus]);
  return null;
}

/** Keeps the outline shader's idea of the screen size in step with the canvas. */
function OutlineResolution() {
  const { size } = useThree();
  useEffect(() => {
    outlineUniforms.uResolution.value.set(size.width, size.height);
  }, [size]);
  return null;
}

function LoadingNote() {
  const { active, progress } = useProgress();
  if (!active) return null;
  return <p className="loading">Building the town… {Math.round(progress)}%</p>;
}

function Lights() {
  return (
    <>
      {/* cool fill: anything out of the sun goes dusty blue, like the reference */}
      <hemisphereLight args={["#e4ecf8", "#6f93c8", 1.9]} />
      <directionalLight
        color="#fff3dc"
        intensity={2.4}
        position={[10, 18, 12]}
        castShadow
        shadow-mapSize={[4096, 4096]}
        shadow-camera-left={-16}
        shadow-camera-right={16}
        shadow-camera-top={16}
        shadow-camera-bottom={-16}
        shadow-camera-near={1}
        shadow-camera-far={60}
        shadow-bias={-0.0006}
        shadow-normalBias={0.03}
      />
    </>
  );
}

export default function App() {
  const [focus, setFocus] = useState<THREE.Vector3 | null>(null);
  return (
    <main className="stage">
      <ErrorBoundary>
        <Canvas orthographic shadows="percentage" dpr={[1, 2]} camera={{ near: 1, far: 200 }} gl={{ antialias: true }}>
          <CameraRig focus={focus} />
          <OutlineResolution />
          <Lights />
          <Suspense fallback={null}>
            <Town focus={LOOK} onFocus={setFocus} />
          </Suspense>
        </Canvas>
        <LoadingNote />
      </ErrorBoundary>
      <header className="overlay">
        <h1>Castle Hill</h1>
        <p>Blockout preview · move the mouse toward either edge to turn the town</p>
      </header>
    </main>
  );
}
