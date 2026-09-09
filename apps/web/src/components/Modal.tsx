import { useCallback, useEffect, useId, useRef } from "react";
import type { ReactNode } from "react";

interface Props {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
}

/**
 * A dialog that closes on Escape, on a click outside it, and on its close
 * button.
 *
 * Hand-written rather than the native <dialog> element: `showModal()` is not
 * implemented everywhere the tests run, and a small amount of explicit focus
 * handling is easier to reason about than working around that. No dependency
 * either way — see AGENTS.md on not adding one you cannot justify.
 *
 * Focus moves into the dialog when it opens and returns to whatever opened it
 * when it closes, because losing your place is the thing that makes a dialog
 * feel broken.
 */
export function Modal({ open, title, onClose, children }: Props) {
  const panelRef = useRef<HTMLDivElement>(null);
  const returnFocusTo = useRef<Element | null>(null);
  const titleId = useId();

  // Escape, from anywhere.
  useEffect(() => {
    if (!open) return;

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.stopPropagation();
        onClose();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  // Remember what opened this, move focus in, and give it back on the way out.
  useEffect(() => {
    if (!open) return;

    returnFocusTo.current = document.activeElement;
    panelRef.current?.focus();

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = previousOverflow;

      const target = returnFocusTo.current;
      if (target instanceof HTMLElement && document.contains(target)) {
        target.focus();
      }
    };
  }, [open]);

  const onBackdropClick = useCallback(
    (event: React.MouseEvent<HTMLDivElement>) => {
      // Only a click on the backdrop itself — not one that started inside the
      // panel and happened to end on it.
      if (event.target === event.currentTarget) {
        onClose();
      }
    },
    [onClose],
  );

  if (!open) return null;

  return (
    <div className="modal__backdrop" onMouseDown={onBackdropClick}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        ref={panelRef}
      >
        <div className="modal__header">
          <h2 className="modal__title" id={titleId}>
            {title}
          </h2>
          <button
            type="button"
            className="modal__close"
            onClick={onClose}
            aria-label="Close"
          >
            <span aria-hidden="true">×</span>
          </button>
        </div>

        <div className="modal__body">{children}</div>
      </div>
    </div>
  );
}
