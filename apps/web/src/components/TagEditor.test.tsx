import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "../api";
import { TagEditor } from "./TagEditor";

vi.mock("../api", async () => {
  const actual = await vi.importActual<typeof import("../api")>("../api");
  return { ...actual, setTags: vi.fn() };
});

const { setTags } = await import("../api");

const summary = (tags: string[]) => ({
  path: "chatgpt/2024-03-14-Making sourdough",
  title: "Making sourdough",
  source: "chatgpt",
  created_at: "2024-03-14T09:30:00+00:00",
  updated_at: null,
  message_count: 2,
  tags,
  snippet: null,
});

describe("editing tags", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(setTags).mockImplementation((_path, tags) =>
      Promise.resolve(summary(tags)),
    );
  });

  it("shows the tags a conversation already has", () => {
    render(<TagEditor path="chatgpt/one" tags={["recipes", "bread"]} />);

    expect(screen.getByText("recipes")).toBeInTheDocument();
    expect(screen.getByText("bread")).toBeInTheDocument();
  });

  it("adds a tag", async () => {
    const user = userEvent.setup();
    render(<TagEditor path="chatgpt/one" tags={[]} />);

    await user.type(screen.getByLabelText(/add a tag/i), "recipes");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(setTags).toHaveBeenCalledWith("chatgpt/one", ["recipes"]);
    expect(await screen.findByText("recipes")).toBeInTheDocument();
  });

  it("adds a tag when Enter is pressed", async () => {
    const user = userEvent.setup();
    render(<TagEditor path="chatgpt/one" tags={[]} />);

    await user.type(screen.getByLabelText(/add a tag/i), "recipes{Enter}");

    await waitFor(() => expect(setTags).toHaveBeenCalledWith("chatgpt/one", ["recipes"]));
  });

  it("keeps the existing tags when adding another", async () => {
    const user = userEvent.setup();
    render(<TagEditor path="chatgpt/one" tags={["bread"]} />);

    await user.type(screen.getByLabelText(/add a tag/i), "recipes{Enter}");

    await waitFor(() =>
      expect(setTags).toHaveBeenCalledWith("chatgpt/one", ["bread", "recipes"]),
    );
  });

  it("removes a tag", async () => {
    const user = userEvent.setup();
    render(<TagEditor path="chatgpt/one" tags={["recipes", "bread"]} />);

    await user.click(screen.getByRole("button", { name: "Remove tag recipes" }));

    expect(setTags).toHaveBeenCalledWith("chatgpt/one", ["bread"]);
  });

  it("ignores a tag that is already there, whatever the capitalisation", async () => {
    const user = userEvent.setup();
    render(<TagEditor path="chatgpt/one" tags={["Recipes"]} />);

    await user.type(screen.getByLabelText(/add a tag/i), "recipes{Enter}");

    expect(setTags).not.toHaveBeenCalled();
  });

  it("ignores an empty tag", async () => {
    const user = userEvent.setup();
    render(<TagEditor path="chatgpt/one" tags={[]} />);

    await user.type(screen.getByLabelText(/add a tag/i), "   {Enter}");

    expect(setTags).not.toHaveBeenCalled();
  });

  it("clears the box after adding", async () => {
    const user = userEvent.setup();
    render(<TagEditor path="chatgpt/one" tags={[]} />);
    const input = screen.getByLabelText(/add a tag/i);

    await user.type(input, "recipes{Enter}");

    await waitFor(() => expect(input).toHaveValue(""));
  });

  it("tells the conversation view when tags change", async () => {
    const onChanged = vi.fn();
    const user = userEvent.setup();
    render(<TagEditor path="chatgpt/one" tags={[]} onChanged={onChanged} />);

    await user.type(screen.getByLabelText(/add a tag/i), "recipes{Enter}");

    await waitFor(() => expect(onChanged).toHaveBeenCalledWith(["recipes"]));
  });
});

describe("when a tag cannot be saved", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("puts the tag back and explains", async () => {
    /* The tag appears immediately so tagging feels instant. If the save fails,
       the interface must not keep showing something that was not stored. */
    vi.mocked(setTags).mockRejectedValue(
      new ApiError("Those tags could not be saved to your archive folder."),
    );

    const user = userEvent.setup();
    render(<TagEditor path="chatgpt/one" tags={["bread"]} />);

    await user.type(screen.getByLabelText(/add a tag/i), "recipes{Enter}");

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "could not be saved",
    );
    expect(screen.queryByText("recipes")).not.toBeInTheDocument();
    expect(screen.getByText("bread")).toBeInTheDocument();
  });
});
