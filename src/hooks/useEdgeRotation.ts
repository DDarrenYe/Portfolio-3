import { useEffect, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import type * as THREE from "three";

export const MAX_SPEED = 0.6; // rad/s at the very edge of the screen
const DEAD_ZONE = 0.15; // half-width of the still band, as a fraction of the half-screen (middle 30%)
const RESPONSE = 4; // how quickly speed follows the mouse; higher is snappier

const smoothstep = (e0: number, e1: number, x: number) => {
  const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0)));
  return t * t * (3 - 2 * t);
};

/**
 * Turning speed (rad/s around +Y) for a horizontal mouse position nx in [-1, 1].
 * Mouse right spins the town clockwise seen from above (negative), mouse left counter-clockwise.
 */
export const speedFor = (nx: number) => -Math.sign(nx) * MAX_SPEED * smoothstep(DEAD_ZONE, 1, Math.abs(nx));

/**
 * Turns a group around Y from the mouse's horizontal position: still in the middle,
 * faster toward either edge. Touch drags spin it with inertia, and the arrow keys
 * turn it too. Edge-hover is off when the viewer prefers reduced motion.
 */
export function useEdgeRotation(group: React.RefObject<THREE.Group>, enabled = true) {
  const state = useRef({ target: 0, vel: 0, dragging: false, lastX: 0, lastT: 0, keys: 0 });
  const on = useRef(enabled);
  on.current = enabled;

  useEffect(() => {
    const s = state.current;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");

    const onMove = (e: PointerEvent) => {
      if (s.dragging && group.current) {
        const now = performance.now();
        const d = ((e.clientX - s.lastX) / window.innerWidth) * Math.PI;
        group.current.rotation.y += d;
        s.vel = d / Math.max(0.016, (now - s.lastT) / 1000);
        s.lastX = e.clientX;
        s.lastT = now;
        return;
      }
      if (e.pointerType !== "mouse" || reduce.matches || s.keys) return;
      s.target = speedFor((e.clientX / window.innerWidth) * 2 - 1);
    };
    const onDown = (e: PointerEvent) => {
      // only drags that start on the town itself, not on the dialogue, panel or nav
      if (e.pointerType === "mouse" || !on.current || !(e.target instanceof HTMLCanvasElement)) return;
      s.dragging = true;
      s.lastX = e.clientX;
      s.lastT = performance.now();
      s.target = 0;
    };
    const onUp = () => {
      s.dragging = false;
    };
    const onLeave = () => {
      s.target = 0;
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      const dir = e.key === "ArrowRight" ? 1 : -1;
      if (e.type === "keydown") {
        if (!on.current) return;
        s.keys = dir;
        s.target = -dir * MAX_SPEED; // same way round as the mouse: right arrow spins clockwise
      } else if (s.keys === dir) {
        s.keys = 0;
        s.target = 0;
      }
    };

    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerdown", onDown);
    window.addEventListener("pointerup", onUp);
    window.addEventListener("pointercancel", onUp);
    document.documentElement.addEventListener("pointerleave", onLeave);
    window.addEventListener("blur", onLeave);
    window.addEventListener("keydown", onKey);
    window.addEventListener("keyup", onKey);
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerdown", onDown);
      window.removeEventListener("pointerup", onUp);
      window.removeEventListener("pointercancel", onUp);
      document.documentElement.removeEventListener("pointerleave", onLeave);
      window.removeEventListener("blur", onLeave);
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("keyup", onKey);
    };
  }, [group]);

  useFrame((_, delta) => {
    const s = state.current;
    if (!group.current || s.dragging) return;
    const dt = Math.min(delta, 0.05);
    const target = enabled ? s.target : 0;
    s.vel += (target - s.vel) * Math.min(1, dt * RESPONSE);
    group.current.rotation.y += s.vel * dt;
  });
}
