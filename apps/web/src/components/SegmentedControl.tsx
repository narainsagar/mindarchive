/**
 * A row of mutually exclusive choices.
 *
 * Built on real radio inputs rather than buttons with aria-pressed, so the
 * keyboard, screen readers and form semantics all work without us
 * reimplementing them. The inputs are hidden visually, never from assistive
 * technology.
 */

interface Props<T extends string> {
  /** Shown above the row, and read out as the group's name. */
  legend: string;
  /** Unique across the page — it groups the radios. */
  name: string;
  value: T;
  options: readonly T[];
  labels: Record<T, string>;
  onChange: (value: T) => void;
}

export function SegmentedControl<T extends string>({
  legend,
  name,
  value,
  options,
  labels,
  onChange,
}: Props<T>) {
  return (
    <fieldset className="segmented">
      <legend className="segmented__legend">{legend}</legend>
      <div className="segmented__options">
        {options.map((option) => (
          <label className="segmented__option" key={option}>
            <input
              type="radio"
              name={name}
              value={option}
              checked={value === option}
              onChange={() => onChange(option)}
            />
            <span>{labels[option]}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
