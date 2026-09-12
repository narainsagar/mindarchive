import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import type { Health, PublicConfig } from "./api";
import { ApiError } from "./api";
import { SUPPORT } from "./support";

vi.mock("./api", async () => {
  const actual = await vi.importActual<typeof import("./api")>("./api");
  return {
    ...actual,
    fetchHealth: vi.fn(),
    fetchConfig: vi.fn(),
    fetchConversations: vi.fn(),
  };
});

const { fetchConfig, fetchHealth, fetchConversations } = await import("./api");

/** An archive with something in it, so the export control is reachable. */
function archiveWithConversations() {
  vi.mocked(fetchConversations).mockResolvedValue({
    conversations: [
      {
        path: "2026/chatgpt/2026-03-11-postgres-index-strategy",
        title: "Postgres index strategy",
        source: "chatgpt",
        created_at: "2026-03-11T10:00:00Z",
        updated_at: "2026-03-11T11:30:00Z",
        message_count: 12,
        snippet: null,
        tags: [],
      },
    ],
    total: 1,
    offset: 0,
    limit: 25,
    sources: { chatgpt: 1 },
    tags: {},
  });
}

const health: Health = {
  status: "ok",
  version: "0.1.0",
  message: "Mind Archive is running.",
};

const config: PublicConfig = {
  version: "0.1.0",
  storage_mode: "local",
  cloud_enabled: false,
  archive_location: "/home/someone/mindarchive/data/archive",
  database_location: "/home/someone/mindarchive/data/mind_archive.db",
  privacy_note:
    "Your archive is stored only on this computer. Nothing is uploaded anywhere.",
};

function backendAvailable() {
  vi.mocked(fetchHealth).mockResolvedValue(health);
  vi.mocked(fetchConfig).mockResolvedValue(config);
}

function backendUnreachable() {
  const failure = new ApiError(
    "Could not reach Mind Archive. Is the backend running?",
  );
  vi.mocked(fetchHealth).mockRejectedValue(failure);
  vi.mocked(fetchConfig).mockRejectedValue(failure);
}

/**
 * Render and wait for the initial load to settle.
 *
 * Without this, React warns that state updates happened outside `act(...)`:
 * the component fetches on mount, and a synchronous assertion runs before the
 * promise resolves.
 */
async function renderApp() {
  const result = render(<App />);
  await screen.findByText(config.archive_location);
  return result;
}

describe("the workspace", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    backendAvailable();
  });

  it("shows the product name", async () => {
    await renderApp();

    expect(
      screen.getByRole("heading", { name: "Mind Archive", level: 1 }),
    ).toBeInTheDocument();
  });

  it("tells you where your archive is stored", async () => {
    await renderApp();

    expect(screen.getByText(config.archive_location)).toBeInTheDocument();
    expect(screen.getByText("On this computer")).toBeInTheDocument();
  });

  it("states plainly that nothing is uploaded", async () => {
    await renderApp();

    expect(screen.getByText(config.privacy_note)).toBeInTheDocument();
  });

  it("shows cloud backup as off", async () => {
    await renderApp();

    expect(screen.getByText("Off")).toBeInTheDocument();
  });

  it("reports the backend as running", async () => {
    await renderApp();

    expect(screen.getByText("Running")).toBeInTheDocument();
  });
});

describe("when the backend is not running", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    backendUnreachable();
  });

  it("explains the problem in plain language", async () => {
    render(<App />);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not reach Mind Archive");
  });

  it("tells you how to start it", async () => {
    render(<App />);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("docker compose up");
  });

  it("still renders the page rather than breaking", async () => {
    render(<App />);

    await screen.findByRole("alert");
    expect(
      screen.getByRole("heading", { name: "Mind Archive", level: 1 }),
    ).toBeInTheDocument();
  });
});

/** Import now lives in the header, reachable from anywhere on the page. */
function importButton() {
  return screen.getByRole("button", { name: /^import/i });
}

describe("importing without scrolling", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    backendAvailable();
  });

  it("offers Import once, from the header", async () => {
    /* It used to appear twice — in the archive panel and in the nav row. Both
       moved into the header (D-037), where it is reachable wherever you have
       scrolled to, and there is only one of it. */
    await renderApp();

    expect(screen.getAllByRole("button", { name: /^import/i })).toHaveLength(1);
  });

  it("opens import in a dialog rather than further down the page", async () => {
    const user = userEvent.setup();
    await renderApp();

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    await user.click(importButton());

    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("closes on Escape", async () => {
    const user = userEvent.setup();
    await renderApp();

    await user.click(importButton());
    await user.keyboard("{Escape}");

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("closes on the close button", async () => {
    const user = userEvent.setup();
    await renderApp();

    await user.click(importButton());
    await user.click(screen.getByRole("button", { name: /close/i }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("gives focus back to whatever opened it", async () => {
    const user = userEvent.setup();
    await renderApp();

    const trigger = importButton();
    await user.click(trigger);
    await user.keyboard("{Escape}");

    expect(trigger).toHaveFocus();
  });
});

describe("moving around the page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    backendAvailable();
  });

  const NAV = [
    // Home is first and points at "/" rather than "#top", so copying the link
    // or opening it in a new tab behaves. A plain click is intercepted and
    // scrolled, because a real navigation would reload and lose the search.
    ["Home", "/"],
    ["Archive", "#archive"],
    ["Coming next", "#next"],
    ["Status", "#status"],
    ["Support", "#support"],
    ["Contribute", "#contribute"],
  ] as const;

  it("links to each section from the header", async () => {
    await renderApp();

    const nav = screen.getByRole("navigation", {
      name: /sections of this page/i,
    });

    for (const [label, href] of NAV) {
      expect(within(nav).getByRole("link", { name: label })).toHaveAttribute(
        "href",
        href,
      );
    }
  });

  it("anchors every one of those sections so no link is a dead end", async () => {
    const { container } = await renderApp();

    for (const [, href] of NAV) {
      // "/" is not an anchor; its scroll target is #top, checked below.
      if (href.startsWith("#")) {
        expect(container.querySelector(href)).not.toBeNull();
      }
    }
    expect(container.querySelector("#top")).not.toBeNull();
  });

  it("offers a way back to the top from the bottom", async () => {
    await renderApp();

    // Scoped to the footer: the floating control below carries the same name
    // and the same destination, so an unscoped query now finds two.
    const footer = screen.getByRole("contentinfo");
    expect(
      within(footer).getByRole("link", { name: /back to top/i }),
    ).toHaveAttribute("href", "#top");
  });

  /** jsdom implements no scrolling at all, so the target has to say it moved. */
  function watchScrollTo(container: HTMLElement) {
    const target = container.querySelector("#top") as HTMLElement;
    const scrollIntoView = vi.fn();
    target.scrollIntoView = scrollIntoView;
    return scrollIntoView;
  }

  it("takes you back to the top from the brand, without navigating away", async () => {
    /* The brand used to cancel its own click and do nothing else, which made
       it a link that did nothing at all. It scrolls now — a real navigation
       would reload and throw away the search and any open conversation. */
    const user = userEvent.setup();
    const { container } = await renderApp();
    const scrolled = watchScrollTo(container);

    const brand = screen.getByRole("link", { name: "Mind Archive" });
    expect(brand).toHaveAttribute("href", "/");

    await user.click(brand);

    expect(scrolled).toHaveBeenCalled();
  });

  it("leaves a modified click on the brand to the browser", async () => {
    /* Ctrl-click, and the rest, must still open a new tab or copy the link.
       Intercepting every click would break that. */
    const user = userEvent.setup();
    const { container } = await renderApp();
    const scrolled = watchScrollTo(container);

    await user.keyboard("{Control>}");
    await user.click(screen.getByRole("link", { name: "Mind Archive" }));
    await user.keyboard("{/Control}");

    expect(scrolled).not.toHaveBeenCalled();
  });
});

describe("back to top", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    backendAvailable();
    scrollTo(0);
  });

  /** jsdom does not scroll, so say where the page is and tell the page so. */
  function scrollTo(y: number) {
    Object.defineProperty(window, "scrollY", { value: y, configurable: true });
    // fireEvent rather than dispatchEvent: it wraps the listener's state
    // update in act(), so React has re-rendered before the next assertion.
    fireEvent.scroll(window);
  }

  function floatingLink() {
    return document.querySelector(".backtotop");
  }

  it("stays out of the way until there is something to scroll back from", async () => {
    await renderApp();

    expect(floatingLink()).not.toHaveClass("backtotop--shown");
  });

  it("appears once you are a screen down, and points at the top", async () => {
    await renderApp();

    scrollTo(window.innerHeight + 1);

    expect(floatingLink()).toHaveClass("backtotop--shown");
    expect(floatingLink()).toHaveAttribute("href", "#top");
  });

  it("goes away again when you are back at the top", async () => {
    await renderApp();

    scrollTo(window.innerHeight + 1);
    expect(floatingLink()).toHaveClass("backtotop--shown");

    scrollTo(0);
    expect(floatingLink()).not.toHaveClass("backtotop--shown");
  });

  it("hides the nav when there is nothing to navigate to", async () => {
    vi.clearAllMocks();
    backendUnreachable();
    render(<App />);
    await screen.findByRole("alert");

    expect(
      screen.queryByRole("navigation", { name: /sections of this page/i }),
    ).not.toBeInTheDocument();
  });
});

describe("exporting", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    backendAvailable();
    archiveWithConversations();
  });

  it("opens a dialog rather than downloading straight away", async () => {
    const user = userEvent.setup();
    await renderApp();

    /* An export can be large. Saying what is in it first is worth one click,
       and the download inside the dialog is still a plain link. */
    await user.click(
      await screen.findByRole("button", { name: /^export$/i }),
    );

    const dialog = await screen.findByRole("dialog", {
      name: /export everything/i,
    });
    expect(dialog).toBeInTheDocument();
    expect(
      within(dialog).getByRole("link", { name: /download the zip/i }),
    ).toBeInTheDocument();
  });

  it("says the index is left out, because it rebuilds itself", async () => {
    const user = userEvent.setup();
    await renderApp();

    await user.click(
      await screen.findByRole("button", { name: /^export$/i }),
    );

    expect(
      await screen.findByText(/search index is deliberately left out/i),
    ).toBeInTheDocument();
  });

  it("closes on Escape", async () => {
    const user = userEvent.setup();
    await renderApp();

    await user.click(
      await screen.findByRole("button", { name: /^export$/i }),
    );
    await screen.findByRole("dialog", { name: /export everything/i });

    await user.keyboard("{Escape}");

    expect(
      screen.queryByRole("dialog", { name: /export everything/i }),
    ).not.toBeInTheDocument();
  });
});

describe("support, contributing and the footer", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    backendAvailable();
  });

  it("promises not to nag, which is the whole posture of the panel", async () => {
    await renderApp();

    expect(screen.getByText(/never nags/i)).toBeInTheDocument();
  });

  it("quotes no price, because nothing is for sale", async () => {
    /* Mind Archive is proprietary and no licence is on offer (D-046). The panel
       must not invent a commercial tier: it says so and gives an address. */
    await renderApp();

    expect(screen.getByText(/nothing is for sale yet/i)).toBeInTheDocument();
  });

  it("gives a way to ask a licensing question", async () => {
    await renderApp();

    /* The configured address rather than a copy of it: this test asserts that
       the panel shows whoever `support.ts` says to write to, not that the
       address is one particular value. Hardcoding it here meant changing the
       contact address broke a test for no reason. */
    const link = screen.getByRole("link", { name: SUPPORT.contactEmail });
    expect(link.getAttribute("href")).toMatch(/^mailto:/);
    expect(link.getAttribute("href")).toContain("Licensing%20enquiry");
  });

  it("sends people to the website rather than to a payment provider", async () => {
    /* LICENSING.md promises the application will never contain payment code.
       The Support panel therefore links out to a page and stops there — no
       provider, no amounts, no checkout inside the app (D-038). */
    await renderApp();

    /* The path, not the host: the host comes from VITE_SITE_URL and defaults
       to the local Jekyll server so the link is usable while developing.
       Pinning the production URL here would make the test fail locally for a
       reason that has nothing to do with the behaviour being checked. */
    const link = screen.getByRole("link", { name: /ways to support this/i });
    expect(link.getAttribute("href")).toMatch(/\/support\/$/);
  });

  it("contains no payment provider anywhere in the interface", async () => {
    /* The guard for the promise above. If someone ever pastes a checkout URL
       into the app, this fails — which is the point. */
    const { container } = await renderApp();
    const html = container.innerHTML.toLowerCase();

    for (const provider of [
      "stripe",
      "paypal",
      "paddle",
      "lemonsqueezy",
      "polar.sh",
      "checkout",
    ]) {
      expect(html).not.toContain(provider);
    }
  });

  it("asks people not to send their actual conversations", async () => {
    await renderApp();

    expect(
      screen.getByText(/never send the file itself/i),
    ).toBeInTheDocument();
  });

  it("carries a copyright line and the licence", async () => {
    await renderApp();

    const footer = screen.getByText(/© 2026 Mind Archive/i);
    expect(footer).toHaveTextContent(/all rights reserved/i);
  });
});

describe("appearance", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    backendAvailable();
    window.localStorage.clear();
  });

  /** Open one of the two menus and return the user-event instance. */
  async function openMenu(name: RegExp) {
    const user = userEvent.setup();
    await user.click(await screen.findByRole("button", { name }));
    return user;
  }

  it("names both menus, and says what is currently chosen", async () => {
    /* The trigger's accessible name carries the group and its value, because
       the visible label is dropped on a narrow screen and the icon alone
       would tell a screen reader nothing. */
    await renderApp();

    expect(
      screen.getByRole("button", { name: "Palette: Light minimal" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Theme: System" }),
    ).toBeInTheDocument();
  });

  it("starts on light minimal, following the system", async () => {
    await renderApp();

    expect(document.documentElement.getAttribute("data-palette")).toBe(
      "minimal",
    );

    await openMenu(/^Palette:/);
    expect(
      screen.getByRole("menuitemradio", { name: /Light minimal/ }),
    ).toBeChecked();
  });

  it("resolves system to a real theme rather than leaving it unset", async () => {
    await renderApp();

    expect(["light", "dark"]).toContain(
      document.documentElement.getAttribute("data-theme"),
    );
  });

  it("switches to dark and back", async () => {
    await renderApp();

    let user = await openMenu(/^Theme:/);
    await user.click(screen.getByRole("menuitemradio", { name: /Dark/ }));
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");

    user = await openMenu(/^Theme:/);
    await user.click(screen.getByRole("menuitemradio", { name: /^Light/ }));
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
  });

  it("remembers the theme choice", async () => {
    await renderApp();
    const user = await openMenu(/^Theme:/);
    await user.click(screen.getByRole("menuitemradio", { name: /Dark/ }));

    await waitFor(() => {
      expect(window.localStorage.getItem("mindarchive-theme")).toBe("dark");
    });
  });

  it("changes palette and remembers it", async () => {
    await renderApp();
    const user = await openMenu(/^Palette:/);
    await user.click(screen.getByRole("menuitemradio", { name: /Ink & violet/i }));

    expect(document.documentElement.getAttribute("data-palette")).toBe(
      "violet",
    );
    await waitFor(() => {
      expect(window.localStorage.getItem("mindarchive-palette")).toBe("violet");
    });
  });

  it("keeps palette and theme independent", async () => {
    await renderApp();
    let user = await openMenu(/^Palette:/);
    await user.click(screen.getByRole("menuitemradio", { name: /Warm paper/ }));

    user = await openMenu(/^Theme:/);
    await user.click(screen.getByRole("menuitemradio", { name: /Dark/ }));

    expect(document.documentElement.getAttribute("data-palette")).toBe("warm");
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("closes on Escape and gives focus back to the trigger", async () => {
    await renderApp();
    const trigger = screen.getByRole("button", { name: /^Theme:/ });
    const user = userEvent.setup();

    await user.click(trigger);
    expect(screen.getByRole("menu", { name: "Theme" })).toBeInTheDocument();

    await user.keyboard("{Escape}");

    expect(screen.queryByRole("menu", { name: "Theme" })).not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
  });

  it("moves between options with the arrow keys", async () => {
    await renderApp();
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: /^Theme:/ }));

    // Opening focuses the current choice, which is System — the last option.
    expect(screen.getByRole("menuitemradio", { name: /System/ })).toHaveFocus();

    await user.keyboard("{Home}");
    expect(screen.getByRole("menuitemradio", { name: /^Light/ })).toHaveFocus();

    await user.keyboard("{ArrowDown}");
    expect(screen.getByRole("menuitemradio", { name: /Dark/ })).toHaveFocus();
  });

  it("only one menu is open at a time", async () => {
    await renderApp();
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: /^Palette:/ }));
    expect(screen.getByRole("menu", { name: "Palette" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /^Theme:/ }));

    expect(
      screen.queryByRole("menu", { name: "Palette" }),
    ).not.toBeInTheDocument();
    expect(screen.getByRole("menu", { name: "Theme" })).toBeInTheDocument();
  });
});
