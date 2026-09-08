import { beforeEach, describe, expect, it, vi } from "vitest";

import { applyTheme, getInitialTheme } from "./theme";

describe("getInitialTheme", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("defaults to light", () => {
    expect(getInitialTheme()).toBe("light");
  });

  it("uses a stored choice", () => {
    window.localStorage.setItem("mind-archive-theme", "dark");

    expect(getInitialTheme()).toBe("dark");
  });

  it("ignores a stored value that is not a theme", () => {
    window.localStorage.setItem("mind-archive-theme", "banana");

    expect(getInitialTheme()).toBe("light");
  });

  it("follows the system preference when nothing is stored", () => {
    vi.spyOn(window, "matchMedia").mockReturnValue({
      matches: true,
    } as MediaQueryList);

    expect(getInitialTheme()).toBe("dark");
  });

  it("falls back to light when storage throws", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("storage is blocked");
    });

    expect(getInitialTheme()).toBe("light");
  });
});

describe("applyTheme", () => {
  it("sets the attribute the stylesheet reads", () => {
    applyTheme("dark");

    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("remembers the choice", () => {
    applyTheme("dark");

    expect(window.localStorage.getItem("mind-archive-theme")).toBe("dark");
  });

  it("still applies the theme when storage throws", () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("storage is blocked");
    });

    expect(() => applyTheme("dark")).not.toThrow();
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });
});
