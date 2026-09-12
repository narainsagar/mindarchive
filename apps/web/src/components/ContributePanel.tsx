import { mailto } from "../support";

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
        Mind Archive is proprietary software, all rights reserved — not open
        source and not source-available. Outside code cannot be accepted yet;
        the reports above are what helps most.
      </p>

      {/* Email, not a repository link. The repository is private (D-046), so a
          "Read the source" button answered 404 and contradicted the sentence
          above it. Writing in is the route that actually works today, and it is
          the one the panel has always really been asking for. */}
      <p>
        <a className="button" href={mailto("Mind Archive")}>
          Get in touch
        </a>
      </p>
    </section>
  );
}
