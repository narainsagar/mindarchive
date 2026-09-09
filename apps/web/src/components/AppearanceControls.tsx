import { SegmentedControl } from "./SegmentedControl";
import {
  PALETTE_LABELS,
  PALETTES,
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

/** How Mind Archive looks: which palette, and light or dark. */
export function AppearanceControls({
  palette,
  theme,
  onPaletteChange,
  onThemeChange,
}: Props) {
  return (
    <div className="appearance">
      <SegmentedControl
        legend="Palette"
        name="palette"
        value={palette}
        options={PALETTES}
        labels={PALETTE_LABELS}
        onChange={onPaletteChange}
      />
      <SegmentedControl
        legend="Theme"
        name="theme"
        value={theme}
        options={THEME_CHOICES}
        labels={THEME_LABELS}
        onChange={onThemeChange}
      />
    </div>
  );
}
