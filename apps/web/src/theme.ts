/**
 * Light or dark.
 *
 * Light is the default. With no stored choice we follow the system preference,
 * falling back to light. See docs/project-memory/DECISIONS.md D-014.
 */

export type Theme = "light" | "dark";

const STORAGE_KEY = "mind-archive-theme";

/**
 * The theme to start with.
 *
 * Every storage access is wrapped: `localStorage` throws outright in some
 * contexts (a browser set to block site data, a private window, a preview
 * frame) rather than simply returning nothing.
 */
export function getInitialTheme(): Theme {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === "light" || stored === "dark") {
      return stored;
    }
  } catch {
    // Storage unavailable. Fall through to the system preference.
  }

  try {
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
  } catch {
    // matchMedia unavailable. Fall through to the default.
  }

  return "light";
}

/** Apply a theme to the page and remember it. */
export function applyTheme(theme: Theme): void {
  document.documentElement.setAttribute("data-theme", theme);

  try {
    window.localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // The theme still applies for this visit; it just will not be remembered.
  }
}
