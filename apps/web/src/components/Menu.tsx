import { useCallback, useEffect, useId, useRef, useState } from "react";
import type { ReactNode } from "react";

import { CaretIcon, TickIcon } from "./icons";

export interface MenuOption<T extends string> {
  value: T;
  label: string;
  /** Rendered before the label — a swatch, or an icon. */
  lead?: ReactNode;
}

interface Props<T extends string> {
  /** Names the group: "Palette", "Theme". Read out, and shown as the tooltip. */
  label: string;
  value: T;
  options: readonly MenuOption<T>[];
  onChange: (value: T) => void;
  /** Shown on the trigger. For Theme this reflects the current choice. */
  icon: ReactNode;
}

/**
 * A button that opens a short list of mutually exclusive choices.
 *
 * `role="menu"` with `menuitemradio` children rather than a listbox: this is a
 * menu button choosing one of a few options, which is exactly what that role
 * pair describes, and it lets each option stay a real `<button>` so click and
 * keyboard activation come for free.
 *
 * Hand-written rather than a native `<select>` because the palette options
 * carry colour swatches, and seeing the colours is the whole job of a palette
 * picker. That choice costs us the keyboard and focus handling below — it is
 * the same shape as `Modal.tsx`, which already does Escape, outside-click and
 * focus-restore.
 */
export function Menu<T extends string>({
  label,
  value,
  options,
  onChange,
  icon,
}: Props<T>) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const menuId = useId();

  const current = options.find((option) => option.value === value);

  const close = useCallback(
    (returnFocus: boolean) => {
      setOpen(false);
      if (returnFocus) triggerRef.current?.focus();
    },
    [],
  );

  // Escape from anywhere, and a click outside.
  useEffect(() => {
    if (!open) return;

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.stopPropagation();
        close(true);
      }
    }
    function onPointerDown(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) close(false);
    }

    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("mousedown", onPointerDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("mousedown", onPointerDown);
    };
  }, [open, close]);

  // Opening moves focus to the current choice, so arrow keys start somewhere
  // sensible rather than at the top of the list.
  useEffect(() => {
    if (!open) return;
    const panel = panelRef.current;
    if (!panel) return;
    const selected = panel.querySelector<HTMLElement>('[aria-checked="true"]');
    (selected ?? panel.querySelector<HTMLElement>("[role]"))?.focus();
  }, [open]);

  function move(from: HTMLElement, delta: number | "first" | "last") {
    const items = Array.from(
      panelRef.current?.querySelectorAll<HTMLElement>(
        '[role="menuitemradio"]',
      ) ?? [],
    );
    if (items.length === 0) return;

    let next: number;
    if (delta === "first") next = 0;
    else if (delta === "last") next = items.length - 1;
    else {
      const index = items.indexOf(from);
      next = Math.min(Math.max(index + delta, 0), items.length - 1);
    }
    items[next]?.focus();
  }

  return (
    <div className="menu" ref={rootRef}>
      <button
        type="button"
        ref={triggerRef}
        className="button menu__trigger"
        aria-haspopup="true"
        aria-expanded={open}
        aria-controls={open ? menuId : undefined}
        aria-label={`${label}: ${current?.label ?? ""}`}
        title={label}
        onClick={() => (open ? close(true) : setOpen(true))}
        onKeyDown={(event) => {
          if (event.key === "ArrowDown" || event.key === "ArrowUp") {
            event.preventDefault();
            setOpen(true);
          }
        }}
      >
        {icon}
        <span className="menu__value">{current?.label}</span>
        <CaretIcon />
      </button>

      {open && (
        <div
          id={menuId}
          className="menu__panel"
          role="menu"
          aria-label={label}
          ref={panelRef}
          onKeyDown={(event) => {
            const target = event.target as HTMLElement;
            if (event.key === "ArrowDown") {
              event.preventDefault();
              move(target, 1);
            } else if (event.key === "ArrowUp") {
              event.preventDefault();
              move(target, -1);
            } else if (event.key === "Home") {
              event.preventDefault();
              move(target, "first");
            } else if (event.key === "End") {
              event.preventDefault();
              move(target, "last");
            } else if (event.key === "Tab") {
              close(false);
            }
          }}
        >
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              role="menuitemradio"
              aria-checked={option.value === value}
              className="menu__option"
              onClick={() => {
                onChange(option.value);
                close(true);
              }}
            >
              {option.lead}
              <span className="menu__label">{option.label}</span>
              <TickIcon />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
