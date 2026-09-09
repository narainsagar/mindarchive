import { SUPPORT, mailto } from "../support";

/**
 * The bottom of the page.
 *
 * The copyright year and holder come from `project.json`; keep them in step if
 * that file changes. The Back to top link is a plain anchor so it works before
 * React has hydrated and with JavaScript off.
 */
const COPYRIGHT_YEAR = "2026";
const COPYRIGHT_HOLDER = "Mind Archive";

export function SiteFooter() {
  return (
    <footer className="footer">
      <div className="workspace footer__inner">
        <div className="footer__block">
          <p className="footer__slogan">Local first. Privacy first. Yours.</p>
          <p className="footer__legal">
            © {COPYRIGHT_YEAR} {COPYRIGHT_HOLDER}. Source-available under
            PolyForm Noncommercial 1.0.0. Free for personal and noncommercial
            use; company use needs a commercial licence.
          </p>
        </div>

        <nav className="footer__links" aria-label="Footer">
          <a href="#support">Support</a>
          <a href="#contribute">Contribute</a>
          <a href={mailto("Mind Archive")}>Contact</a>
          {SUPPORT.repositoryUrl && (
            <a
              href={SUPPORT.repositoryUrl}
              target="_blank"
              rel="noreferrer noopener"
            >
              Source
            </a>
          )}
          <a className="footer__top" href="#top">
            Back to top
          </a>
        </nav>
      </div>
    </footer>
  );
}
