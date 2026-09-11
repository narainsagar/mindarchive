import { useCallback, useEffect, useState } from "react";

import { ApiError, fetchConfig, fetchHealth } from "./api";
import type { Health, PublicConfig } from "./api";
import { ArchivePanel } from "./components/ArchivePanel";
import { BackToTop } from "./components/BackToTop";
import { ContributePanel } from "./components/ContributePanel";
import { ExportPanel } from "./components/ExportPanel";
import { Header } from "./components/Header";
import { ImportButton } from "./components/ImportButton";
import { ImportPanel } from "./components/ImportPanel";
import { Modal } from "./components/Modal";
import { NextPanel } from "./components/NextPanel";
import { SiteFooter } from "./components/SiteFooter";
import { StatusPanel } from "./components/StatusPanel";
import { SupportPanel } from "./components/SupportPanel";
import { useInbox } from "./useInbox";
import {
  applyPalette,
  applyTheme,
  getInitialPalette,
  getInitialTheme,
  watchSystemTheme,
} from "./theme";
import type { Palette, ThemeChoice } from "./theme";

/**
 * The parts of the page the header can jump to.
 *
 * In-page anchors, not routes — there is still one view. See D-008, extended
 * by D-030.
 */
const SECTIONS = [
  { id: "top", label: "Home", href: "/" },
  { id: "archive", label: "Archive" },
  { id: "next", label: "Coming next" },
  { id: "status", label: "Status" },
  { id: "support", label: "Support" },
  { id: "contribute", label: "Contribute" },
] as const;

/**
 * The Mind Archive workspace.
 *
 * One page, no router, no sidebar. There is one view; the header nav moves
 * within it rather than between views. See project-memory/DECISIONS.md
 * D-008 and D-030.
 */
export default function App() {
  const [theme, setTheme] = useState<ThemeChoice>(getInitialTheme);
  const [palette, setPalette] = useState<Palette>(getInitialPalette);
  const [importOpen, setImportOpen] = useState(false);
  const [exportTotal, setExportTotal] = useState<number | null>(null);
  /** Reported by ArchivePanel; the header's Export button needs the count. */
  const [archiveTotal, setArchiveTotal] = useState(0);
  const [health, setHealth] = useState<Health | null>(null);
  const [config, setConfig] = useState<PublicConfig | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Bumped after an import so the archive list reloads and shows what arrived.
  const [archiveVersion, setArchiveVersion] = useState(0);

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  useEffect(() => {
    applyPalette(palette);
  }, [palette]);

  const inbox = useInbox();
  const waiting = inbox.status?.waiting ?? 0;

  const openImport = useCallback(() => setImportOpen(true), []);
  const closeImport = useCallback(() => {
    setImportOpen(false);
    // Whatever happened in there may have emptied the inbox folder.
    void inbox.refresh();
  }, [inbox]);

  // On "system", keep following the computer rather than freezing at whatever
  // it said when the page loaded.
  useEffect(() => {
    if (theme !== "system") return;

    return watchSystemTheme(() => applyTheme("system"));
  }, [theme]);

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
      <Header
        palette={palette}
        theme={theme}
        onPaletteChange={setPalette}
        onThemeChange={setTheme}
        sections={health ? SECTIONS : undefined}
        actions={
          health ? (
            <>
              <ImportButton waiting={waiting} onClick={openImport} />
              <button
                type="button"
                className="button"
                onClick={() => setExportTotal(archiveTotal)}
              >
                Export
              </button>
            </>
          ) : undefined
        }
      />

      <main className="workspace">
        <section className="intro" id="top">
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
          <ArchivePanel
            key={archiveVersion}
            id="archive"
            onTotalChange={setArchiveTotal}
          />
        )}

        <NextPanel id="next" />

        <StatusPanel health={health} config={config} id="status" />

        <SupportPanel id="support" />

        <ContributePanel id="contribute" />
      </main>

      <Modal open={importOpen} title="Import" onClose={closeImport}>
        <ImportPanel
          inbox={inbox}
          onImported={() => setArchiveVersion((version) => version + 1)}
        />
      </Modal>

      <Modal
        open={exportTotal !== null}
        title="Export everything"
        onClose={() => setExportTotal(null)}
      >
        <ExportPanel total={exportTotal ?? 0} />
      </Modal>

      <SiteFooter />

      {/* Fixed to the viewport, so it sits outside the flow of the page. */}
      <BackToTop />
    </div>
  );
}
