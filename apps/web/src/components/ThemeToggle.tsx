import type { Theme } from "../theme";

interface Props {
  theme: Theme;
  onToggle: () => void;
}

export function ThemeToggle({ theme, onToggle }: Props) {
  const switchingTo = theme === "light" ? "dark" : "light";

  return (
    <button
      type="button"
      className="button"
      onClick={onToggle}
      aria-label={`Switch to ${switchingTo} mode`}
    >
      <span className="button__icon" aria-hidden="true">
        {theme === "light" ? "◐" : "◑"}
      </span>
      {theme === "light" ? "Dark" : "Light"}
    </button>
  );
}
