import { isAxiosError } from 'axios';

export interface ApiConflict {
  entry_id?: string;
  teacher_id?: string;
  teacher_name?: string | null;
  weekday?: string | null;
  period_number?: number;
  subject?: string | null;
  class_name?: string | null;
}

export interface ApiError {
  status?: number;
  /** Always safe to show to the user. */
  message: string;
  /** Machine-readable reason for 409/422 responses, e.g. `class_overlap`. */
  code?: string;
  /** Per-field messages from a 422, keyed by field name. */
  fieldErrors: Record<string, string>;
  conflicts: ApiConflict[];
  isNetworkError: boolean;
}

/**
 * Normalise every shape the API (and axios) can fail with: a plain string
 * `detail`, our `{code, message, errors, conflicts}` object, FastAPI's own
 * validation list, or no response at all.
 */
export function parseApiError(error: unknown, fallback = 'Something went wrong. Please try again.'): ApiError {
  const base: ApiError = { message: fallback, fieldErrors: {}, conflicts: [], isNetworkError: false };

  if (!isAxiosError(error)) {
    return error instanceof Error && error.message ? { ...base, message: error.message } : base;
  }
  if (!error.response) {
    return { ...base, message: "Can't reach the server. Check your connection and try again.", isNetworkError: true };
  }

  const { status, data } = error.response;
  const detail = (data as { detail?: unknown } | undefined)?.detail;
  const result: ApiError = { ...base, status };

  if (typeof detail === 'string') {
    result.message = detail;
  } else if (Array.isArray(detail)) {
    // FastAPI/pydantic: [{ loc: ['body', 'field'], msg }]
    for (const item of detail as { loc?: (string | number)[]; msg?: string }[]) {
      const field = item.loc?.[item.loc.length - 1];
      if (typeof field === 'string' && item.msg) result.fieldErrors[field] = item.msg;
    }
    result.message = 'Please check the highlighted fields.';
  } else if (detail && typeof detail === 'object') {
    const d = detail as { code?: string; message?: string; errors?: { field: string; message: string }[]; conflicts?: ApiConflict[] };
    result.code = d.code;
    result.message = d.message ?? fallback;
    for (const e of d.errors ?? []) result.fieldErrors[e.field] = e.message;
    result.conflicts = d.conflicts ?? [];
  } else if (status === 403) {
    result.message = "You don't have permission to do that.";
  } else if (status && status >= 500) {
    result.message = 'The server ran into a problem. Please try again in a moment.';
  }
  return result;
}
