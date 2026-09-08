import { useCallback, useEffect, useRef, useState } from "react";

import { ApiError, fetchInbox, importExport, scanInbox } from "../api";
import type { ImportSummary, InboxStatus } from "../api";

interface Props {
  onImported?: () => void;
}

/**
 * Import a provider export.
 *
 * Two routes, because getting an export out of ChatGPT is slow and the
 * interface should be honest about that rather than cheerful:
 *
 *  - drop the file in the inbox folder and it imports itself
 *  - or choose it here
 *
 * The guidance about timings is deliberately specific. "Up to 24 hours" — which
 * this panel used to say — is wrong and actively misleading: 24 hours is how
 * long the download link lasts, not how long the export takes.
 */
export function ImportPanel({ onImported }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [summary, setSummary] = useState<ImportSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [inbox, setInbox] = useState<InboxStatus | null>(null);
  const [inboxMessage, setInboxMessage] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const refreshInbox = useCallback(async () => {
    try {
      setInbox(await fetchInbox());
    } catch {
      // The inbox is a convenience. If it cannot be read, the panel still
      // works — say nothing rather than showing an error about a folder.
      setInbox(null);
    }
  }, []);

  useEffect(() => {
    void refreshInbox();
  }, [refreshInbox]);

  // Coming back to the tab is the moment a download is likely to have
  // finished, so it is the natural time to look in the inbox again.
  useEffect(() => {
    function onFocus() {
      void refreshInbox();
    }
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, [refreshInbox]);

  function choose(chosen: File | null) {
    setFile(chosen);
    setSummary(null);
    setError(null);
    setInboxMessage(null);
  }

  async function submit() {
    if (!file || busy) return;

    setBusy(true);
    setSummary(null);
    setError(null);
    setInboxMessage(null);

    try {
      const result = await importExport(file);
      setSummary(result);
      if (result.ok) {
        setFile(null);
        if (inputRef.current) inputRef.current.value = "";
        onImported?.();
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

  async function checkInbox() {
    if (busy) return;

    setBusy(true);
    setSummary(null);
    setError(null);
    setInboxMessage(null);

    try {
      const result = await scanInbox();
      setInboxMessage(result.message);
      if (result.new || result.updated) onImported?.();
      await refreshInbox();
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Could not check your inbox folder.",
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

      <div className="import__steps">
        <p>
          In ChatGPT, go to{" "}
          <a
            href="https://chatgpt.com/#settings/DataControls"
            target="_blank"
            rel="noreferrer noopener"
          >
            Settings → Data controls → Export data
          </a>
          . ChatGPT emails you when it is ready.
        </p>

        <p className="import__warning">
          <strong>ChatGPT says this can take a few days.</strong> Two things
          catch people out: the download link{" "}
          <strong>expires 24 hours after the email arrives</strong>, and asking
          again <strong>cancels your previous request</strong>. Ask once, then
          wait.
        </p>
      </div>

      {inbox && (
        <div className="import__inbox">
          <p>
            Save the file into{" "}
            <code>{inbox.folder}</code> and it imports itself.
            {inbox.waiting > 0 && (
              <>
                {" "}
                <strong>
                  {inbox.waiting} {inbox.waiting === 1 ? "file is" : "files are"}{" "}
                  waiting.
                </strong>
              </>
            )}
          </p>
          <button
            type="button"
            className="button"
            onClick={checkInbox}
            disabled={busy}
          >
            {busy ? "Checking…" : "Check that folder now"}
          </button>
        </div>
      )}

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
          Reading your export. A large one can take a few minutes — nothing is
          being uploaded anywhere, it is all happening on this computer.
        </p>
      )}

      {error && (
        <p className="message message--error" role="alert">
          {error}
        </p>
      )}

      {inboxMessage && !error && (
        <p className="message message--ok" role="status">
          {inboxMessage}
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
