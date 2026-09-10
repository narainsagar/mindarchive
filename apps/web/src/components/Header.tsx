import { useCallback, useEffect, useId, useRef, useState } from "react";

import { AppearanceControls } from "./AppearanceControls";
import { SectionNav } from "./SectionNav";
import type { Section } from "./SectionNav";
import { CloseIcon, MenuIcon } from "./icons";
import type { Palette, ThemeChoice } from "../theme";

interface Props {
  palette: Palette;
  theme: ThemeChoice;
  onPaletteChange: (palette: Palette) => void;
  onThemeChange: (theme: ThemeChoice) => void;
  /** Omitted while the backend is unreachable — there is nothing to jump to. */
  sections?: readonly Section[];
  /** Import and Export. Inline on a wide screen, in the menu on a narrow one. */
  actions?: React.ReactNode;
}

/**
 * One row: brand, navigation, then actions and appearance.
 *
 * The navigation used to sit on a second row that scrolled sideways when it
 * did not fit. It now folds into a menu instead, which is what removes the
 * horizontal scrolling (D-037). The appearance controls never fold — changing
 * how it looks is one tap at every width.
 */
export function Header({
  palette,
  theme,
  onPaletteChange,
  onThemeChange,
  sections,
  actions,
}: Props) {
  const [menuOpen, setMenuOpen] = useState(false);
  const panelId = useId();
  const burgerRef = useRef<HTMLButtonElement>(null);
  const headerRef = useRef<HTMLElement>(null);

  const hasMenu = Boolean((sections && sections.length > 0) || actions);

  const close = useCallback((returnFocus: boolean) => {
    setMenuOpen(false);
    if (returnFocus) burgerRef.current?.focus();
  }, []);

  useEffect(() => {
    if (!menuOpen) return;

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") close(true);
    }
    function onPointerDown(event: MouseEvent) {
      if (!headerRef.current?.contains(event.target as Node)) close(false);
    }
    // Widening past the breakpoint puts the links back in the row; a panel
    // left open over them would be a second copy of the same navigation.
    function onResize() {
      if (window.innerWidth >= 1024) close(false);
    }

    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("mousedown", onPointerDown);
    window.addEventListener("resize", onResize);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("mousedown", onPointerDown);
      window.removeEventListener("resize", onResize);
    };
  }, [menuOpen, close]);

  return (
    <header className="header" ref={headerRef}>
      <div className="header__inner">
        {/* Still an h1. The tagline left the header (D-037), but the page's
            one top-level heading has to stay somewhere, and this is it. */}
        <h1 className="header__title">
          <a
            className="header__brand"
            href="/"
            onClick={(event) => event.preventDefault()}
          >
            Mind Archive
          </a>
        </h1>

        {sections && sections.length > 0 && (
          <SectionNav sections={sections} className="sectionnav--inline" />
        )}

        <span className="header__spacer" />

        <div className="header__actions">
          {actions && <div className="header__actions-wide">{actions}</div>}

          <AppearanceControls
            palette={palette}
            theme={theme}
            onPaletteChange={onPaletteChange}
            onThemeChange={onThemeChange}
          />

          {hasMenu && (
            <button
              type="button"
              ref={burgerRef}
              className="button header__burger"
              aria-expanded={menuOpen}
              aria-controls={menuOpen ? panelId : undefined}
              aria-label={menuOpen ? "Close menu" : "Menu"}
              onClick={() => setMenuOpen((open) => !open)}
            >
              {menuOpen ? <CloseIcon /> : <MenuIcon />}
            </button>
          )}
        </div>
      </div>

      {hasMenu && menuOpen && (
        <div className="header__panel" id={panelId}>
          <div className="header__panel-inner">
            {sections && sections.length > 0 && (
              <SectionNav
                sections={sections}
                className="sectionnav--stacked"
                onNavigate={() => close(false)}
              />
            )}
            {actions && <div className="header__panel-actions">{actions}</div>}
          </div>
        </div>
      )}
    </header>
  );
}
