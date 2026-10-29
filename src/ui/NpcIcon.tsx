import type { NpcId } from "../content/portfolio";

const INK = "#2a2d3a";

/** Small portrait badge for each NPC: their signature item, drawn in the town's palette. */
export function NpcIcon({ npc }: { npc: NpcId }) {
  return (
    <svg viewBox="0 0 48 48" width="48" height="48" aria-hidden="true">
      {npc === "king" && (
        <>
          <path d="M8 34 L10 14 L18 24 L24 10 L30 24 L38 14 L40 34 Z" fill="#e8b84a" stroke={INK} strokeWidth="2.5" strokeLinejoin="round" />
          <rect x="8" y="34" width="32" height="6" fill="#e8b84a" stroke={INK} strokeWidth="2.5" />
          <circle cx="24" cy="29" r="3" fill="#c4483f" stroke={INK} strokeWidth="2" />
        </>
      )}
      {npc === "shopkeeper" && (
        <>
          <circle cx="24" cy="24" r="15" fill="#e8b84a" stroke={INK} strokeWidth="2.5" />
          <circle cx="24" cy="24" r="10" fill="none" stroke={INK} strokeWidth="2" />
          <path d="M24 17 V31 M20 20.5 H26 A3 3 0 0 1 26 26.5 H21" fill="none" stroke={INK} strokeWidth="2.2" strokeLinecap="round" />
        </>
      )}
      {npc === "blacksmith" && (
        <>
          <rect x="21" y="18" width="6" height="24" rx="2" fill="#7a5236" stroke={INK} strokeWidth="2.5" transform="rotate(35 24 30)" />
          <rect x="10" y="8" width="24" height="12" rx="2" fill="#8a93a6" stroke={INK} strokeWidth="2.5" transform="rotate(35 22 14)" />
        </>
      )}
      {npc === "wizard" && (
        <>
          <path d="M24 5 L33 34 H15 Z" fill="#4f63b0" stroke={INK} strokeWidth="2.5" strokeLinejoin="round" />
          <ellipse cx="24" cy="36" rx="18" ry="5" fill="#3c4d92" stroke={INK} strokeWidth="2.5" />
          <circle cx="22" cy="22" r="2" fill="#e8b84a" />
          <circle cx="27" cy="15" r="1.6" fill="#e8b84a" />
        </>
      )}
      {npc === "adventurer" && (
        <>
          <rect x="22" y="6" width="5" height="26" fill="#b9c2d0" stroke={INK} strokeWidth="2.5" transform="rotate(30 24 24)" />
          <rect x="14" y="30" width="20" height="5" rx="1.5" fill="#e8b84a" stroke={INK} strokeWidth="2.5" transform="rotate(30 24 24)" />
          <rect x="22" y="34" width="5" height="8" fill="#8f5f3a" stroke={INK} strokeWidth="2.5" transform="rotate(30 24 24)" />
        </>
      )}
    </svg>
  );
}
