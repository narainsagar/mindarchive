import "@testing-library/jest-dom/vitest";

import { afterEach, vi } from "vitest";

/**
 * jsdom does not implement `matchMedia`, which the theme code calls to read the
 * system colour preference. Provide a stub that reports "light", which is the
 * product default anyway.
 */
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }),
});

afterEach(() => {
  window.localStorage.clear();
  document.documentElement.removeAttribute("data-theme");
  vi.restoreAllMocks();
});
