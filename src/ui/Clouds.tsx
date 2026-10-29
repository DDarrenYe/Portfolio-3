import { useId } from "react";

// puffs that make up one cloud: [cx, cy, r] in a 200 x 90 box
const PUFFS: [number, number, number][] = [
  [48, 56, 26],
  [82, 40, 32],
  [122, 44, 30],
  [154, 57, 22],
  [28, 64, 16],
];
const BASE = { x: 28, y: 52, w: 138, h: 26 };

/** A toon cloud: white puffs with one ink outline round the whole shape and a pale blue underside. */
function Cloud({ width }: { width: number }) {
  const clip = useId();
  const shapes = (grow: number, fill: string) => (
    <g fill={fill}>
      {PUFFS.map(([x, y, r], i) => (
        <circle key={i} cx={x} cy={y} r={r + grow} />
      ))}
      <rect x={BASE.x - grow} y={BASE.y - grow} width={BASE.w + grow * 2} height={BASE.h + grow * 2} rx={13 + grow} />
    </g>
  );
  return (
    <svg viewBox="-4 -4 208 98" width={width} aria-hidden="true">
      <defs>
        <clipPath id={clip}>{shapes(0, "#fff")}</clipPath>
      </defs>
      {shapes(3, "#2a2d3a")}
      {shapes(0, "#ffffff")}
      <ellipse cx="96" cy="84" rx="92" ry="17" fill="#d4e5f6" clipPath={`url(#${clip})`} />
    </svg>
  );
}

// top (% of the sky), width (px), seconds to cross the screen, and a head start so they begin spread out
const CLOUDS = [
  { top: 6, width: 230, secs: 150, start: -25 },
  { top: 17, width: 150, secs: 115, start: -80 },
  { top: 3, width: 180, secs: 175, start: -125 },
  { top: 27, width: 120, secs: 100, start: -45 },
  { top: 12, width: 270, secs: 200, start: -160 },
  { top: 33, width: 170, secs: 135, start: -105 },
];

/** Clouds drifting slowly across the back of the sky. DayNight fades them at night through --day. */
export function Clouds() {
  return (
    <div className="clouds">
      {CLOUDS.map((c, i) => (
        <div
          key={i}
          className="cloud"
          style={{ top: `${c.top}%`, animationDuration: `${c.secs}s`, animationDelay: `${c.start}s` }}
        >
          <Cloud width={c.width} />
        </div>
      ))}
    </div>
  );
}
