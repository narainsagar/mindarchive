import { useEffect, useRef, useState } from "react";

import { ApiError, setTags } from "../api";

interface Props {
  path: string;
  tags: string[];
  onChanged?: (tags: string[]) => void;
}

/**
 * Add and remove a conversation's tags.
 *
 * Tags are saved into that conversation's `metadata.json` on disk, not into the
 * search index — they are the one thing in the archive you made rather than
 * imported, so they belong with everything else you own (D-025).
 *
 * Deliberately plain: a list of labels and a text box. No autocomplete
 * dropdown, no drag-and-drop, no colour picker. Tagging something should take
 * about as long as writing the word.
 */
export function TagEditor({ path, tags, onChanged }: Props) {
  const [current, setCurrent] = useState<string[]>(tags);
  const [draft, setDraft] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setCurrent(tags);
  }, [tags]);

  async function save(next: string[]) {
    // Show the change immediately, then put it back if the save fails. Tagging
    // should feel instant; it is one word.
    const previous = current;
    setCurrent(next);
    setSaving(true);
    setError(null);

    try {
      const saved = await setTags(path, next);
      setCurrent(saved.tags);
      onChanged?.(saved.tags);
    } catch (caught) {
      setCurrent(previous);
      setError(
        caught instanceof ApiError ? caught.message : "Those tags were not saved.",
      );
    } finally {
      setSaving(false);
    }
  }

  function add() {
    const label = draft.trim();
    if (!label) return;

    // Already there, in any capitalisation? Do nothing rather than complain.
    if (current.some((tag) => tag.toLowerCase() === label.toLowerCase())) {
      setDraft("");
      return;
    }

    setDraft("");
    void save([...current, label]);
    inputRef.current?.focus();
  }

  return (
    <div className="tags">
      <ul className="tags__list">
        {current.map((tag) => (
          <li key={tag} className="tags__tag">
            <span>{tag}</span>
            <button
              type="button"
              className="tags__remove"
              disabled={saving}
              aria-label={`Remove tag ${tag}`}
              onClick={() => void save(current.filter((one) => one !== tag))}
            >
              ×
            </button>
          </li>
        ))}
      </ul>

      <form
        className="tags__add"
        onSubmit={(event) => {
          event.preventDefault();
          add();
        }}
      >
        <label>
          <span className="visually-hidden">Add a tag</span>
          <input
            ref={inputRef}
            type="text"
            value={draft}
            placeholder="Add a tag…"
            maxLength={50}
            disabled={saving}
            onChange={(event) => setDraft(event.target.value)}
          />
        </label>
        <button type="submit" className="button" disabled={!draft.trim() || saving}>
          Add
        </button>
      </form>

      {error && (
        <p className="message message--error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
