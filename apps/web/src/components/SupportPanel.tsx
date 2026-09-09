import { SUPPORT, configuredDonations, mailto } from "../support";

interface Props {
  /** Anchor target for the header nav. */
  id?: string;
}

/**
 * Donations, and how to get a commercial licence.
 *
 * Mind Archive is free for noncommercial use and always will be (D-016), so
 * this asks rather than nags: no modal, no banner, no counting down to
 * anything. Links that have not been configured in `support.ts` are simply
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
        Mind Archive is free for personal use, and for schools, charities and
        public research bodies. It stays that way. If it has been useful and you
        want to put something behind it, here is how.
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
          Company use needs a commercial licence. It is a short email, not a
          sales process — say what you are doing and a licence comes back.
        </p>
        <p>
          <a href={mailto("Commercial licence")}>{SUPPORT.contactEmail}</a>
        </p>
      </div>
    </section>
  );
}
