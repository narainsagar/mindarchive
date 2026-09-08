import type { Theme } from "../theme";
import { ThemeToggle } from "./ThemeToggle";

interface Props {
  theme: Theme;
  onToggleTheme: () => void;
}

export function Header({ theme, onToggleTheme }: Props) {
  return (
    <header className="header">
      <div className="header__inner">
        <div>
          <h1 className="header__title">Mind Archive</h1>
          <p className="header__tagline">Own your AI memory.</p>
        </div>
        <ThemeToggle theme={theme} onToggle={onToggleTheme} />
      </div>
    </header>
  );
}
