import { useEffect, useState } from "react";

export interface Section {
  id: string;
  label: string;
}

interface Props {
  sections: readonly Section[];
  /** Rendered at the end of the row — the Import button lives here. */
  action?: React.ReactNode;
}

/**
 * Jump between the parts of the workspace.
 *
 * These are in-page anchors, not routes. There is still one page and one view
 * — D-008 stands — but the page grew long enough that reaching the bottom of
 * it meant a great deal of scrolling. See D-030.
 *
 * The current section is highlighted as you scroll, which is the whole reason
 * this is worth having over a plain list of links.
 */
export function SectionNav({ sections, action }: Props) {
  const [active, setActive] = useState<string>(sections[0]?.id ?? "");

  useEffect(() => {
    const elements = sections
      .map((section) => document.getElementById(section.id))
      .filter((element): element is HTMLElement => element !== null);

    if (elements.length === 0 || typeof IntersectionObserver === "undefined") {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        // The heading nearest the top of the viewport wins. Taking the first
        // intersecting entry directly would flicker between two sections that
        // are both partly on screen.
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort(
            (a, b) => a.boundingClientRect.top - b.boundingClientRect.top,
          )[0];

        if (visible) setActive(visible.target.id);
      },
      // A band across the upper part of the viewport, so a section becomes
      // "current" when it reaches reading position rather than when it first
      // appears at the bottom.
      { rootMargin: "-96px 0px -55% 0px", threshold: 0 },
    );

    elements.forEach((element) => observer.observe(element));
    return () => observer.disconnect();
  }, [sections]);

  return (
    <nav className="sectionnav" aria-label="Sections of this page">
      <ul className="sectionnav__list">
        {sections.map((section) => (
          <li key={section.id}>
            <a
              href={`#${section.id}`}
              className="sectionnav__link"
              aria-current={active === section.id ? "true" : undefined}
            >
              {section.label}
            </a>
          </li>
        ))}
      </ul>
      {action}
    </nav>
  );
}
