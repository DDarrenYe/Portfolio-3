import type { ReactNode } from "react";

/** A short iron chain, link by link. */
function Chain() {
  return (
    <svg className="chain" viewBox="0 0 14 40" width="17" height="48" aria-hidden="true">
      {[0, 1, 2, 3].map((i) =>
        i % 2 === 0 ? (
          <rect key={i} x="3" y={i * 9 + 1} width="8" height="12" rx="4" fill="none" stroke="#2a2d3a" strokeWidth="4.5" />
        ) : (
          <rect key={i} x="5.5" y={i * 9 + 1} width="3" height="12" rx="1.5" fill="#2a2d3a" />
        ),
      )}
      {[0, 1, 2, 3].map((i) =>
        i % 2 === 0 ? (
          <rect key={`h${i}`} x="3" y={i * 9 + 1} width="8" height="12" rx="4" fill="none" stroke="#9aa2b1" strokeWidth="2" />
        ) : (
          <rect key={`h${i}`} x="6.25" y={i * 9 + 2} width="1.5" height="10" rx="0.75" fill="#9aa2b1" />
        ),
      )}
    </svg>
  );
}

/**
 * Wooden sign hanging from a weathered beam on two chains, like a tavern sign.
 * Children go on the board.
 */
export function Signpost({ children }: { children: ReactNode }) {
  return (
    <header className="signpost">
      <div className="signpost-post" aria-hidden="true" />
      <div className="signpost-brace" aria-hidden="true" />
      <div className="signpost-arm">
        <div className="signpost-beam" aria-hidden="true">
          <span className="signpost-clamp" />
          <span className="signpost-clamp" />
        </div>
        <div className="signpost-swing">
          <div className="signpost-chains" aria-hidden="true">
            <Chain />
            <Chain />
          </div>
          <div className="sign">
            <div className="sign-frame">
              <div className="sign-board">{children}</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
