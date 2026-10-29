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

/**
 * A toon cloud in three tones, like the town's cel shading: each puff is mid blue-grey with a
 * white lit cap toward the sun (top left), and a deeper blue band runs along the underside.
 * One ink outline goes round the whole shape.
 */
function Cloud({ width }: { width: number }) {
  const clip = useId().replace(/:/g, ""); // React ids contain colons, which break url(#id)
  // shapes go straight into the clipPath: SVG ignores a <g> inside one
  const shapes = (grow: number, fill: string) => (
    <>
      {PUFFS.map(([x, y, r], i) => (
        <circle key={i} cx={x} cy={y} r={r + grow} fill={fill} />
      ))}
      <rect x={BASE.x - grow} y={BASE.y - grow} width={BASE.w + grow * 2} height={BASE.h + grow * 2} rx={13 + grow} fill={fill} />
    </>
  );
  return (
    <svg viewBox="-4 -4 208 98" width={width} aria-hidden="true">
      <defs>
        <clipPath id={clip}>{shapes(0, "#fff")}</clipPath>
      </defs>
      {shapes(3, "#2a2d3a")}
      <g clipPath={`url(#${clip})`}>
        {/* shade tone fills the cloud */}
        <rect x="-4" y="-4" width="208" height="98" fill="#cfdff0" />
        {/* lit caps: each puff's white highlight, nudged up and left toward the sun */}
        {PUFFS.map(([x, y, r], i) => (
          <circle key={i} cx={x - r * 0.18} cy={y - r * 0.24} r={r * 0.86} fill="#ffffff" />
        ))}
        {/* deep shade along the base */}
        <ellipse cx="100" cy="88" rx="96" ry="15" fill="#a9c3e0" />
        {/* thin crescent lines where puffs overlap, like the reference's hand-drawn folds */}
        {PUFFS.slice(1, 4).map(([x, y, r], i) => (
          <path
            key={i}
            d={`M ${x - r * 0.75} ${y + r * 0.35} A ${r} ${r} 0 0 0 ${x + r * 0.2} ${y + r * 0.82}`}
            fill="none"
            stroke="#9fb8d4"
            strokeWidth="2"
            strokeLinecap="round"
          />
        ))}
      </g>
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
