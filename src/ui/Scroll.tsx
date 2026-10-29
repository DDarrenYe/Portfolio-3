import type { ReactNode } from "react";

/** One rolled end of the scroll: the curl of paper round a rod with brass knobs. */
function ScrollEnd({ side }: { side: "left" | "right" }) {
  return (
    <svg
      className={`scroll-end scroll-end-${side}`}
      viewBox="0 0 30 64"
      width="30"
      height="64"
      aria-hidden="true"
      style={side === "right" ? { transform: "scaleX(-1)" } : undefined}
    >
      {/* rod */}
      <rect x="10" y="4" width="8" height="56" rx="3" fill="#7d8594" stroke="#2a2d3a" strokeWidth="2.5" />
      {/* rolled paper */}
      <rect x="7" y="10" width="17" height="44" rx="7" fill="#d8b46e" stroke="#2a2d3a" strokeWidth="2.5" />
      <path d="M24 16 C 18 18, 18 46, 24 48" fill="none" stroke="#a9813f" strokeWidth="2" />
      {/* curl where the paper leaves the roll */}
      <path d="M24 10 C 30 10, 30 18, 24 18" fill="#eed6a0" stroke="#2a2d3a" strokeWidth="2" />
      <path d="M24 46 C 30 46, 30 54, 24 54" fill="#eed6a0" stroke="#2a2d3a" strokeWidth="2" />
      {/* brass knobs */}
      <rect x="7.5" y="1" width="13" height="7" rx="3" fill="#c9a25a" stroke="#2a2d3a" strokeWidth="2" />
      <rect x="7.5" y="56" width="13" height="7" rx="3" fill="#c9a25a" stroke="#2a2d3a" strokeWidth="2" />
    </svg>
  );
}

/** A parchment scroll that holds a line of text, with a rolled end on each side. */
export function Scroll({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`scroll ${className}`}>
      <ScrollEnd side="left" />
      <p className="scroll-body">{children}</p>
      <ScrollEnd side="right" />
    </div>
  );
}
