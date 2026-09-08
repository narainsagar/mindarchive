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

async function request<T>(path: string): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${BASE_URL}${path}`);
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

export function fetchHealth(): Promise<Health> {
  return request<Health>("/api/health");
}

export function fetchConfig(): Promise<PublicConfig> {
  return request<PublicConfig>("/api/config");
}
