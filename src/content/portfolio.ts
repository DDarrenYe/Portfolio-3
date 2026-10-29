// Everything the townsfolk say and show. Edit this file to change the portfolio's words.

export type NpcId = "king" | "shopkeeper" | "blacksmith" | "wizard" | "adventurer";

export type Link = { label: string; href: string };

export const PROFILE = {
  name: "Darren Ye",
  role: "IT Management student",
  school: "University of Auckland",
  mission: "I build programs that bridge people with their goals.",
  github: "https://github.com/DDarrenYe",
};

export type Section = {
  npc: NpcId;
  /** The NPC's name on their dialogue box and name tag. */
  speaker: string;
  /** Short label for the nav and the panel heading. */
  label: string;
  title: string;
  /** What the NPC says, one line per click. */
  lines: string[];
  /** The button that opens the full section. */
  cta: string;
};

// Order here is the order of the nav buttons.
export const SECTIONS: Section[] = [
  {
    npc: "king",
    speaker: "The King",
    label: "About",
    title: "About Darren",
    lines: [
      "Welcome, traveller, to my realm!",
      "This realm belongs to Darren Ye, an IT Management student at the University of Auckland.",
      "He builds programs that bridge people with their goals. Shall I tell you more of him?",
    ],
    cta: "Tell me about Darren",
  },
  {
    npc: "shopkeeper",
    speaker: "Shopkeeper",
    label: "Projects",
    title: "Projects",
    lines: [
      "Welcome, welcome! Finest wares in the land!",
      "On the shelves today: INBTWN, Pacer and Pentimento. Each one built to help someone reach a goal.",
    ],
    cta: "Browse the wares",
  },
  {
    npc: "blacksmith",
    speaker: "Blacksmith",
    label: "Skills",
    title: "Skills",
    lines: [
      "Mind the sparks!",
      "Every tool on this rack was forged in Darren's own projects. TypeScript, Python, Swift, SQL, and plenty more besides.",
    ],
    cta: "See the tools",
  },
  {
    npc: "wizard",
    speaker: "Wizard",
    label: "Education",
    title: "Education",
    lines: [
      "Ah, a seeker of knowledge.",
      "Darren studies IT Management at the University of Auckland. For his capstone, he and his team built Pentimento.",
    ],
    cta: "Read the scrolls",
  },
  {
    npc: "adventurer",
    speaker: "Adventurer",
    label: "Adventures",
    title: "Adventures",
    lines: [
      "Hey there, fellow traveller!",
      "Darren loves to travel. In July 2025 his crew explored Seoul and Busan in South Korea.",
      "Then in November it was Guangzhou and Beijing in China. Want to see the photos?",
    ],
    cta: "See the adventures",
  },
];

export const sectionFor = (npc: NpcId) => SECTIONS.find((s) => s.npc === npc)!;

export type Project = {
  name: string;
  /** App icon, from public/projects/. */
  icon: string;
  tagline: string;
  summary: string;
  highlights: string[];
  stack: string[];
  links: Link[];
  note?: string;
};

export const PROJECTS: Project[] = [
  {
    name: "INBTWN",
    icon: "inbtwn.png",
    tagline: "Learn a language by talking, not tapping",
    summary:
      "An iOS language-learning app where every lesson is a conversation with an AI tutor in the language you're learning. Mandarin is the first language, and Toto the mascot is your conversation partner.",
    highlights: [
      "Each session ends in a scorecard for fluency, clarity, vocabulary, grammar and task completion",
      "Switch between an offline practice tutor, Claude and ChatGPT, all behind one tutor service",
      "The lesson engine, scoring and streaks live in a Swift package with no UI code, ready for an Android version",
    ],
    stack: ["Swift", "SwiftUI", "Swift Package Manager", "iOS 17", "GitHub Actions"],
    links: [],
    note: "Private repository · in development",
  },
  {
    name: "Pacer",
    icon: "pacer.svg",
    tagline: "Running analytics that tell you what to work on",
    summary:
      "Connect Strava or upload a GPX file to see km splits, how much you fade, best efforts, weekly trends and predicted race times. Set a race goal and Pacer shows where your trend puts you on race day.",
    highlights: [
      "Race predictions from three methods, each scored for accuracy on held-out runs",
      "Age and sex comparisons from 5k to marathon, plus a runner card with your rank and runner title",
      "Read-only demo account, so anyone can try it without signing up",
    ],
    stack: ["Python", "FastAPI", "pandas", "statsmodels", "PostgreSQL", "React", "TypeScript", "Chart.js", "Playwright"],
    links: [
      { label: "Try the demo", href: "https://training-analytics-tool.vercel.app" },
      { label: "API docs", href: "https://run-analytics-api.onrender.com/docs" },
    ],
  },
  {
    name: "Pentimento",
    icon: "pentimento.svg",
    tagline: "Showing the thinking behind AI-assisted essays",
    summary:
      "Our INFOMGMT 399 capstone. Students import their AI chats, critique each step with three questions and submit the final essay. Instructors see which parts match the logged AI answers, read the reflection checks, leave feedback and export PDF or CSV reports.",
    highlights: [
      "Imports ChatGPT share links or pasted chats into a step-by-step log",
      "An LLM reflection check runs on submit, and instructors can dismiss flags or add them to feedback",
      "Role-based student and instructor views on Supabase, with a review queue first",
    ],
    stack: ["TypeScript", "Next.js", "Tailwind CSS", "Drizzle ORM", "Supabase", "Vercel AI SDK"],
    links: [
      { label: "Open the app", href: "https://days-capstone.vercel.app" },
      { label: "Code", href: "https://github.com/DDarrenYe/DAYS-Capstone" },
    ],
    note: "Team project",
  },
];

export const SKILLS: { group: string; items: string[] }[] = [
  { group: "Languages", items: ["TypeScript", "JavaScript", "Python", "Swift", "SQL", "R", "C", "Java", "HTML & CSS"] },
  { group: "Frameworks", items: ["React", "Next.js", "SwiftUI", "FastAPI", "Tailwind CSS", "Three.js"] },
  { group: "Data", items: ["PostgreSQL", "Supabase", "pandas", "NumPy", "statsmodels", "RStudio"] },
  { group: "Tools", items: ["Git", "GitHub Actions", "Vercel", "Render", "pytest", "Playwright", "Blender"] },
];

export type Photo = { src: string; alt: string; caption: string };

export type Trip = { when: string; country: string; cities: string[]; story: string; photos: Photo[] };

// Photos live in public/adventures/.
export const TRIPS: Trip[] = [
  {
    when: "July 2025",
    country: "South Korea",
    cities: ["Seoul", "Busan"],
    story:
      "We spent July in South Korea, starting in Seoul and heading south to Busan. Highlights were dressing up in hanbok for Gyeongbokgung Palace, wandering Seoul's side streets, and looking out over the city lights at night.",
    photos: [
      {
        src: "seoul-hanbok.webp",
        alt: "Darren and two friends in dark hanbok robes with prop swords, arms crossed, by the pond at Gyeongbokgung Palace with a mountain behind",
        caption: "Hanbok at Gyeongbokgung Palace, Seoul",
      },
      {
        src: "seoul-street.webp",
        alt: "Darren smiling in the middle of a narrow Seoul street lined with shops, signs and overhead power lines",
        caption: "Exploring the streets of Seoul",
      },
      {
        src: "seoul-night.webp",
        alt: "Darren in a cap in front of Seoul's skyline lit up at night",
        caption: "Seoul by night",
      },
    ],
  },
  {
    when: "November 2025",
    country: "China",
    cities: ["Guangzhou", "Beijing"],
    story:
      "In November we went to China, from Guangzhou in the south up to Beijing. Cold, clear skies made for great days at the Great Wall and the Summer Palace.",
    photos: [
      {
        src: "great-wall.webp",
        alt: "Darren in a beanie and scarf giving two thumbs up, sitting on steep stone steps of the Great Wall below a watchtower",
        caption: "The Great Wall",
      },
      {
        src: "beijing-summer-palace.webp",
        alt: "The red and green Tower of Buddhist Incense rising above a stone terrace against a deep blue sky, framed by pine branches",
        caption: "Summer Palace, Beijing",
      },
    ],
  },
];
