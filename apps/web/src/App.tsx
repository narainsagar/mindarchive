import { useCallback, useEffect, useState } from "react";

import { ApiError, fetchConfig, fetchHealth } from "./api";
import type { Health, PublicConfig } from "./api";
import { ArchivePanel } from "./components/ArchivePanel";
import { Header } from "./components/Header";
import { ImportPanel } from "./components/ImportPanel";
import { StatusPanel } from "./components/StatusPanel";
import { applyTheme, getInitialTheme } from "./theme";
import type { Theme } from "./theme";

/**
 * The Mind Archive workspace.
 *
 * One page, no router, no sidebar. There is one view, so there is nothing to
 * navigate between. See docs/project-memory/DECISIONS.md D-008.
 */
export default function App() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);
  const [health, setHealth] = useState<Health | null>(null);
  const [config, setConfig] = useState<PublicConfig | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Bumped after an import so the archive list reloads and shows what arrived.
  const [archiveVersion, setArchiveVersion] = useState(0);

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((current) => (current === "light" ? "dark" : "light"));
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [healthResult, configResult] = await Promise.all([
          fetchHealth(),
          fetchConfig(),
        ]);
        if (cancelled) return;
        setHealth(healthResult);
        setConfig(configResult);
        setError(null);
      } catch (caught) {
        if (cancelled) return;
        setError(
          caught instanceof ApiError
            ? caught.message
            : "Something went wrong reaching Mind Archive.",
        );
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="app">
      <Header theme={theme} onToggleTheme={toggleTheme} />

      <main className="workspace">
        <section className="intro">
          <h2>Your archive, on your computer.</h2>
          <p>
            Mind Archive keeps your AI conversations, notes and files as
            ordinary readable documents that stay yours — whichever AI you use
            next.
          </p>
        </section>

        {error && (
          <div className="message message--error" role="alert">
            <p>{error}</p>
            <p>
              Start it with <code>docker compose up</code>, or run the backend
              directly with{" "}
              <code>uvicorn mind_archive.main:app --reload</code>.
            </p>
          </div>
        )}

        {health && (
          <ArchivePanel key={archiveVersion} />
        )}

        {health && (
          <ImportPanel
            onImported={() => setArchiveVersion((version) => version + 1)}
          />
        )}

        <StatusPanel health={health} config={config} />

        <section className="next">
          <h3>What is coming next</h3>
          <ul>
            <li>Organise it with projects and tags</li>
            <li>Import from Claude, Gemini and others</li>
            <li>Optional backup to storage you choose</li>
          </ul>
        </section>
      </main>

      <footer className="footer">
        <div className="workspace">
          Local first. Privacy first. Yours.
        </div>
      </footer>
    </div>
  );
}
