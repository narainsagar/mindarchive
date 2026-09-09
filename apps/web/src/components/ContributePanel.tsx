import { SUPPORT } from "../support";

interface Props {
  /** Anchor target for the header nav. */
  id?: string;
}

/**
 * Ways to help that are not money.
 *
 * Deliberately concrete. "Contributions welcome" tells nobody what to do; an
 * export format that does not import yet is something a person can act on this
 * afternoon.
 */
export function ContributePanel({ id }: Props) {
  return (
    <section className="panel" id={id} aria-labelledby="contribute-heading">
      <h2 className="panel__title" id="contribute-heading">
        Contribute
      </h2>

      <p className="support__lede">
        The most valuable contributions are not code.
      </p>

      <ul className="contribute__list">
        <li>
          <strong>Tell us about an export that will not import.</strong> Every
          provider changes its format eventually, and a real broken export is
          worth more than any amount of guessing. Say which service and what
          happened — never send the file itself, it is your conversations.
        </li>
        <li>
          <strong>Add an importer.</strong> Each provider sits behind its own
          adapter and the core knows nothing about any of them, so a new one is
          a self-contained piece of work.
        </li>
        <li>
          <strong>Say what is confusing.</strong> Wording that made you hesitate
          is a bug worth reporting.
        </li>
      </ul>

      <p className="note">
        Mind Archive is source-available under PolyForm Noncommercial 1.0.0 —
        readable and inspectable, but not open source. Read the code before you
        trust it with your archive.
      </p>

      {SUPPORT.repositoryUrl && (
        <p>
          <a
            className="button"
            href={SUPPORT.repositoryUrl}
            target="_blank"
            rel="noreferrer noopener"
          >
            Read the source
          </a>
        </p>
      )}
    </section>
  );
}
