import { exportUrl } from "../api";

interface Props {
  /** How many conversations are in the archive, for the summary line. */
  total: number;
  onDownloaded?: () => void;
}

/**
 * What "export everything" actually gives you.
 *
 * The download itself is a plain link — the browser fetches the zip and the
 * backend streams it, with no JavaScript in the middle. The dialog exists to
 * say what is in the file before you commit to a download that may be large,
 * and to make the point that this is a copy of your own folder rather than
 * anything being sent anywhere.
 */
export function ExportPanel({ total, onDownloaded }: Props) {
  return (
    <section className="export" aria-labelledby="export-heading">
      <h3 className="visually-hidden" id="export-heading">
        Export
      </h3>

      <p className="export__lede">
        A zip of your whole archive — {total}{" "}
        {total === 1 ? "conversation" : "conversations"} as ordinary files that
        need nothing to read them.
      </p>

      <ul className="export__contents">
        <li>
          One folder per conversation, each with a{" "}
          <code>conversation.md</code> you can open in any editor
        </li>
        <li>
          The <code>metadata.json</code> beside it, including your tags
        </li>
        <li>A README for whoever opens it without Mind Archive</li>
      </ul>

      <p className="note">
        The search index is deliberately left out. It is derived from these
        files and rebuilds itself, so it would only make the download larger.
      </p>

      <div className="export__actions">
        {/* A plain link: the browser downloads it, and the file is just the
            archive folder zipped up. No upload, no server round trip beyond
            your own machine. */}
        <a
          className="button button--primary"
          href={exportUrl()}
          download
          onClick={() => onDownloaded?.()}
        >
          Download the zip
        </a>
      </div>

      <p className="note">
        A large archive takes a moment to compress. Nothing leaves this
        computer — the file is written by the backend running on it.
      </p>
    </section>
  );
}
