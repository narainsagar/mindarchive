/**
 * Appearance: which palette, and light or dark.
 *
 * Two independent choices, both remembered:
 *
 *   palette   minimal | warm | violet      default: minimal
 *   theme     system  | light | dark       default: system
 *
 * "System" means follow the operating system and keep following it, which is
 * why the choice is stored separately from the theme actually showing. The
 * stylesheet never sees "system": resolveTheme turns it into light or dark and
 * applyTheme stamps that answer on <html>, so every colour is selected by one
 * rule. See project-memory/DECISIONS.md D-014 and D-029.
 *
 * Every storage access is wrapped: `localStorage` throws outright in some
 * contexts (a browser set to block site data, a private window, a preview
 * frame) rather than simply returning nothing.
 */

export type ThemeChoice = "system" | "light" | "dark";
export type ResolvedTheme = "light" | "dark";
export type Palette = "minimal" | "warm" | "violet";

const THEME_KEY = "mindarchive-theme";
const PALETTE_KEY = "mindarchive-palette";

const DARK_QUERY = "(prefers-color-scheme: dark)";

export const THEME_CHOICES: ThemeChoice[] = ["light", "dark", "system"];
export const PALETTES: Palette[] = ["minimal", "warm", "violet"];

/** What each palette is called in the interface. */
export const PALETTE_LABELS: Record<Palette, string> = {
  minimal: "Light minimal",
  warm: "Warm paper",
  violet: "Ink & Violet",
};

/** What each theme choice is called in the interface. */
export const THEME_LABELS: Record<ThemeChoice, string> = {
  light: "Light",
  dark: "Dark",
  system: "System",
};

/**
 * Three colours from each palette, shown as a swatch in the palette menu:
 * the page, a sunken surface, and the accent.
 *
 * Duplicated from styles.css on purpose — a swatch has to be a real colour
 * value in markup, and a custom property cannot be read from a palette that is
 * not currently applied. Keep these in step with the token blocks; they are
 * the light variant of each palette, because the menu shows what a palette
 * *is* rather than what it looks like right now.
 */
export const PALETTE_SWATCHES: Record<Palette, readonly string[]> = {
  minimal: ["#ffffff", "#f6f8fa", "#0b5fbf"],
  warm: ["#fbfaf8", "#f4f2ef", "#6b5b45"],
  violet: ["#ffffff", "#f7f6fa", "#6435cf"],
};

function isThemeChoice(value: unknown): value is ThemeChoice {
  return value === "system" || value === "light" || value === "dark";
}

function isPalette(value: unknown): value is Palette {
  return value === "minimal" || value === "warm" || value === "violet";
}

/**
 * Whether the operating system is asking for dark.
 *
 * Returns false when the browser cannot answer, which keeps light as the
 * fallback everywhere.
 */
export function systemPrefersDark(): boolean {
  try {
    return window.matchMedia(DARK_QUERY).matches;
  } catch {
    return false;
  }
}

/** The theme choice to start with. */
export function getInitialTheme(): ThemeChoice {
  try {
    const stored = window.localStorage.getItem(THEME_KEY);
    if (isThemeChoice(stored)) {
      return stored;
    }
  } catch {
    // Storage unavailable. Follow the system, as a first visit would.
  }

  return "system";
}

/** The palette to start with. */
export function getInitialPalette(): Palette {
  try {
    const stored = window.localStorage.getItem(PALETTE_KEY);
    if (isPalette(stored)) {
      return stored;
    }
  } catch {
    // Storage unavailable.
  }

  return "minimal";
}

/** Turn a choice into the theme that actually shows. */
export function resolveTheme(choice: ThemeChoice): ResolvedTheme {
  if (choice === "system") {
    return systemPrefersDark() ? "dark" : "light";
  }

  return choice;
}

/** Apply a theme choice to the page and remember it. */
export function applyTheme(choice: ThemeChoice): void {
  document.documentElement.setAttribute("data-theme", resolveTheme(choice));

  try {
    window.localStorage.setItem(THEME_KEY, choice);
  } catch {
    // The theme still applies for this visit; it just will not be remembered.
  }
}

/** Apply a palette to the page and remember it. */
export function applyPalette(palette: Palette): void {
  document.documentElement.setAttribute("data-palette", palette);

  try {
    window.localStorage.setItem(PALETTE_KEY, palette);
  } catch {
    // As above: applied now, not remembered.
  }
}

/**
 * Follow the system while the choice is "system".
 *
 * Returns a function that stops watching. Without this, someone on "system"
 * who switches their computer to dark in the evening would keep seeing light
 * until they reloaded.
 */
export function watchSystemTheme(onChange: () => void): () => void {
  let query: MediaQueryList;

  try {
    query = window.matchMedia(DARK_QUERY);
  } catch {
    return () => {};
  }

  // Safari below 14 has no addEventListener on MediaQueryList.
  if (typeof query.addEventListener === "function") {
    query.addEventListener("change", onChange);
    return () => query.removeEventListener("change", onChange);
  }

  if (typeof query.addListener === "function") {
    query.addListener(onChange);
    return () => query.removeListener(onChange);
  }

  return () => {};
}
