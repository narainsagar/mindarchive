import { useCallback, useEffect, useRef, useState } from "react";

import { ApiError, fetchConversations } from "../api";
import type { ConversationSummary } from "../api";
import { ConversationView } from "./ConversationView";
import { Snippet } from "./Snippet";

const PAGE_SIZE = 25;

/** "14 March 2024", or nothing at all if the date is missing. */
function formatDate(value: string | null): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

interface Props {
  /** Anchor target for the header nav. */
  id?: string;
  /**
   * Reports how many conversations are in the archive.
   *
   * Import and Export moved to the header (D-037), where they are reachable
   * from anywhere on the page — but Export needs to know the count so its
   * dialog can say what is about to be downloaded, and this panel is what
   * knows it.
   */
  onTotalChange?: (total: number) => void;
}

/**
 * Browse and search the archive.
 *
 * A search box and a list. Choosing a conversation opens it in place — still
 * one page, still no router, because there is still nothing to navigate
 * between (D-008).
 */
export function ArchivePanel({ id, onTotalChange }: Props) {
  const [query, setQuery] = useState("");
  const [tag, setTag] = useState("");
  const [tagCounts, setTagCounts] = useState<Record<string, number>>({});
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openPath, setOpenPath] = useState<string | null>(null);

  // Identifies the most recent request, so a slow earlier search cannot
  // overwrite the results of a later one.
  const latest = useRef(0);

  const load = useCallback(
    async (search: string, filterTag: string, page: number) => {
      const request = ++latest.current;
      setLoading(true);

      try {
        const result = await fetchConversations({
          query: search,
          tag: filterTag,
          limit: PAGE_SIZE,
          offset: page * PAGE_SIZE,
        });
        if (request !== latest.current) return;

        setConversations(result.conversations);
        setTotal(result.total);
        onTotalChange?.(result.total);
        // Defensive: a response without tags must narrow the view, not
        // blank it. Object.entries(undefined) throws.
        setTagCounts(result.tags ?? {});
        setError(null);
      } catch (caught) {
        if (request !== latest.current) return;
        setError(
          caught instanceof ApiError
            ? caught.message
            : "Could not read your archive.",
        );
      } finally {
        if (request === latest.current) setLoading(false);
      }
    },
    // App passes a plain setState function here, which React guarantees is
    // stable — so this dependency never actually changes identity. It is
    // listed because it is genuinely used, and a future caller passing an
    // inline arrow should re-create the callback rather than silently read a
    // stale one.
    [onTotalChange],
  );

  // Search as you type, but wait for a pause first.
  useEffect(() => {
    const timer = setTimeout(() => {
      setOffset(0);
      void load(query, tag, 0);
    }, 200);
    return () => clearTimeout(timer);
  }, [query, tag, load]);

  useEffect(() => {
    if (offset > 0) void load(query, tag, offset);
    // Paging only: query and tag changes are handled by the effect above.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [offset]);

  if (openPath) {
    return (
      <ConversationView
        path={openPath}
        onClose={() => setOpenPath(null)}
        onTagsChanged={() => void load(query, tag, offset)}
      />
    );
  }

  const allTags = Object.entries(tagCounts);

  const pages = Math.ceil(total / PAGE_SIZE);
  const searching = query.trim().length > 0;

  return (
    <section className="panel" id={id} aria-labelledby="archive-heading">
      <div className="archive__header">
        <h2 className="panel__title" id="archive-heading">
          Your archive
        </h2>
        {/* Import and Export used to sit here. They live in the header now
            (D-037), so they are reachable from anywhere on the page rather
            than only when the archive is in view. */}
        {total > 0 && (
          <p className="archive__count">
            {total} {total === 1 ? "conversation" : "conversations"}
          </p>
        )}
      </div>

      <label className="archive__search">
        <span className="visually-hidden">Search your conversations</span>
        <input
          type="search"
          value={query}
          placeholder="Search your conversations…"
          onChange={(event) => setQuery(event.target.value)}
        />
      </label>

      {allTags.length > 0 && (
        <div className="tagbar" role="group" aria-label="Filter by tag">
          <button
            type="button"
            className={`tagbar__tag${tag === "" ? " tagbar__tag--on" : ""}`}
            onClick={() => setTag("")}
          >
            All
          </button>
          {allTags.map(([name, count]) => (
            <button
              key={name}
              type="button"
              className={`tagbar__tag${tag === name ? " tagbar__tag--on" : ""}`}
              aria-pressed={tag === name}
              onClick={() => setTag(tag === name ? "" : name)}
            >
              {name} <span className="tagbar__count">{count}</span>
            </button>
          ))}
        </div>
      )}

      {error && (
        <p className="message message--error" role="alert">
          {error}
        </p>
      )}

      {!error && !loading && conversations.length === 0 && (
        <p className="archive__empty">
          {tag && !searching
            ? `Nothing is tagged ${tag}.`
            : searching
              ? "Nothing matched that search."
              : "Nothing here yet. Import a ChatGPT export to get started."}
        </p>
      )}

      {conversations.length > 0 && (
        <ul className="archive__list">
          {conversations.map((conversation) => {
            const date = formatDate(conversation.created_at);
            return (
              <li key={conversation.path}>
                <button
                  type="button"
                  className="archive__item"
                  onClick={() => setOpenPath(conversation.path)}
                >
                  <span className="archive__title">{conversation.title}</span>

                  <span className="archive__meta">
                    {date && <span>{date}</span>}
                    <span>
                      {conversation.message_count}{" "}
                      {conversation.message_count === 1
                        ? "message"
                        : "messages"}
                    </span>
                    <span className="archive__source">
                      {conversation.source}
                    </span>
                  </span>

                  {(conversation.tags ?? []).length > 0 && (
                    <span className="archive__tags">
                      {conversation.tags.map((name: string) => (
                        <span key={name} className="archive__tag">
                          {name}
                        </span>
                      ))}
                    </span>
                  )}

                  {conversation.snippet && (
                    <Snippet text={conversation.snippet} />
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      )}

      {pages > 1 && (
        <div className="archive__paging">
          <button
            type="button"
            className="button"
            disabled={offset === 0}
            onClick={() => setOffset((page) => Math.max(0, page - 1))}
          >
            Previous
          </button>
          <span className="archive__page">
            Page {offset + 1} of {pages}
          </span>
          <button
            type="button"
            className="button"
            disabled={offset >= pages - 1}
            onClick={() => setOffset((page) => page + 1)}
          >
            Next
          </button>
        </div>
      )}
    </section>
  );
}
