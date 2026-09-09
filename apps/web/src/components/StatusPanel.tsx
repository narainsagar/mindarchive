import type { Health, PublicConfig } from "../api";

interface Props {
  health: Health | null;
  config: PublicConfig | null;
  /** Anchor target for the header nav. */
  id?: string;
}

/**
 * Where your archive is, and whether anything is leaving this computer.
 *
 * This panel exists to answer the question the product is built around, in
 * plain language, without the user having to trust a claim on a website.
 */
export function StatusPanel({ health, config, id }: Props) {
  return (
    <section className="panel" id={id} aria-labelledby="status-heading">
      <h2 className="panel__title" id="status-heading">
        Status
      </h2>

      <dl className="facts">
        <dt>Backend</dt>
        <dd>
          {health ? (
            <span className="badge badge--ok">Running</span>
          ) : (
            <span className="badge badge--warn">Not connected</span>
          )}
        </dd>

        {config && (
          <>
            <dt>Stored</dt>
            <dd>
              {config.storage_mode === "local"
                ? "On this computer"
                : config.storage_mode}
            </dd>

            <dt>Cloud backup</dt>
            <dd>
              {config.cloud_enabled ? (
                <span className="badge badge--warn">On</span>
              ) : (
                <span className="badge badge--ok">Off</span>
              )}
            </dd>

            <dt>Archive folder</dt>
            <dd className="path">{config.archive_location}</dd>

            <dt>Version</dt>
            <dd>{config.version}</dd>
          </>
        )}
      </dl>

      {config && <p className="note">{config.privacy_note}</p>}
    </section>
  );
}
