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
 * `contactEmail` is the only one already filled in. The site keeps its own copy
 * in `docs/_data/support.yml`, because Jekyll cannot read a TypeScript file —
 * change both, or the page and the application disagree about where mail goes.
 *
 * It is deliberately *not* the `author` address in `project.json`. That one is
 * the git commit identity; this one is published to anyone who visits.
 */

/**
 * Where the project website lives.
 *
 * Configurable for the same reason `VITE_API_BASE_URL` is: the address differs
 * between a developer's machine and the published site. It defaults to the
 * local Jekyll server, so `dev.py up` plus the Jekyll one-liner gives a
 * working Support link with no configuration — the previous hardcoded
 * production URL made the app impossible to check locally.
 *
 * Set VITE_SITE_URL for a production build.
 */
const SITE_URL =
  import.meta.env.VITE_SITE_URL ?? "http://localhost:4000";

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
  contactEmail: "info@rootedglobal.co",

  /**
   * One link, and it goes to the website — never to a payment provider.
   *
   * LICENSING.md promises that Mind Archive "will never contain payment code,
   * phone home, or ask you for money while you are using it". Linking out to a
   * page keeps that literally true: no provider script, no checkout, no
   * third-party request ever originates from the application (D-038).
   *
   * It also means changing payment provider never touches the application —
   * the amounts and the checkout URLs live in docs/_data/support.yml.
   */
  donate: [
    {
      label: "Ways to support this",
      url: `${SITE_URL}/support/`,
      note: "Opens the website",
    },
  ],

  /**
   * Deliberately empty, and staying that way.
   *
   * A wallet address in the application would be payment detail inside the
   * product. It belongs on the website with everything else about money.
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
