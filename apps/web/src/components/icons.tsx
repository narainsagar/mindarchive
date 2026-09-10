/**
 * The handful of icons the interface needs, as inline SVG.
 *
 * Not an icon library: these are six small paths, and the project rule is no
 * dependency that cannot be justified in one sentence. They take their colour
 * from `currentColor` so they follow the palette without any extra work.
 *
 * Every one is decorative — the control around it carries the accessible name
 * — so they are all `aria-hidden`.
 */

const base = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
  focusable: false,
};

export function PaletteIcon() {
  return (
    <svg {...base} className="icon">
      <circle cx="12" cy="12" r="9" />
      <circle cx="9" cy="9.5" r="1.4" fill="currentColor" stroke="none" />
      <circle cx="15" cy="9.5" r="1.4" fill="currentColor" stroke="none" />
      <circle cx="12" cy="15" r="1.4" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function SunIcon() {
  return (
    <svg {...base} className="icon">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
  );
}

export function MoonIcon() {
  return (
    <svg {...base} className="icon">
      <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
    </svg>
  );
}

/** "System" — follow the computer. */
export function MonitorIcon() {
  return (
    <svg {...base} className="icon">
      <rect x="2" y="4" width="20" height="13" rx="2" />
      <path d="M8 21h8M12 17v4" />
    </svg>
  );
}

export function MenuIcon() {
  return (
    <svg {...base} className="icon">
      <path d="M3 6h18M3 12h18M3 18h18" />
    </svg>
  );
}

export function CloseIcon() {
  return (
    <svg {...base} className="icon">
      <path d="M18 6L6 18M6 6l12 12" />
    </svg>
  );
}

export function CaretIcon() {
  return (
    <svg {...base} strokeWidth={3} className="icon icon--caret">
      <path d="M6 9l6 6 6-6" />
    </svg>
  );
}

export function TickIcon() {
  return (
    <svg {...base} strokeWidth={3} className="icon icon--tick">
      <path d="M20 6L9 17l-5-5" />
    </svg>
  );
}
