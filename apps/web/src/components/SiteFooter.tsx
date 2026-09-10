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
        {/* One flowing line rather than two stacked blocks. The slogan and the
            licence are the same sentence's worth of information, and stacking
            them left a hole in a full-width footer. */}
        <p className="footer__legal">
          <strong className="footer__slogan">
            Local first. Privacy first. Yours.
          </strong>{" "}
          © {COPYRIGHT_YEAR} {COPYRIGHT_HOLDER}. Source-available under PolyForm
          Noncommercial 1.0.0. Free for personal and noncommercial use; company
          use needs a commercial licence.
        </p>

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
