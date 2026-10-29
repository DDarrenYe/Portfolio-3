import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { getToon } from "./toon";

export const CYCLE_SECONDS = 180;

// ?phase=0.5 freezes the clock at that point of the cycle (0 = noon, 0.5 = midnight), for reviewing
const PHASE = new URLSearchParams(window.location.search).get("phase");

const smooth = (a: number, b: number, x: number) => {
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
};

/**
 * How dark it is, 0 (day) to 1 (night), for a point in the cycle. Day and night each hold
 * for about 50 seconds, with slow 40 second dusk and dawn transitions between them.
 */
export function nightAt(phase: number) {
  return smooth(0.17, 0.39, phase) - smooth(0.67, 0.89, phase);
}

type Key = { sun: string; sunI: number; sky: string; ground: string; hemiI: number; top: string; bottom: string };

// three looks the cycle blends between: day, the golden middle of dusk/dawn, and night
const DAY: Key = { sun: "#fff3dc", sunI: 2.4, sky: "#e4ecf8", ground: "#6f93c8", hemiI: 1.9, top: "#5fb0ec", bottom: "#c4e6fb" };
const DUSK: Key = { sun: "#ffb27a", sunI: 1.6, sky: "#f0c9b0", ground: "#6a6aa8", hemiI: 1.5, top: "#7f74b0", bottom: "#f4ac7c" };
const NIGHT: Key = { sun: "#9fb6ff", sunI: 0.75, sky: "#5d6fa6", ground: "#28325e", hemiI: 1.1, top: "#121a36", bottom: "#2f3a68" };

const c = (hex: string) => new THREE.Color(hex);
const KEYS = [DAY, DUSK, NIGHT].map((k) => ({
  ...k,
  sunC: c(k.sun),
  skyC: c(k.sky),
  groundC: c(k.ground),
  topC: c(k.top),
  bottomC: c(k.bottom),
}));
const WARM = c("#f2c66a");
const tmp = { sun: new THREE.Color(), sky: new THREE.Color(), ground: new THREE.Color(), top: new THREE.Color(), bottom: new THREE.Color() };

/**
 * Sun, fill light and sky for the day and night cycle. The sky is a DOM element behind the
 * canvas; its colours, star opacity and cloud fade are set here as CSS variables.
 */
export function DayNight({ sky }: { sky: React.RefObject<HTMLDivElement> }) {
  const sun = useRef<THREE.DirectionalLight>(null);
  const hemi = useRef<THREE.HemisphereLight>(null);

  useFrame(({ clock }) => {
    const phase = PHASE !== null ? Number(PHASE) : (clock.elapsedTime / CYCLE_SECONDS) % 1;
    const n = nightAt(phase);
    // day -> dusk over the first half of the transition, dusk -> night over the second
    const [a, b, t] = n < 0.5 ? [KEYS[0], KEYS[1], n * 2] : [KEYS[1], KEYS[2], n * 2 - 1];
    const lerp = (x: number, y: number) => x + (y - x) * t;

    if (sun.current) {
      sun.current.color.copy(tmp.sun.copy(a.sunC).lerp(b.sunC, t));
      sun.current.intensity = lerp(a.sunI, b.sunI);
    }
    if (hemi.current) {
      hemi.current.color.copy(tmp.sky.copy(a.skyC).lerp(b.skyC, t));
      hemi.current.groundColor.copy(tmp.ground.copy(a.groundC).lerp(b.groundC, t));
      hemi.current.intensity = lerp(a.hemiI, b.hemiI);
    }

    // the town lights up as it gets dark: lamps and the forge brighten, windows glow warm
    const lamp = getToon("pal_lamp");
    if (lamp) lamp.emissive.copy(lamp.color).multiplyScalar(0.45 + n * 0.6);
    const ember = getToon("pal_ember");
    if (ember) ember.emissive.copy(ember.color).multiplyScalar(0.3 + n * 0.7);
    const crystal = getToon("pal_crystal");
    if (crystal) crystal.emissive.copy(crystal.color).multiplyScalar(n * 0.6);
    const glass = getToon("pal_glass");
    if (glass) glass.emissive.copy(WARM).multiplyScalar(n * 0.75);

    const el = sky.current;
    if (el) {
      el.style.setProperty("--sky-top", `#${tmp.top.copy(a.topC).lerp(b.topC, t).getHexString()}`);
      el.style.setProperty("--sky-bottom", `#${tmp.bottom.copy(a.bottomC).lerp(b.bottomC, t).getHexString()}`);
      el.style.setProperty("--stars", smooth(0.55, 1, n).toFixed(3));
      el.style.setProperty("--day", (1 - n).toFixed(3)); // clouds fade and darken with this
    }
  });

  return (
    <>
      {/* cool fill: anything out of the sun goes dusty blue, like the reference */}
      <hemisphereLight ref={hemi} args={[DAY.sky, DAY.ground, DAY.hemiI]} />
      <directionalLight
        ref={sun}
        color={DAY.sun}
        intensity={DAY.sunI}
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
