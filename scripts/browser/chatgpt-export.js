/*
 * Export your ChatGPT conversations from your own browser.
 *
 * ─────────────────────────────────────────────────────────────────────────
 * THIS IS NOT PART OF MIND ARCHIVE.
 *
 * It is a convenience script you run yourself, in your own browser, on your
 * own account. Mind Archive never runs it, never sees your session, and never
 * contacts OpenAI. All it ever does is read the file this produces.
 *
 * Read it before you run it. It is short on purpose.
 * ─────────────────────────────────────────────────────────────────────────
 *
 * WHY THIS EXISTS
 *
 * OpenAI's official export is the right way to get your data, but its own
 * email says it "may take a few days". This does the same job in a few minutes
 * by asking ChatGPT's web app for your conversations the same way the page you
 * are looking at already does.
 *
 * WHAT YOU SHOULD KNOW FIRST
 *
 *   - These endpoints are undocumented. They are not part of OpenAI's public
 *     API and may change, break, or be blocked at any time without notice.
 *   - Using them may violate OpenAI's Terms of Use. The counter-argument is
 *     that this is your own data, which GDPR Article 20 gives you a right to
 *     port. That is a real argument, but it is yours to weigh, not ours.
 *   - Requesting too fast can trigger rate limiting on your account. This
 *     script deliberately goes slowly.
 *   - It cannot download images or file attachments. The official export can.
 *     For a complete archive, use the official export.
 *
 * NEVER paste your session token into any website or application. This script
 * does not ask you to, and nothing legitimate ever should — that token can read
 * everything in your account and send messages as you.
 *
 * HOW TO USE IT
 *
 *   1. Open https://chatgpt.com and make sure you are logged in.
 *   2. Open the developer console:  F12,  or  Ctrl+Shift+J  /  Cmd+Option+J
 *   3. If the console asks you to type "allow pasting", do that first.
 *   4. Paste this entire file and press Enter.
 *   5. Wait. Progress is printed as it goes.
 *   6. A file called conversations.json downloads when it finishes.
 *   7. Put that file in your Mind Archive inbox folder — by default
 *      `data/inbox/` — and it imports itself.
 */

(async () => {
  "use strict";

  // Slow on purpose. You are a person reading your own history, not a crawler.
  const PAUSE_MS = 350;
  const PAGE_SIZE = 100;

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  function log(message) {
    console.log(`%c[mind archive] ${message}`, "color:#6b5b45");
  }

  // The page is already authenticated. This reads the session the browser
  // holds; the token is never displayed, stored, or sent anywhere but back to
  // ChatGPT itself.
  async function accessToken() {
    const response = await fetch("/api/auth/session", {
      credentials: "include",
    });
    if (!response.ok) {
      throw new Error(
        "Could not read your ChatGPT session. Are you logged in on this tab?",
      );
    }
    const session = await response.json();
    if (!session || !session.accessToken) {
      throw new Error("You do not appear to be logged in to ChatGPT.");
    }
    return session.accessToken;
  }

  async function get(path, token) {
    const response = await fetch(path, {
      credentials: "include",
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 429) {
      log("Rate limited — waiting 30 seconds before trying again.");
      await sleep(30000);
      return get(path, token);
    }
    if (!response.ok) {
      throw new Error(`${path} returned ${response.status}`);
    }
    return response.json();
  }

  async function listConversations(token) {
    const found = [];
    let offset = 0;

    for (;;) {
      const page = await get(
        `/backend-api/conversations?offset=${offset}&limit=${PAGE_SIZE}&order=updated`,
        token,
      );
      const items = (page && page.items) || [];
      found.push(...items);

      log(`Found ${found.length} conversations so far…`);

      if (items.length < PAGE_SIZE) break;
      offset += PAGE_SIZE;
      await sleep(PAUSE_MS);
    }

    return found;
  }

  function download(conversations) {
    const blob = new Blob([JSON.stringify(conversations)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "conversations.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  try {
    if (!location.hostname.endsWith("chatgpt.com")) {
      throw new Error("Run this on https://chatgpt.com, with a tab open there.");
    }

    log("Reading your session…");
    const token = await accessToken();

    log("Listing your conversations…");
    const summaries = await listConversations(token);

    if (summaries.length === 0) {
      log("No conversations found. Nothing to export.");
      return;
    }

    log(`Downloading ${summaries.length} conversations. This will take a while.`);

    const conversations = [];
    const failed = [];

    for (let index = 0; index < summaries.length; index += 1) {
      const id = summaries[index].id;
      try {
        const detail = await get(`/backend-api/conversation/${id}`, token);
        // The detail response carries title, create_time, update_time,
        // mapping and current_node — the same shape the official export uses.
        // conversation_id is added because the detail response omits it.
        conversations.push({ ...detail, conversation_id: id });
      } catch (error) {
        failed.push(id);
        console.warn(`[mind archive] Could not fetch one conversation:`, error);
      }

      if ((index + 1) % 25 === 0 || index + 1 === summaries.length) {
        log(`${index + 1} of ${summaries.length}…`);
      }
      await sleep(PAUSE_MS);
    }

    log(`Done. ${conversations.length} conversations exported.`);
    if (failed.length) {
      log(`${failed.length} could not be fetched and were left out.`);
    }

    download(conversations);
    log("Saved conversations.json — put it in your Mind Archive inbox folder.");
  } catch (error) {
    console.error("[mind archive] Export failed:", error);
    log(
      "Something went wrong. These endpoints are undocumented and may have " +
        "changed — use the official export instead: Settings → Data controls.",
    );
  }
})();
