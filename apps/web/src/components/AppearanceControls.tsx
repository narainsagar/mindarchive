import { Menu } from "./Menu";
import type { MenuOption } from "./Menu";
import { MonitorIcon, MoonIcon, PaletteIcon, SunIcon } from "./icons";
import {
  PALETTES,
  PALETTE_LABELS,
  PALETTE_SWATCHES,
  THEME_CHOICES,
  THEME_LABELS,
} from "../theme";
import type { Palette, ThemeChoice } from "../theme";

interface Props {
  palette: Palette;
  theme: ThemeChoice;
  onPaletteChange: (palette: Palette) => void;
  onThemeChange: (theme: ThemeChoice) => void;
}

/** The icon for a theme choice, so the trigger shows the current state. */
function themeIcon(choice: ThemeChoice) {
  if (choice === "light") return <SunIcon />;
  if (choice === "dark") return <MoonIcon />;
  return <MonitorIcon />;
}

const paletteOptions: MenuOption<Palette>[] = PALETTES.map((palette) => ({
  value: palette,
  label: PALETTE_LABELS[palette],
  lead: (
    <span className="swatch" aria-hidden="true">
      {PALETTE_SWATCHES[palette].map((colour) => (
        <i key={colour} style={{ background: colour }} />
      ))}
    </span>
  ),
}));

const themeOptions: MenuOption<ThemeChoice>[] = THEME_CHOICES.map((choice) => ({
  value: choice,
  label: THEME_LABELS[choice],
  lead: themeIcon(choice),
}));

/**
 * How Mind Archive looks: which palette, and light or dark.
 *
 * Two menus rather than the segmented rows this used to be (D-037). The theme
 * trigger shows the icon of the current choice, which is what lets it drop its
 * text label on a narrow screen and still read.
 */
export function AppearanceControls({
  palette,
  theme,
  onPaletteChange,
  onThemeChange,
}: Props) {
  return (
    <div className="appearance">
      <Menu
        label="Palette"
        value={palette}
        options={paletteOptions}
        onChange={onPaletteChange}
        icon={<PaletteIcon />}
      />
      <Menu
        label="Theme"
        value={theme}
        options={themeOptions}
        onChange={onThemeChange}
        icon={themeIcon(theme)}
      />
    </div>
  );
}
