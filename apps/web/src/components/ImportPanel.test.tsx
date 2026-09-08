import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { ImportSummary } from "../api";
import { ApiError } from "../api";
import { ImportPanel } from "./ImportPanel";

vi.mock("../api", async () => {
  const actual = await vi.importActual<typeof import("../api")>("../api");
  return { ...actual, importExport: vi.fn() };
});

const { importExport } = await import("../api");

const success: ImportSummary = {
  ok: true,
  message: "Imported 412 conversations.",
  source: "chatgpt",
  imported: 412,
  skipped: 0,
  problems: [],
  archive_location: "/home/someone/mind-archive/data/archive",
};

function exportFile(name = "chatgpt-export.zip") {
  return new File(["pretend zip bytes"], name, { type: "application/zip" });
}

async function chooseFile(file = exportFile()) {
  const user = userEvent.setup();
  const input = screen.getByLabelText(/choose an export file/i);
  await user.upload(input, file);
  return user;
}

describe("the import panel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(importExport).mockResolvedValue(success);
  });

  it("explains where to get an export", () => {
    render(<ImportPanel />);

    expect(screen.getByText(/Settings → Data controls → Export data/)).toBeInTheDocument();
  });

  it("cannot import until a file is chosen", () => {
    render(<ImportPanel />);

    expect(screen.getByRole("button", { name: "Import" })).toBeDisabled();
  });

  it("enables the button once a file is chosen", async () => {
    render(<ImportPanel />);

    await chooseFile();

    expect(screen.getByRole("button", { name: "Import" })).toBeEnabled();
  });

  it("imports the chosen file", async () => {
    render(<ImportPanel />);
    const user = await chooseFile();

    await user.click(screen.getByRole("button", { name: "Import" }));

    expect(importExport).toHaveBeenCalledOnce();
    expect(await screen.findByText("Imported 412 conversations.")).toBeInTheDocument();
  });

  it("says where the conversations were saved", async () => {
    render(<ImportPanel />);
    const user = await chooseFile();

    await user.click(screen.getByRole("button", { name: "Import" }));

    expect(
      await screen.findByText(success.archive_location as string),
    ).toBeInTheDocument();
  });

  it("reassures the user that nothing is uploaded", async () => {
    let release: (value: ImportSummary) => void = () => {};
    vi.mocked(importExport).mockReturnValue(
      new Promise<ImportSummary>((resolve) => {
        release = resolve;
      }),
    );

    render(<ImportPanel />);
    const user = await chooseFile();
    await user.click(screen.getByRole("button", { name: "Import" }));

    expect(await screen.findByText(/nothing is being uploaded anywhere/i)).toBeInTheDocument();

    // Let the import finish and wait for the result, so the state update
    // happens inside the test rather than after it.
    release(success);
    await screen.findByText(success.message);
  });

  it("calls back when an import succeeds", async () => {
    const onImported = vi.fn();
    render(<ImportPanel onImported={onImported} />);
    const user = await chooseFile();

    await user.click(screen.getByRole("button", { name: "Import" }));

    await screen.findByText(success.message);
    expect(onImported).toHaveBeenCalledWith(success);
  });
});

describe("when the import cannot be done", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows the backend's explanation", async () => {
    vi.mocked(importExport).mockResolvedValue({
      ...success,
      ok: false,
      imported: 0,
      message:
        "That file was not recognised. Mind Archive currently reads ChatGPT exports.",
      archive_location: null,
    });

    render(<ImportPanel />);
    const user = await chooseFile(exportFile("holiday-photos.zip"));
    await user.click(screen.getByRole("button", { name: "Import" }));

    expect(await screen.findByText(/was not recognised/)).toBeInTheDocument();
  });

  it("reports a failure in plain language", async () => {
    vi.mocked(importExport).mockRejectedValue(
      new ApiError("Could not reach Mind Archive. Is the backend running?"),
    );

    render(<ImportPanel />);
    const user = await chooseFile();
    await user.click(screen.getByRole("button", { name: "Import" }));

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not reach Mind Archive");
  });

  it("lists what could not be read, without hiding it", async () => {
    vi.mocked(importExport).mockResolvedValue({
      ...success,
      imported: 410,
      skipped: 2,
      message: "Imported 410 conversations, skipped 2 that could not be read.",
      problems: [
        "Conversation 12 could not be read (KeyError).",
        "Conversation 88 had no readable messages.",
      ],
    });

    render(<ImportPanel />);
    const user = await chooseFile();
    await user.click(screen.getByRole("button", { name: "Import" }));

    await screen.findByText(/skipped 2/);
    await user.click(screen.getByText(/What could not be read \(2\)/));

    expect(screen.getByText(/Conversation 12 could not be read/)).toBeInTheDocument();
  });
});
