import { useEffect, useRef } from "react";
import { PROFILE, PROJECTS, SKILLS, TRIPS, type Link, type Section } from "../content/portfolio";
import { NpcIcon } from "./NpcIcon";

function Links({ links }: { links: Link[] }) {
  if (!links.length) return null;
  return (
    <p className="panel-links">
      {links.map((l) => (
        <a key={l.href} href={l.href} target="_blank" rel="noreferrer">
          {l.label} ↗
        </a>
      ))}
    </p>
  );
}

function About() {
  return (
    <>
      <p className="panel-lede">
        Hi, I'm {PROFILE.name}, an {PROFILE.role} at the {PROFILE.school}.
      </p>
      <p>
        {PROFILE.mission} That might be learning a new language, training for a race, or showing your own thinking when
        you write with AI. Each project in the shop started from a goal like that.
      </p>
      <p>
        When I'm not building, I'm travelling. Ask the adventurer by the guild hall about that, or visit the shopkeeper at
        the market stall to see what I've made.
      </p>
      <Links links={[{ label: "GitHub", href: PROFILE.github }]} />
    </>
  );
}

function Projects() {
  return (
    <ul className="wares">
      {PROJECTS.map((p) => (
        <li key={p.name} className="ware">
          <header>
            <h3>{p.name}</h3>
            {p.note && <span className="chip chip-quiet">{p.note}</span>}
          </header>
          <p className="ware-tagline">{p.tagline}</p>
          <p>{p.summary}</p>
          <ul className="ware-highlights">
            {p.highlights.map((h) => (
              <li key={h}>{h}</li>
            ))}
          </ul>
          <p className="chips">
            {p.stack.map((s) => (
              <span key={s} className="chip">
                {s}
              </span>
            ))}
          </p>
          <Links links={p.links} />
        </li>
      ))}
    </ul>
  );
}

function Skills() {
  return (
    <>
      <p>Languages and tools from my projects, plus the ones I've used in my studies.</p>
      {SKILLS.map((g) => (
        <div key={g.group} className="skill-group">
          <h3>{g.group}</h3>
          <p className="chips">
            {g.items.map((s) => (
              <span key={s} className="chip">
                {s}
              </span>
            ))}
          </p>
        </div>
      ))}
    </>
  );
}

function Education() {
  return (
    <>
      <div className="scroll-card">
        <h3>{PROFILE.school}</h3>
        <p>IT Management</p>
      </div>
      <p>
        My studies sit where technology meets the people and organisations who use it, which is where I like to build.
      </p>
      <p>
        For the INFOMGMT 399 capstone, my team built Pentimento, a tool that shows the thinking behind AI-assisted essays.
        You'll find it on the shopkeeper's shelf.
      </p>
      <Links links={[{ label: "Pentimento", href: "https://days-capstone.vercel.app" }]} />
    </>
  );
}

const photoUrl = (src: string) => `${import.meta.env.BASE_URL}adventures/${src}`;

function Adventures() {
  return (
    <>
      <p className="panel-lede">I love travelling: new places, new people and new ideas to bring home and build.</p>
      {TRIPS.map((t) => (
        <section key={t.when} className="trip">
          <header className="trip-head">
            <span className="trip-when">{t.when}</span>
            <h3>{t.country}</h3>
            <p className="chips">
              {t.cities.map((c) => (
                <span key={c} className="chip">
                  {c}
                </span>
              ))}
            </p>
          </header>
          <p>{t.story}</p>
          <div className="photos">
            {t.photos.map((ph) => (
              <figure key={ph.src} className="photo">
                <img src={photoUrl(ph.src)} alt={ph.alt} loading="lazy" decoding="async" width="900" height="1200" />
                <figcaption>{ph.caption}</figcaption>
              </figure>
            ))}
          </div>
        </section>
      ))}
      <p>Every finished project is a quest completed too. The full quest log lives on GitHub.</p>
      <Links links={[{ label: "Quest log on GitHub", href: PROFILE.github }]} />
    </>
  );
}

const BODIES = { king: About, shopkeeper: Projects, blacksmith: Skills, wizard: Education, adventurer: Adventures };

type Props = { section: Section; onClose: () => void };

/** The full portfolio section, opened from an NPC's dialogue. */
export function SectionPanel({ section, onClose }: Props) {
  const close = useRef<HTMLButtonElement>(null);
  const Body = BODIES[section.npc];

  useEffect(() => {
    close.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [section, onClose]);

  return (
    <aside className="panel" role="dialog" aria-labelledby="panel-title">
      <header className="panel-head">
        <div className="panel-badge">
          <NpcIcon npc={section.npc} />
        </div>
        <div>
          <span className="panel-eyebrow">{section.speaker}</span>
          <h2 id="panel-title">{section.title}</h2>
        </div>
        <button ref={close} type="button" className="panel-close" onClick={onClose} aria-label="Close and return to the town">
          ✕
        </button>
      </header>
      <div className="panel-body">
        <Body />
      </div>
    </aside>
  );
}
