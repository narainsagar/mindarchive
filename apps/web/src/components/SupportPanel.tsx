import { SUPPORT, configuredDonations, mailto } from "../support";

interface Props {
  /** Anchor target for the header nav. */
  id?: string;
}

/**
 * Donations, and where a licensing question goes.
 *
 * Mind Archive is proprietary, all rights reserved, and nothing is on sale
 * (D-046) — so this panel sells nothing: no modal, no banner, no counting down
 * to anything. Links that have not been configured in `support.ts` are simply
 * absent — better nothing than a dead link.
 */
export function SupportPanel({ id }: Props) {
  const donations = configuredDonations();
  const wallets = SUPPORT.wallets;

  return (
    <section className="panel" id={id} aria-labelledby="support-heading">
      <h2 className="panel__title" id="support-heading">
        Support this work
      </h2>

      <p className="support__lede">
        Mind Archive never nags, never counts down, and never asks twice. If it
        has been useful and you want to put something behind it, here is how.
      </p>

      {donations.length > 0 && (
        <div className="support__links">
          {donations.map((link) => (
            <a
              key={link.label}
              className="button button--primary"
              href={link.url}
              target="_blank"
              rel="noreferrer noopener"
            >
              {link.label}
            </a>
          ))}
        </div>
      )}

      {wallets.length > 0 && (
        <dl className="support__wallets">
          {wallets.map((wallet) => (
            <div className="support__wallet" key={wallet.label}>
              <dt>{wallet.note ?? "Wallet"}</dt>
              <dd className="path">{wallet.label}</dd>
            </div>
          ))}
        </dl>
      )}

      {donations.length === 0 && wallets.length === 0 && (
        <p className="note">
          Donation links are not set up yet. Until they are, the most useful
          thing you can send is a bug report.
        </p>
      )}

      <div className="support__commercial">
        <h3>Using it at work?</h3>
        <p>
          Mind Archive is proprietary and nothing is for sale yet, so there is
          no price to quote and nowhere to send you. If you want to use it in a
          company, write and ask.
        </p>
        <p>
          <a href={mailto("Licensing enquiry")}>{SUPPORT.contactEmail}</a>
        </p>
      </div>
    </section>
  );
}
