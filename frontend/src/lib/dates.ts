/** Date helpers. All ISO strings here are the user's *local* calendar date -
 *  `toISOString()` is UTC and would call it "yesterday" in the early morning. */

function pad(n: number) {
  return String(n).padStart(2, '0');
}

export function toISODate(d: Date): string {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export function todayISO(): string {
  return toISODate(new Date());
}

export function parseISODate(iso: string): Date {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d);
}

export function addDays(iso: string, days: number): string {
  const d = parseISODate(iso);
  d.setDate(d.getDate() + days);
  return toISODate(d);
}

export function formatLongDate(iso: string): string {
  return parseISODate(iso).toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
}

export function formatShortDate(iso: string): string {
  return parseISODate(iso).toLocaleDateString('en-US', { weekday: 'short', day: 'numeric', month: 'short' });
}

/** The API stamps times in UTC; SQLite returns them without a zone suffix, which the
 *  browser would otherwise read as local time. */
export function parseTimestamp(iso: string): Date {
  return new Date(/(Z|[+-]\d{2}:?\d{2})$/.test(iso) ? iso : `${iso}Z`);
}

export function formatTime(iso: string): string {
  return parseTimestamp(iso).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
}

export type Weekday = 'MONDAY' | 'TUESDAY' | 'WEDNESDAY' | 'THURSDAY' | 'FRIDAY' | 'SATURDAY';
const WEEKDAYS: (Weekday | null)[] = [null, 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];

/** The school weekday for a date, or null on Sunday. */
export function weekdayOf(iso: string): Weekday | null {
  return WEEKDAYS[parseISODate(iso).getDay()] ?? null;
}
