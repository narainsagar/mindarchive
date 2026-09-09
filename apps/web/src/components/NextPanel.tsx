interface Props {
  /** Anchor target for the header nav. */
  id?: string;
}

/**
 * What is being worked on next.
 *
 * Its own section rather than a footnote inside Status, because it is one of
 * the things people most want to know about a young project and it needs to be
 * reachable from the header (D-031).
 */
export function NextPanel({ id }: Props) {
  return (
    <section className="panel" id={id} aria-labelledby="next-heading">
      <h2 className="panel__title" id="next-heading">
        Coming next
      </h2>

      <ul className="next__list">
        <li>Organise it with projects and tags</li>
        <li>Import from Gemini, Cursor and others</li>
        <li>Import several exports at once, in the background</li>
        <li>Optional backup to storage you choose</li>
      </ul>

      <p className="note">
        Nothing here is a promise of a date. If one of these matters to you,
        say so — it is the clearest signal about what to build next.
      </p>
    </section>
  );
}
