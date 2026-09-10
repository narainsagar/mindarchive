import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { ConversationDetail, ConversationList } from "../api";
import { ArchivePanel } from "./ArchivePanel";

vi.mock("../api", async () => {
  const actual = await vi.importActual<typeof import("../api")>("../api");
  return {
    ...actual,
    fetchConversations: vi.fn(),
    fetchConversation: vi.fn(),
  };
});

const { fetchConversations, fetchConversation } = await import("../api");

function summary(overrides: Partial<ConversationList["conversations"][0]> = {}) {
  return {
    path: "chatgpt/2024-03-14-Making sourdough",
    title: "Making sourdough",
    source: "chatgpt",
    created_at: "2024-03-14T09:30:00+00:00",
    updated_at: null,
    message_count: 2,
    tags: [],
    snippet: null,
    ...overrides,
  };
}

function list(overrides: Partial<ConversationList> = {}): ConversationList {
  return {
    conversations: [summary()],
    total: 1,
    limit: 25,
    offset: 0,
    sources: { chatgpt: 1 },
    tags: {},
    ...overrides,
  };
}

const detail: ConversationDetail = {
  ...summary(),
  body: "## You\n\nHow do I make sourdough?\n\n## Assistant\n\nStart a starter.",
  source_id: "conversation-1",
};

describe("browsing the archive", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(fetchConversations).mockResolvedValue(list());
    vi.mocked(fetchConversation).mockResolvedValue(detail);
  });

  it("lists what is in the archive", async () => {
    render(<ArchivePanel />);

    expect(await screen.findByText("Making sourdough")).toBeInTheDocument();
  });

  it("shows how many conversations there are", async () => {
    vi.mocked(fetchConversations).mockResolvedValue(list({ total: 412 }));

    render(<ArchivePanel />);

    expect(await screen.findByText("412 conversations")).toBeInTheDocument();
  });

  it("describes each conversation", async () => {
    render(<ArchivePanel />);

    // The date is formatted in the viewer's locale, so the exact wording
    // depends on where they are. Assert the date is shown and readable, not
    // that it matches one country's convention.
    expect(await screen.findByText(/2024/)).toBeInTheDocument();
    expect(screen.getByText("2 messages")).toBeInTheDocument();
  });

  it("copes with a conversation that has no date", async () => {
    vi.mocked(fetchConversations).mockResolvedValue(
      list({ conversations: [summary({ created_at: null })] }),
    );

    render(<ArchivePanel />);

    await screen.findByText("Making sourdough");
    expect(screen.queryByText(/Invalid Date/)).not.toBeInTheDocument();
  });

  it("says so when the archive is empty", async () => {
    vi.mocked(fetchConversations).mockResolvedValue(
      list({ conversations: [], total: 0 }),
    );

    render(<ArchivePanel />);

    expect(await screen.findByText(/Nothing here yet/)).toBeInTheDocument();
  });

  it("explains when the backend cannot be reached", async () => {
    const { ApiError } = await import("../api");
    vi.mocked(fetchConversations).mockRejectedValue(
      new ApiError("Could not reach Mind Archive. Is the backend running?"),
    );

    render(<ArchivePanel />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Could not reach Mind Archive",
    );
  });
});

describe("searching", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(fetchConversations).mockResolvedValue(list());
    vi.mocked(fetchConversation).mockResolvedValue(detail);
  });

  it("searches for what was typed", async () => {
    const user = userEvent.setup();
    render(<ArchivePanel />);
    await screen.findByText("Making sourdough");

    await user.type(screen.getByLabelText(/search your conversations/i), "bread");

    await waitFor(() =>
      expect(fetchConversations).toHaveBeenCalledWith(
        expect.objectContaining({ query: "bread" }),
      ),
    );
  });

  it("waits for a pause rather than searching on every keystroke", async () => {
    const user = userEvent.setup();
    render(<ArchivePanel />);
    await screen.findByText("Making sourdough");
    vi.mocked(fetchConversations).mockClear();

    await user.type(screen.getByLabelText(/search your conversations/i), "bread");

    await waitFor(() => expect(fetchConversations).toHaveBeenCalled());
    expect(vi.mocked(fetchConversations).mock.calls.length).toBeLessThan(5);
  });

  it("says so when nothing matched", async () => {
    const user = userEvent.setup();
    render(<ArchivePanel />);
    await screen.findByText("Making sourdough");

    vi.mocked(fetchConversations).mockResolvedValue(
      list({ conversations: [], total: 0 }),
    );
    await user.type(screen.getByLabelText(/search your conversations/i), "kangaroo");

    expect(await screen.findByText(/Nothing matched/)).toBeInTheDocument();
  });

  it("highlights the matching words in a snippet", async () => {
    vi.mocked(fetchConversations).mockResolvedValue(
      list({
        conversations: [
          summary({ snippet: "a good <<sourdough>> starter needs time" }),
        ],
      }),
    );

    render(<ArchivePanel />);

    const mark = await screen.findByText("sourdough");
    expect(mark.tagName).toBe("MARK");
  });

  it("never renders snippet text as markup", async () => {
    /* A snippet is part of someone's conversation. If it contains HTML, that
       must appear as characters, not as elements. */
    vi.mocked(fetchConversations).mockResolvedValue(
      list({
        conversations: [
          summary({ snippet: "look: <img src=x onerror=alert(1)> and <<hi>>" }),
        ],
      }),
    );

    const { container } = render(<ArchivePanel />);

    await screen.findByText("hi");
    expect(container.querySelector("img")).toBeNull();
    expect(container.textContent).toContain("<img src=x onerror=alert(1)>");
  });
});

describe("reading a conversation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(fetchConversations).mockResolvedValue(list());
    vi.mocked(fetchConversation).mockResolvedValue(detail);
  });

  it("opens the conversation that was chosen", async () => {
    const user = userEvent.setup();
    render(<ArchivePanel />);

    await user.click(await screen.findByText("Making sourdough"));

    expect(fetchConversation).toHaveBeenCalledWith(detail.path);
    expect(
      await screen.findByText("How do I make sourdough?"),
    ).toBeInTheDocument();
  });

  it("renders the Markdown rather than showing it raw", async () => {
    const user = userEvent.setup();
    render(<ArchivePanel />);

    await user.click(await screen.findByText("Making sourdough"));

    const heading = await screen.findByRole("heading", { name: "You" });
    expect(heading).toBeInTheDocument();
  });

  it("goes back to the list", async () => {
    const user = userEvent.setup();
    render(<ArchivePanel />);
    await user.click(await screen.findByText("Making sourdough"));
    await screen.findByText("How do I make sourdough?");

    await user.click(screen.getByRole("button", { name: /back to your archive/i }));

    expect(
      await screen.findByLabelText(/search your conversations/i),
    ).toBeInTheDocument();
  });

  it("never renders HTML hidden in a conversation", async () => {
    /* The body came from a provider export. It must not be able to put markup
       into the page. */
    vi.mocked(fetchConversation).mockResolvedValue({
      ...detail,
      body: "Here is a tag: <img src=x onerror=alert(1)>\n\n<script>alert(2)</script>",
    });

    const user = userEvent.setup();
    const { container } = render(<ArchivePanel />);
    await user.click(await screen.findByText("Making sourdough"));

    await screen.findByText(/Here is a tag/);
    expect(container.querySelector("img")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
  });

  it("explains when a conversation cannot be opened", async () => {
    const { ApiError } = await import("../api");
    vi.mocked(fetchConversation).mockRejectedValue(
      new ApiError("No such conversation.", 404),
    );

    const user = userEvent.setup();
    render(<ArchivePanel />);
    await user.click(await screen.findByText("Making sourdough"));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "No such conversation.",
    );
  });
});

describe("exporting the archive", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(fetchConversations).mockResolvedValue(list());
    vi.mocked(fetchConversation).mockResolvedValue(detail);
  });

  it("hands the export over to whoever opens the dialog", async () => {
    /* The panel no longer downloads directly — it asks App to open the export
       dialog, and passes the count so the dialog can say what is in the zip.
       The download itself is a plain link inside that dialog. */
    const onExport = vi.fn();
    const user = userEvent.setup();
    render(<ArchivePanel onExport={onExport} />);

    await user.click(
      await screen.findByRole("button", { name: /export everything/i }),
    );

    expect(onExport).toHaveBeenCalledWith(1);
  });

  it("offers no export when nobody is listening for it", async () => {
    render(<ArchivePanel />);

    await screen.findByText(/making sourdough/i);
    expect(
      screen.queryByRole("button", { name: /export everything/i }),
    ).not.toBeInTheDocument();
  });

  it("does not offer an export of an empty archive", async () => {
    vi.mocked(fetchConversations).mockResolvedValue(
      list({ conversations: [], total: 0 }),
    );

    render(<ArchivePanel />);

    await screen.findByText(/Nothing here yet/);
    expect(
      screen.queryByRole("link", { name: /export everything/i }),
    ).not.toBeInTheDocument();
  });
});
