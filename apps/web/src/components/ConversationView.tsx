import { useEffect, useState } from "react";
import Markdown from "react-markdown";

import { ApiError, fetchConversation } from "../api";
import type { ConversationDetail } from "../api";

interface Props {
  path: string;
  onClose: () => void;
}

/**
 * Drop the file's opening `# Title` heading.
 *
 * The Markdown on disk repeats the title as an H1, which is right for a file
 * someone opens in an editor and wrong here, where the title is already shown
 * above. Only a heading on the very first line is removed, and only when it
 * matches the title — a conversation that happens to begin with a different
 * heading keeps it.
 */
function withoutLeadingTitle(body: string, title: string): string {
  const newline = body.indexOf("\n");
  const firstLine = newline === -1 ? body : body.slice(0, newline);

  if (firstLine.trim() !== `# ${title}`.trim()) {
    return body;
  }

  return newline === -1 ? "" : body.slice(newline + 1).replace(/^\n+/, "");
}

/**
 * Read one conversation.
 *
 * The body is Markdown from the file on disk, rendered by `react-markdown`,
 * which builds React elements rather than setting HTML. That matters: this is
 * text that came from a provider export, and it must never be able to put
 * markup or script into the page. Raw HTML in the Markdown is not enabled, so
 * a conversation containing `<script>` renders as those characters.
 */
export function ConversationView({ path, onClose }: Props) {
  const [conversation, setConversation] = useState<ConversationDetail | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setConversation(null);
    setError(null);

    async function load() {
      try {
        const result = await fetchConversation(path);
        if (!cancelled) setConversation(result);
      } catch (caught) {
        if (cancelled) return;
        setError(
          caught instanceof ApiError
            ? caught.message
            : "Could not open that conversation.",
        );
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [path]);

  // Escape closes it, which is what people expect from something opened
  // in place.
  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  return (
    <section className="panel" aria-labelledby="conversation-heading">
      <div className="conversation__header">
        <button type="button" className="button" onClick={onClose}>
          ← Back to your archive
        </button>
      </div>

      {error && (
        <p className="message message--error" role="alert">
          {error}
        </p>
      )}

      {!error && !conversation && <p className="note">Opening…</p>}

      {conversation && (
        <article className="conversation">
          <h2 className="conversation__title" id="conversation-heading">
            {conversation.title}
          </h2>

          <p className="conversation__meta">
            {conversation.message_count}{" "}
            {conversation.message_count === 1 ? "message" : "messages"} · from{" "}
            {conversation.source}
          </p>

          <div className="conversation__body">
            <Markdown>
              {withoutLeadingTitle(conversation.body, conversation.title)}
            </Markdown>
          </div>
        </article>
      )}
    </section>
  );
}
