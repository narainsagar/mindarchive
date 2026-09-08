import react from "@vitejs/plugin-react";
// From vitest/config rather than vite, so the `test` block below is typed.
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Bind to all interfaces so the dev server is reachable from outside the
    // Docker container. Compose decides what is actually published.
    host: true,
    watch: {
      // Docker on Windows and macOS cannot always deliver filesystem events
      // into the container, so fall back to polling there.
      usePolling: process.env.VITE_USE_POLLING === "true",
    },
  },
  preview: {
    port: 5173,
    host: true,
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
    css: false,
  },
});
