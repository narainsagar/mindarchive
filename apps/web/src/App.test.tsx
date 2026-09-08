import { render, screen, waitFor } from "@testing-library/react";
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

describe("the theme", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    backendAvailable();
  });

  it("starts in light mode", async () => {
    await renderApp();

    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
  });

  it("switches to dark and back", async () => {
    const user = userEvent.setup();
    await renderApp();

    await user.click(screen.getByRole("button", { name: /switch to dark/i }));
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");

    await user.click(screen.getByRole("button", { name: /switch to light/i }));
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
  });

  it("remembers the choice", async () => {
    const user = userEvent.setup();
    await renderApp();

    await user.click(screen.getByRole("button", { name: /switch to dark/i }));

    await waitFor(() => {
      expect(window.localStorage.getItem("mind-archive-theme")).toBe("dark");
    });
  });
});
