interface Props {
  waiting: number;
  onClick: () => void;
}

/**
 * Opens the import dialog, and says when the inbox folder has something in it.
 *
 * The count is the reason this is a button and not a plain link: it is the one
 * piece of import state worth seeing without opening anything.
 */
export function ImportButton({ waiting, onClick }: Props) {
  return (
    <button type="button" className="button" onClick={onClick}>
      Import
      {waiting > 0 && (
        <span className="button__count">
          <span className="visually-hidden">
            {waiting} {waiting === 1 ? "file" : "files"} waiting
          </span>
          <span aria-hidden="true">{waiting}</span>
        </span>
      )}
    </button>
  );
}
