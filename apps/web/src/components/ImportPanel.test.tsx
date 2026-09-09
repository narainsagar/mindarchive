import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { ImportSummary, InboxStatus } from "../api";
import { ApiError } from "../api";
import { ImportPanel as ImportPanelBase } from "./ImportPanel";

vi.mock("../api", async () => {
  const actual = await vi.importActual<typeof import("../api")>("../api");
  return {
    ...actual,
    importExport: vi.fn(),
    fetchInbox: vi.fn(),
    scanInbox: vi.fn(),
  };
});

const { importExport, fetchInbox, scanInbox } = await import("../api");

const inbox = {
  folder: "/home/someone/mind-archive/data/inbox",
  managed: true,
  moves_files: true,
  waiting: 0,
};

/**
 * The inbox now comes from `useInbox` in App rather than being fetched by the
 * panel, so the tests supply it. `currentInbox` lets a test change what the
 * panel sees before rendering.
 */
let currentInbox: InboxStatus | null = inbox;
const refreshInbox = vi.fn(async () => {});

function ImportPanel(props: { onImported?: () => void } = {}) {
  return (
    <ImportPanelBase
      inbox={{ status: currentInbox, refresh: refreshInbox }}
      {...props}
    />
  );
}

/** The export instructions live behind a disclosure now — open it. */
async function openInstructions() {
  const user = userEvent.setup();
  await user.click(screen.getByText(/how do i get my export/i));
  return user;
}

const success: ImportSummary = {
  ok: true,
  message: "Imported 412 conversations.",
  source: "chatgpt",
  imported: 412,
  new: 412,
  updated: 0,
  unchanged: 0,
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
    currentInbox = inbox;
    vi.mocked(importExport).mockResolvedValue(success);
    vi.mocked(fetchInbox).mockResolvedValue(inbox);
  });

  it("keeps the export instructions out of the way until asked", () => {
    render(<ImportPanel />);

    /* The instructions matter enormously the first time and never again, so
       they sit behind a disclosure rather than filling the dialog. */
    const disclosure = screen
      .getByText(/how do i get my export/i)
      .closest("details");

    expect(disclosure).not.toBeNull();
    expect(disclosure).not.toHaveAttribute("open");
  });

  it("explains where to get an export", async () => {
    render(<ImportPanel />);
    await openInstructions();

    expect(
      screen.getByText(/Settings → Data controls → Export data/),
    ).toBeInTheDocument();
  });

  it("says the export takes days, not hours", async () => {
    /* This panel used to say "up to 24 hours", which was wrong in the most
       misleading way: 24 hours is the download deadline, not the wait. */
    render(<ImportPanel />);

    expect(await screen.findByText(/can take a few days/i)).toBeInTheDocument();
  });

  it("warns that the download link expires", async () => {
    render(<ImportPanel />);

    expect(
      await screen.findByText(/expires 24 hours after the email arrives/i),
    ).toBeInTheDocument();
  });

  it("warns that asking again cancels the previous request", async () => {
    render(<ImportPanel />);

    expect(
      await screen.findByText(/cancels your previous request/i),
    ).toBeInTheDocument();
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
    expect(onImported).toHaveBeenCalled();
  });
});

describe("the inbox", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(importExport).mockResolvedValue(success);
    vi.mocked(fetchInbox).mockResolvedValue(inbox);
    vi.mocked(scanInbox).mockResolvedValue({
      ok: true,
      message: "Read 1 file: 412 new.",
      scanned: 1,
      imported_files: 1,
      failed_files: 0,
      new: 412,
      updated: 0,
      unchanged: 0,
      problems: [],
    });
  });

  it("tells you where to put the file", async () => {
    render(<ImportPanel />);

    expect(await screen.findByText(inbox.folder)).toBeInTheDocument();
  });

  it("says how many files are waiting", async () => {
    currentInbox = { ...inbox, waiting: 3 };

    render(<ImportPanel />);

    expect(await screen.findByText(/3 files waiting/i)).toBeInTheDocument();
  });

  it("says nothing about waiting files when there are none", () => {
    currentInbox = { ...inbox, waiting: 0 };

    render(<ImportPanel />);

    expect(screen.queryByText(/waiting/i)).not.toBeInTheDocument();
  });

  it("imports what is waiting when asked", async () => {
    const user = userEvent.setup();
    render(<ImportPanel />);

    await user.click(
      await screen.findByRole("button", { name: /check that folder now/i }),
    );

    expect(scanInbox).toHaveBeenCalledOnce();
    expect(await screen.findByText("Read 1 file: 412 new.")).toBeInTheDocument();
  });

  it("refreshes the archive after the inbox brings something in", async () => {
    const onImported = vi.fn();
    const user = userEvent.setup();
    render(<ImportPanel onImported={onImported} />);

    await user.click(
      await screen.findByRole("button", { name: /check that folder now/i }),
    );

    await screen.findByText("Read 1 file: 412 new.");
    expect(onImported).toHaveBeenCalled();
  });

  it("does not refresh the archive when nothing arrived", async () => {
    vi.mocked(scanInbox).mockResolvedValue({
      ok: true,
      message: "Nothing new in your inbox.",
      scanned: 0,
      imported_files: 0,
      failed_files: 0,
      new: 0,
      updated: 0,
      unchanged: 0,
      problems: [],
    });
    const onImported = vi.fn();
    const user = userEvent.setup();
    render(<ImportPanel onImported={onImported} />);

    await user.click(
      await screen.findByRole("button", { name: /check that folder now/i }),
    );

    await screen.findByText("Nothing new in your inbox.");
    expect(onImported).not.toHaveBeenCalled();
  });

  it("still works when the inbox cannot be read", async () => {
    /* The inbox is a convenience. Losing it must not break importing. */
    vi.mocked(fetchInbox).mockRejectedValue(new Error("no such folder"));

    render(<ImportPanel />);

    expect(
      await screen.findByRole("button", { name: "Import" }),
    ).toBeInTheDocument();
  });
});

describe("when the import cannot be done", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(fetchInbox).mockResolvedValue(inbox);
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
