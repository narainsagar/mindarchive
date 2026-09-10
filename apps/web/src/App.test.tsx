import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import type { Health, PublicConfig } from "./api";
import { ApiError } from "./api";

vi.mock("./api", async () => {
  const actual = await vi.importActual<typeof import("./api")>("./api");
  return {
    ...actual,
    fetchHealth: vi.fn(),
    fetchConfig: vi.fn(),
  };
});

const { fetchConfig, fetchHealth } = await import("./api");

const health: Health = {
  status: "ok",
  version: "0.1.0",
  message: "Mind Archive is running.",
};

const config: PublicConfig = {
  version: "0.1.0",
  storage_mode: "local",
  cloud_enabled: false,
  archive_location: "/home/someone/mind-archive/data/archive",
  database_location: "/home/someone/mind-archive/data/mind_archive.db",
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

/** The Import button in the archive header — there is a second one in the nav. */
function importButton() {
  const [button] = screen.getAllByRole("button", { name: /^import/i });
  if (!button) throw new Error("no Import button was rendered");
  return button;
}

describe("importing without scrolling", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    backendAvailable();
  });

  it("offers Import from the archive header and the nav", async () => {
    await renderApp();

    expect(screen.getAllByRole("button", { name: /^import/i })).toHaveLength(2);
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
      expect(container.querySelector(href)).not.toBeNull();
    }
    expect(container.querySelector("#top")).not.toBeNull();
  });

  it("offers a way back to the top from the bottom", async () => {
    await renderApp();

    expect(screen.getByRole("link", { name: /back to top/i })).toHaveAttribute(
      "href",
      "#top",
    );
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

describe("support, contributing and the footer", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    backendAvailable();
  });

  it("says the noncommercial licence is free, and stays free", async () => {
    await renderApp();

    expect(
      screen.getByText(/free for personal use, and for schools/i),
    ).toBeInTheDocument();
  });

  it("gives a way to ask for a commercial licence", async () => {
    await renderApp();

    const link = screen.getByRole("link", { name: /kishor3947@gmail\.com/i });
    expect(link.getAttribute("href")).toMatch(/^mailto:/);
    expect(link.getAttribute("href")).toContain("Commercial%20licence");
  });

  it("shows no donation buttons until they are configured", async () => {
    /* Better nothing than a dead link. `support.ts` ships with blank URLs and
       `configuredDonations` filters them out. */
    await renderApp();

    expect(
      screen.getByText(/donation links are not set up yet/i),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("link", { name: /buy me a coffee/i }),
    ).not.toBeInTheDocument();
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
    expect(footer).toHaveTextContent(/PolyForm Noncommercial 1\.0\.0/);
  });
});

describe("appearance", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    backendAvailable();
    window.localStorage.clear();
  });

  it("names both groups for screen readers, though the words are not shown", async () => {
    /* "Palette" and "Theme" were removed from the header (D-034), but only
       visually — `.segmented__legend` in styles.css hides them. The legends
       stay in the accessibility tree, because without them a screen reader
       announces six unrelated radio buttons with no idea which three belong
       together.

       That they are invisible is not asserted here and cannot be: jsdom does
       not load the stylesheet, so every element reports as visible. The CSS is
       the mechanism; this test guards the half that would otherwise be
       "tidied away" by someone deleting a legend they could not see. */
    await renderApp();

    expect(screen.getByRole("group", { name: "Palette" })).toBeInTheDocument();
    expect(screen.getByRole("group", { name: "Theme" })).toBeInTheDocument();
  });

  it("starts on light minimal, following the system", async () => {
    await renderApp();

    expect(document.documentElement.getAttribute("data-palette")).toBe(
      "minimal",
    );
    expect(screen.getByRole("radio", { name: "Light minimal" })).toBeChecked();
    expect(screen.getByRole("radio", { name: "System" })).toBeChecked();
  });

  it("resolves system to a real theme rather than leaving it unset", async () => {
    await renderApp();

    expect(["light", "dark"]).toContain(
      document.documentElement.getAttribute("data-theme"),
    );
  });

  it("switches to dark and back", async () => {
    const user = userEvent.setup();
    await renderApp();

    await user.click(screen.getByRole("radio", { name: "Dark" }));
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");

    await user.click(screen.getByRole("radio", { name: "Light" }));
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
  });

  it("remembers the theme choice", async () => {
    const user = userEvent.setup();
    await renderApp();

    await user.click(screen.getByRole("radio", { name: "Dark" }));

    await waitFor(() => {
      expect(window.localStorage.getItem("mind-archive-theme")).toBe("dark");
    });
  });

  it("changes palette and remembers it", async () => {
    const user = userEvent.setup();
    await renderApp();

    await user.click(screen.getByRole("radio", { name: "Ink & violet" }));

    expect(document.documentElement.getAttribute("data-palette")).toBe(
      "violet",
    );
    await waitFor(() => {
      expect(window.localStorage.getItem("mind-archive-palette")).toBe(
        "violet",
      );
    });
  });

  it("keeps palette and theme independent", async () => {
    const user = userEvent.setup();
    await renderApp();

    await user.click(screen.getByRole("radio", { name: "Warm paper" }));
    await user.click(screen.getByRole("radio", { name: "Dark" }));

    expect(document.documentElement.getAttribute("data-palette")).toBe("warm");
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });
});
