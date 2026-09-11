import { useEffect, useState } from "react";

/** How far down the page it becomes worth offering. One screen. */
function pastOneScreen() {
  return window.scrollY > window.innerHeight;
}

/**
 * A way back to the top from wherever you are, not only from the footer.
 *
 * It is a plain anchor to `#top`, the same target the footer link and the
 * header's Home entry use. That means it works with JavaScript off and before
 * React has hydrated, and the browser does the scrolling — `html` already has
 * `scroll-behavior: smooth`, which a reduced-motion preference turns off.
 *
 * The only thing this component decides is whether the link is worth showing.
 * It stays out of the way until you have scrolled a screen, because a control
 * offering to take you to the top while you are already at the top is clutter.
 *
 * Hidden state is `visibility: hidden` in CSS rather than an unmounted element,
 * which keeps it out of the tab order and away from screen readers while it is
 * not offered.
 */
export function BackToTop() {
  const [shown, setShown] = useState(false);

  useEffect(() => {
    function onScroll() {
      setShown(pastOneScreen());
    }

    // Run once on mount: the page can be reloaded at a scroll position, or
    // opened straight at an anchor, and neither fires a scroll event.
    onScroll();

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  // The footer has a link of the same name and the same destination. Two links
  // agreeing with each other is not an accessibility problem; renaming this one
  // to avoid the duplicate would be, since "Back to top" is what it does.
  return (
    <a className={`backtotop${shown ? " backtotop--shown" : ""}`} href="#top">
      Back to top
    </a>
  );
}
