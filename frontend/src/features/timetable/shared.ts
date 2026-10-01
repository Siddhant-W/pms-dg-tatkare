import { Weekday } from '../../types';

export const DAYS: { label: string; value: Weekday }[] = [
  { label: 'Mon', value: 'MONDAY' },
  { label: 'Tue', value: 'TUESDAY' },
  { label: 'Wed', value: 'WEDNESDAY' },
  { label: 'Thu', value: 'THURSDAY' },
  { label: 'Fri', value: 'FRIDAY' },
  { label: 'Sat', value: 'SATURDAY' },
];

export const DAY_NAMES: Record<Weekday, string> = {
  MONDAY: 'Monday', TUESDAY: 'Tuesday', WEDNESDAY: 'Wednesday', THURSDAY: 'Thursday', FRIDAY: 'Friday', SATURDAY: 'Saturday',
};

export const PERIODS = Array.from({ length: 9 }, (_, i) => i + 1);

/** "08:30:00" -> "08:30" for <input type="time"> and display. */
export const trimTime = (t: string | null | undefined) => (t ? t.slice(0, 5) : '');
