/**
 * A search snippet, with the matching words marked.
 *
 * The backend wraps matches in `<<` and `>>` rather than sending HTML. That is
 * deliberate: a snippet is a piece of someone's conversation, and conversation
 * text must never reach the page as markup. Here it is split on those markers
 * and rendered as React elements, so the text stays text whatever is in it.
 */
export function Snippet({ text }: { text: string }) {
  const parts = text.split(/<<(.*?)>>/gs);

  return (
    <span className="snippet">
      {parts.map((part, index) =>
        // Odd indices are the captured groups: the matched words.
        index % 2 === 1 ? (
          <mark key={index}>{part}</mark>
        ) : (
          <span key={index}>{part}</span>
        ),
      )}
    </span>
  );
}
