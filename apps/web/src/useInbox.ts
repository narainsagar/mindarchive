import { useCallback, useEffect, useState } from "react";

import { fetchInbox } from "./api";
import type { InboxStatus } from "./api";

export interface Inbox {
  status: InboxStatus | null;
  refresh: () => Promise<void>;
}

/**
 * The watched inbox folder, and how many files are waiting in it.
 *
 * This lives outside `ImportPanel` because two places need the same answer:
 * the panel itself, and the Import button in the archive header, which shows
 * the waiting count while the panel is closed. Fetching it once here keeps
 * those two from disagreeing — and from asking the backend twice.
 */
export function useInbox(): Inbox {
  const [status, setStatus] = useState<InboxStatus | null>(null);

  const refresh = useCallback(async () => {
    try {
      setStatus(await fetchInbox());
    } catch {
      // The inbox is a convenience. If it cannot be read, everything still
      // works — say nothing rather than showing an error about a folder.
      setStatus(null);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  // Coming back to the tab is the moment a download is likely to have
  // finished, so it is the natural time to look in the inbox again.
  useEffect(() => {
    function onFocus() {
      void refresh();
    }
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, [refresh]);

  return { status, refresh };
}
