import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  applyPalette,
  applyTheme,
  getInitialPalette,
  getInitialTheme,
  resolveTheme,
  watchSystemTheme,
} from "./theme";

/** Pretend the operating system is asking for dark, or not. */
function systemIsDark(dark: boolean) {
  vi.spyOn(window, "matchMedia").mockReturnValue({
    matches: dark,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  } as unknown as MediaQueryList);
}

beforeEach(() => {
  window.localStorage.clear();
  document.documentElement.removeAttribute("data-theme");
  document.documentElement.removeAttribute("data-palette");
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("getInitialTheme", () => {
  it("follows the system until you choose otherwise", () => {
    expect(getInitialTheme()).toBe("system");
  });

  it("uses a stored choice", () => {
    window.localStorage.setItem("mindarchive-theme", "dark");

    expect(getInitialTheme()).toBe("dark");
  });

  it("keeps following the system when that is what was chosen", () => {
    window.localStorage.setItem("mindarchive-theme", "system");

    expect(getInitialTheme()).toBe("system");
  });

  it("ignores a stored value that is not a theme", () => {
    window.localStorage.setItem("mindarchive-theme", "banana");

    expect(getInitialTheme()).toBe("system");
  });

  it("falls back to the system when storage throws", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("storage is blocked");
    });

    expect(getInitialTheme()).toBe("system");
  });
});

describe("getInitialPalette", () => {
  it("defaults to light minimal", () => {
    expect(getInitialPalette()).toBe("minimal");
  });

  it("uses a stored choice", () => {
    window.localStorage.setItem("mindarchive-palette", "violet");

    expect(getInitialPalette()).toBe("violet");
  });

  it("ignores a stored value that is not a palette", () => {
    window.localStorage.setItem("mindarchive-palette", "chartreuse");

    expect(getInitialPalette()).toBe("minimal");
  });

  it("falls back to the default when storage throws", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("storage is blocked");
    });

    expect(getInitialPalette()).toBe("minimal");
  });
});

describe("resolveTheme", () => {
  it("passes an explicit choice straight through", () => {
    systemIsDark(true);

    expect(resolveTheme("light")).toBe("light");
    expect(resolveTheme("dark")).toBe("dark");
  });

  it("reads the system when the choice is system", () => {
    systemIsDark(true);
    expect(resolveTheme("system")).toBe("dark");

    systemIsDark(false);
    expect(resolveTheme("system")).toBe("light");
  });

  it("falls back to light when the browser cannot answer", () => {
    vi.spyOn(window, "matchMedia").mockImplementation(() => {
      throw new Error("matchMedia is unavailable");
    });

    expect(resolveTheme("system")).toBe("light");
  });
});

describe("applyTheme", () => {
  it("stamps the resolved theme, never the word system", () => {
    systemIsDark(true);
    applyTheme("system");

    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("sets the attribute the stylesheet reads", () => {
    applyTheme("dark");

    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("remembers the choice rather than the result", () => {
    systemIsDark(true);
    applyTheme("system");

    expect(window.localStorage.getItem("mindarchive-theme")).toBe("system");
  });

  it("still applies the theme when storage throws", () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("storage is blocked");
    });

    expect(() => applyTheme("dark")).not.toThrow();
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });
});

describe("applyPalette", () => {
  it("sets the attribute the stylesheet reads", () => {
    applyPalette("warm");

    expect(document.documentElement.getAttribute("data-palette")).toBe("warm");
  });

  it("remembers the choice", () => {
    applyPalette("violet");

    expect(window.localStorage.getItem("mindarchive-palette")).toBe("violet");
  });

  it("still applies the palette when storage throws", () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("storage is blocked");
    });

    expect(() => applyPalette("warm")).not.toThrow();
    expect(document.documentElement.getAttribute("data-palette")).toBe("warm");
  });
});

describe("watchSystemTheme", () => {
  it("listens, and stops listening when told to", () => {
    const addEventListener = vi.fn();
    const removeEventListener = vi.fn();
    vi.spyOn(window, "matchMedia").mockReturnValue({
      matches: false,
      addEventListener,
      removeEventListener,
    } as unknown as MediaQueryList);

    const onChange = vi.fn();
    const stop = watchSystemTheme(onChange);

    expect(addEventListener).toHaveBeenCalledWith("change", onChange);

    stop();
    expect(removeEventListener).toHaveBeenCalledWith("change", onChange);
  });

  it("does nothing rather than throwing when matchMedia is missing", () => {
    vi.spyOn(window, "matchMedia").mockImplementation(() => {
      throw new Error("matchMedia is unavailable");
    });

    expect(() => watchSystemTheme(vi.fn())()).not.toThrow();
  });
});
