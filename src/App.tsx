import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useProgress } from "@react-three/drei";
import { PROFILE, SECTIONS, sectionFor, type NpcId } from "./content/portfolio";
import { ErrorBoundary } from "./ErrorBoundary";
import { DayNight } from "./scene/DayNight";
import { Town } from "./scene/Town";
import { outlineUniforms } from "./scene/toon";
import { DialogueBox } from "./ui/DialogueBox";
import { SectionPanel } from "./ui/SectionPanel";

const TARGET: [number, number, number] = [0, 1.2, 0];
const ELEVATION = (37 * Math.PI) / 180;

// ?look=spot_shopkeeper (or any spot_<npc>) frames one NPC up close for review
const params = new URLSearchParams(window.location.search);
const LOOK = params.get("look");
// ?turn=90 starts the town turned by that many degrees, for checking the other sides
const TURN = Number(params.get("turn") ?? 0);

type RigProps = {
  focus: THREE.Vector3 | null;
  /** Screen pixels to push the subject left, to clear the side panel. */
  shiftPx: number;
};

/**
 * Fixed isometric-style camera that eases between framing the whole town and a
 * close-up of whoever you're talking to. Zoom keeps the disc in frame at any size.
 */
function CameraRig({ focus, shiftPx }: RigProps) {
  const { camera, size } = useThree();
  const target = useRef(new THREE.Vector3(...TARGET));
  const goal = useRef(new THREE.Vector3());

  useFrame((_, delta) => {
    // a little tighter on narrow screens, where the disc would otherwise sit small
    const fit = Math.min(size.width / (size.width < 600 ? 25 : 28), size.height / 23);
    const review = LOOK?.startsWith("spot_");
    const zoom = focus ? fit * (LOOK ? (review ? 9 : 3.6) : 2.6) : fit;
    if (focus) goal.current.set(focus.x, focus.y + (review ? 0.6 : 0.75), focus.z);
    else goal.current.set(...TARGET);
    goal.current.x += shiftPx / zoom;

    const k = Math.min(1, delta * 3.5);
    target.current.lerp(goal.current, k);
    camera.zoom += (zoom - camera.zoom) * k;
    const dist = 60;
    const t = target.current;
    camera.position.set(t.x, t.y + Math.sin(ELEVATION) * dist, t.z + Math.cos(ELEVATION) * dist);
    camera.lookAt(t);
    camera.updateProjectionMatrix();
  });
  return null;
}

/** Keeps the outline shader's idea of the screen size in step with the canvas. */
function OutlineResolution() {
  const { size } = useThree();
  useEffect(() => {
    outlineUniforms.uResolution.value.set(size.width, size.height);
    outlineUniforms.uWidth.value = size.width < 600 ? 2 : 3; // thinner ink when the town is drawn small
  }, [size]);
  return null;
}

function LoadingNote() {
  const { active, progress } = useProgress();
  if (!active) return null;
  return <p className="loading">Building the town… {Math.round(progress)}%</p>;
}

const PANEL_WIDTH = 460;

export default function App() {
  const [focus, setFocus] = useState<THREE.Vector3 | null>(null);
  const [active, setActive] = useState<NpcId | null>(null);
  const [panelOpen, setPanelOpen] = useState(false);
  const [wide, setWide] = useState(() => window.innerWidth > 900);
  const section = active ? sectionFor(active) : null;
  const sky = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onResize = () => setWide(window.innerWidth > 900);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const talkTo = useCallback((npc: NpcId) => {
    setActive(npc);
    setPanelOpen(false);
  }, []);
  const leave = useCallback(() => {
    setActive(null);
    setPanelOpen(false);
  }, []);

  return (
    <main className="stage">
      <div ref={sky} className="sky" aria-hidden="true">
        <div className="stars" />
      </div>
      <ErrorBoundary>
        <Canvas
          orthographic
          shadows="percentage"
          dpr={[1, 2]}
          camera={{ near: 1, far: 200 }}
          gl={{ antialias: true }}
          onPointerMissed={() => active && !panelOpen && leave()}
        >
          <CameraRig focus={focus} shiftPx={panelOpen && wide ? PANEL_WIDTH / 2 : 0} />
          <OutlineResolution />
          <DayNight sky={sky} />
          <Suspense fallback={null}>
            <Town focus={LOOK} active={active} onSelect={talkTo} onFocus={setFocus} turn={TURN} />
          </Suspense>
        </Canvas>
        <LoadingNote />
      </ErrorBoundary>

      <header className="overlay">
        <h1>{PROFILE.name}</h1>
        <p className="overlay-role">
          {PROFILE.role} · {PROFILE.school}
        </p>
        <nav aria-label="Portfolio sections">
          {SECTIONS.map((s) => (
            <button
              key={s.npc}
              type="button"
              className={`nav-btn${active === s.npc ? " is-active" : ""}`}
              aria-pressed={active === s.npc}
              onClick={() => talkTo(s.npc)}
            >
              {s.label}
            </button>
          ))}
        </nav>
      </header>

      {!active && (
        <p className="hint">
          <span className="hint-wide">Move toward either edge to turn the town · Click a townsperson to talk</span>
          <span className="hint-touch">Drag to turn the town · Tap a townsperson to talk</span>
        </p>
      )}

      {section && !panelOpen && <DialogueBox section={section} onOpen={() => setPanelOpen(true)} onClose={leave} />}
      {section && panelOpen && <SectionPanel section={section} onClose={leave} />}
    </main>
  );
}
