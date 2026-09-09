import { AppearanceControls } from "./AppearanceControls";
import { SectionNav } from "./SectionNav";
import type { Section } from "./SectionNav";
import type { Palette, ThemeChoice } from "../theme";

interface Props {
  palette: Palette;
  theme: ThemeChoice;
  onPaletteChange: (palette: Palette) => void;
  onThemeChange: (theme: ThemeChoice) => void;
  /** Omitted while the backend is unreachable — there is nothing to jump to. */
  sections?: readonly Section[];
  navAction?: React.ReactNode;
}

export function Header({
  palette,
  theme,
  onPaletteChange,
  onThemeChange,
  sections,
  navAction,
}: Props) {
  return (
    <header className="header">
      <div className="header__inner">
        <div>
          <h1 className="header__title">Mind Archive</h1>
          <p className="header__tagline">Own your AI memory.</p>
        </div>
        <AppearanceControls
          palette={palette}
          theme={theme}
          onPaletteChange={onPaletteChange}
          onThemeChange={onThemeChange}
        />
      </div>

      {sections && sections.length > 0 && (
        <div className="header__nav">
          <div className="header__nav-inner">
            <SectionNav sections={sections} action={navAction} />
          </div>
        </div>
      )}
    </header>
  );
}
