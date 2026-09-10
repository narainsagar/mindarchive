/**
 * Where support, donations and licensing enquiries go.
 *
 * ─────────────────────────────────────────────────────────────────────────
 *  FILL THESE IN. Every value is blank on purpose — nothing here has been
 *  guessed. A blank entry is simply not rendered, so the interface never
 *  shows a dead link or a placeholder handle to anyone.
 * ─────────────────────────────────────────────────────────────────────────
 *
 * These are public by design: a donation handle and a contact address are
 * meant to be seen. Nothing secret belongs in this file — it ships to the
 * browser. Secrets go in `.env`, which is git-ignored.
 *
 * `contactEmail` is the only one already filled in, taken from the `author`
 * block in `project.json`, which is committed. Change it in both places if
 * you would rather licensing mail went somewhere else.
 */

export interface SupportLink {
  /** Shown on the button. */
  label: string;
  /** Leave blank until you have the real address. */
  url: string;
  /** One line under the button, saying what it is. */
  note?: string;
}

interface SupportConfig {
  contactEmail: string;
  donate: SupportLink[];
  wallets: SupportLink[];
  repositoryUrl: string;
}

export const SUPPORT: SupportConfig = {
  /** Reaches you for commercial licensing and anything else. */
  contactEmail: "kishor3947@gmail.com",

  /**
   * One-off and recurring donations. Add a URL to make one appear.
   *
   * Examples of what goes here:
   *   PayPal      https://paypal.me/yourhandle
   *   Ko-fi       https://ko-fi.com/yourhandle
   *   GitHub      https://github.com/sponsors/yourhandle
   */
  donate: [
    { label: "Buy me a coffee", url: "", note: "A one-off thank you" },
    { label: "Sponsor monthly", url: "", note: "Ongoing support" },
  ],

  /**
   * Public wallet addresses, if you want them. `url` stays blank; put the
   * address in `label` — it is shown as text to copy, not as a link.
   */
  wallets: [],

  /** Where the code lives. Makes the "Read the source" button appear. */
  repositoryUrl: "https://github.com/RootedGlobal/mindarchive",
};

/** Only the donation links that have actually been configured. */
export function configuredDonations(): SupportLink[] {
  return SUPPORT.donate.filter((link) => link.url.trim().length > 0);
}

/**
 * A mailto link with the subject encoded.
 *
 * Spaces and punctuation in a mailto query have to be percent-encoded or mail
 * clients truncate the subject at the first space.
 */
export function mailto(subject: string): string {
  return `mailto:${SUPPORT.contactEmail}?subject=${encodeURIComponent(subject)}`;
}
