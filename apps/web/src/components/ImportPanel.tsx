import { useRef, useState } from "react";

import { ApiError, importExport } from "../api";
import type { ImportSummary } from "../api";

interface Props {
  onImported?: (summary: ImportSummary) => void;
}

/**
 * Import a provider export.
 *
 * Deliberately one control and one button. The hard part of importing is
 * finding the export file in the first place, so the panel spends its words on
 * that rather than on options nobody needs.
 */
export function ImportPanel({ onImported }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [summary, setSummary] = useState<ImportSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function choose(chosen: File | null) {
    setFile(chosen);
    setSummary(null);
    setError(null);
  }

  async function submit() {
    if (!file || busy) return;

    setBusy(true);
    setSummary(null);
    setError(null);

    try {
      const result = await importExport(file);
      setSummary(result);
      if (result.ok) {
        setFile(null);
        if (inputRef.current) inputRef.current.value = "";
        onImported?.(result);
      }
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Something went wrong during the import.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel" aria-labelledby="import-heading">
      <h2 className="panel__title" id="import-heading">
        Import
      </h2>

      <p className="import__intro">
        Bring in your ChatGPT history. In ChatGPT, go to{" "}
        <strong>Settings → Data controls → Export data</strong>. You will get an
        email with a link; the download is a <code>.zip</code> file.
      </p>

      <div className="import__controls">
        <label className="import__file">
          <span className="visually-hidden">Choose an export file</span>
          <input
            ref={inputRef}
            type="file"
            accept=".zip,.json,application/zip"
            disabled={busy}
            onChange={(event) => choose(event.target.files?.[0] ?? null)}
          />
        </label>

        <button
          type="button"
          className="button button--primary"
          onClick={submit}
          disabled={!file || busy}
        >
          {busy ? "Importing…" : "Import"}
        </button>
      </div>

      {busy && (
        <p className="note" role="status">
          Reading your export. A large one can take a minute — nothing is being
          uploaded anywhere, it is all happening on this computer.
        </p>
      )}

      {error && (
        <p className="message message--error" role="alert">
          {error}
        </p>
      )}

      {summary && !error && (
        <div
          className={`message message--${summary.ok ? "ok" : "error"}`}
          role="status"
        >
          <p>{summary.message}</p>

          {summary.ok && summary.archive_location && (
            <p className="import__location">
              Saved to <code>{summary.archive_location}</code>
            </p>
          )}

          {summary.problems.length > 0 && (
            <details className="import__problems">
              <summary>
                What could not be read ({summary.problems.length})
              </summary>
              <ul>
                {summary.problems.map((problem) => (
                  <li key={problem}>{problem}</li>
                ))}
              </ul>
            </details>
          )}
        </div>
      )}
    </section>
  );
}
