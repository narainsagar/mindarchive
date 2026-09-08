/**
 * Talking to the Mind Archive backend.
 *
 * The backend runs on your own computer. There is no authentication, because
 * there is nobody else to authenticate against.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface Health {
  status: string;
  version: string;
  message: string;
}

export interface PublicConfig {
  version: string;
  storage_mode: string;
  cloud_enabled: boolean;
  archive_location: string;
  database_location: string;
  privacy_note: string;
}

/** The backend was reachable but unhappy, or could not be reached at all. */
export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${BASE_URL}${path}`, init);
  } catch {
    // Almost always means the backend is not running. Say that, rather than
    // showing the browser's own wording.
    throw new ApiError(
      "Could not reach Mind Archive. Is the backend running?",
    );
  }

  if (!response.ok) {
    throw new ApiError(
      `Mind Archive returned an error (${response.status}).`,
      response.status,
    );
  }

  return (await response.json()) as T;
}

export interface ImporterInfo {
  name: string;
  display_name: string;
  supported_formats: string[];
}

export interface ImportSummary {
  ok: boolean;
  message: string;
  source: string | null;
  imported: number;
  skipped: number;
  /** Descriptions of what could not be read. Never conversation content. */
  problems: string[];
  archive_location: string | null;
}

export function fetchHealth(): Promise<Health> {
  return request<Health>("/api/health");
}

export function fetchConfig(): Promise<PublicConfig> {
  return request<PublicConfig>("/api/config");
}

export function fetchImporters(): Promise<ImporterInfo[]> {
  return request<ImporterInfo[]>("/api/importers");
}

export interface ConversationSummary {
  path: string;
  title: string;
  source: string;
  created_at: string | null;
  updated_at: string | null;
  message_count: number;
  /**
   * Matching text with the match wrapped in `<<` and `>>`.
   *
   * Delimited rather than HTML, so nothing from a conversation is ever
   * rendered as markup.
   */
  snippet: string | null;
}

export interface ConversationList {
  conversations: ConversationSummary[];
  total: number;
  limit: number;
  offset: number;
  sources: Record<string, number>;
}

export interface ConversationDetail extends ConversationSummary {
  /** Markdown, exactly as stored on disk minus the front matter. */
  body: string;
  source_id: string | null;
}

export interface RebuildResult {
  ok: boolean;
  message: string;
  indexed: number;
}

export function fetchConversations(
  options: { query?: string; limit?: number; offset?: number } = {},
): Promise<ConversationList> {
  const params = new URLSearchParams();
  if (options.query) params.set("q", options.query);
  if (options.limit !== undefined) params.set("limit", String(options.limit));
  if (options.offset !== undefined) params.set("offset", String(options.offset));

  const query = params.toString();
  return request<ConversationList>(
    `/api/conversations${query ? `?${query}` : ""}`,
  );
}

export function fetchConversation(path: string): Promise<ConversationDetail> {
  // Each segment is encoded separately: the slashes are real path structure,
  // but anything inside a segment is a title and could contain any character.
  const encoded = path.split("/").map(encodeURIComponent).join("/");
  return request<ConversationDetail>(`/api/conversations/${encoded}`);
}

export function rebuildIndex(): Promise<RebuildResult> {
  return request<RebuildResult>("/api/index/rebuild", { method: "POST" });
}

/**
 * Upload an export and archive it.
 *
 * The file never leaves this computer — it goes to the Mind Archive backend
 * running locally, which reads it and writes conversations to your own disk.
 */
export async function importExport(file: File): Promise<ImportSummary> {
  const body = new FormData();
  body.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}/api/import`, { method: "POST", body });
  } catch {
    throw new ApiError("Could not reach Mind Archive. Is the backend running?");
  }

  if (response.status === 413) {
    throw new ApiError("That file is too large to import (the limit is 1 GB).");
  }

  if (!response.ok) {
    // The backend explains its own failures; fall back only if it did not.
    let detail = `Mind Archive returned an error (${response.status}).`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // Response was not JSON. Keep the generic message.
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as ImportSummary;
}
