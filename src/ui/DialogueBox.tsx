import { useEffect, useRef, useState } from "react";
import type { Section } from "../content/portfolio";
import { NpcIcon } from "./NpcIcon";

const CHAR_MS = 22;

type Props = {
  section: Section;
  onOpen: () => void;
  onClose: () => void;
};

/**
 * RPG text box: the NPC's lines type out one at a time. Click, Enter or Space finishes
 * the line or moves to the next; the last line offers the section and a goodbye.
 */
export function DialogueBox({ section, onOpen, onClose }: Props) {
  const [line, setLine] = useState(0);
  const [shown, setShown] = useState(0);
  const reduce = useRef(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  const text = section.lines[line];
  const typing = shown < text.length;
  const last = line === section.lines.length - 1;
  const primary = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    setLine(0);
    setShown(0);
  }, [section]);

  useEffect(() => {
    if (reduce.current) {
      setShown(text.length);
      return;
    }
    if (!typing) return;
    const id = window.setTimeout(() => setShown((n) => n + 1), CHAR_MS);
    return () => window.clearTimeout(id);
  }, [shown, typing, text]);

  useEffect(() => {
    if (!typing && last) primary.current?.focus();
  }, [typing, last]);

  const advance = () => {
    if (typing) setShown(text.length);
    else if (!last) {
      setLine((l) => l + 1);
      setShown(0);
    }
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if ((e.key === "Enter" || e.key === " ") && !(e.target instanceof HTMLButtonElement)) {
        e.preventDefault();
        advance();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  return (
    <section className="dialogue" role="dialog" aria-label={`${section.speaker} says`} onClick={advance}>
      <span className="dialogue-name">{section.speaker}</span>
      <div className="dialogue-portrait">
        <NpcIcon npc={section.npc} />
      </div>
      <p className="dialogue-text" aria-live="polite">
        {text.slice(0, shown)}
        {!typing && !last && <span className="dialogue-caret" aria-hidden="true">▾</span>}
      </p>
      <div className="dialogue-choices">
        {last && !typing ? (
          <>
            <button
              ref={primary}
              type="button"
              className="btn btn-primary"
              onClick={(e) => {
                e.stopPropagation();
                onOpen();
              }}
            >
              {section.cta}
            </button>
            <button
              type="button"
              className="btn"
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
            >
              Goodbye
            </button>
          </>
        ) : (
          <span className="dialogue-hint">{typing ? "Click to skip" : "Click to continue"}</span>
        )}
      </div>
    </section>
  );
}
