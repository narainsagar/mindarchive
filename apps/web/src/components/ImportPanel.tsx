import { useRef, useState } from "react";

import { ApiError, importExport, scanInbox } from "../api";
import type { ImportSummary } from "../api";
import type { Inbox } from "../useInbox";

interface Props {
  inbox: Inbox;
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
 * long the download link lasts, not how long the export takes. It sits behind a
 * disclosure because it matters enormously the first time and never again, and
 * this panel now opens above the archive rather than below it (D-030).
 */
export function ImportPanel({ inbox: inboxState, onImported }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [summary, setSummary] = useState<ImportSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [inboxMessage, setInboxMessage] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const inbox = inboxState.status;
  const refreshInbox = inboxState.refresh;

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
    <section className="import" aria-labelledby="import-heading">
      <h3 className="visually-hidden" id="import-heading">
        Import
      </h3>

      <div className="import__row">
        {inbox && inbox.waiting > 0 && (
          <span className="import__waiting">
            {inbox.waiting} {inbox.waiting === 1 ? "file" : "files"} waiting
          </span>
        )}

        {inbox && (
          <button
            type="button"
            className="button"
            onClick={checkInbox}
            disabled={busy}
          >
            {busy ? "Checking…" : "Check that folder now"}
          </button>
        )}

        <label className="button import__file">
          <span className="visually-hidden">Choose an export file</span>
          <span aria-hidden="true">{file ? file.name : "Choose a file…"}</span>
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

      {inbox && (
        <p className="import__inbox">
          Save an export into <code>{inbox.folder}</code> and it imports
          itself. Nothing leaves your machine.
        </p>
      )}

      <details className="import__how">
        <summary>How do I get my export?</summary>
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

          <p>
            <strong>Import the zip exactly as it arrives.</strong> Do not
            unpack it looking for <code>conversations.json</code> — recent
            exports split it into <code>conversations-000.json</code> and
            friends, and Mind Archive puts them back together for you.
          </p>

          <p className="import__warning">
            <strong>ChatGPT says this can take a few days.</strong> Two things
            catch people out: the download link{" "}
            <strong>expires 24 hours after the email arrives</strong>, and
            asking again <strong>cancels your previous request</strong>. Ask
            once, then wait.
          </p>
        </div>
      </details>

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
