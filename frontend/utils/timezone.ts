const TIMEZONE_COOKIE_KEY = 'todo_timezone';
const TIME_FORMAT_COOKIE_KEY = 'todo_time_format'; // '12' or '24'

export const getUserTimezone = (): string => {
  if (typeof document !== 'undefined') {
    const match = document.cookie.match(new RegExp('(?:^|; )' + TIMEZONE_COOKIE_KEY + '=([^;]*)'));
    if (match && match[1]) {
      try {
        return decodeURIComponent(match[1]);
      } catch {
        // ignore
      }
    }
  }
  if (typeof Intl !== 'undefined' && Intl.DateTimeFormat) {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  }
  return 'UTC';
};

export const setUserTimezone = (tz: string) => {
  if (typeof document === 'undefined') return;
  const expires = new Date();
  expires.setFullYear(expires.getFullYear() + 1);
  document.cookie = `${TIMEZONE_COOKIE_KEY}=${encodeURIComponent(tz)}; path=/; expires=${expires.toUTCString()}`;
};

export type HourFormat = '12' | '24';

export const getUserHourFormat = (): HourFormat => {
  if (typeof document !== 'undefined') {
    const match = document.cookie.match(new RegExp('(?:^|; )' + TIME_FORMAT_COOKIE_KEY + '=([^;]*)'));
    if (match && match[1]) {
      const v = decodeURIComponent(match[1]);
      if (v === '12' || v === '24') return v;
    }
  }
  return '24';
};

export const setUserHourFormat = (format: HourFormat) => {
  if (typeof document === 'undefined') return;
  const expires = new Date();
  expires.setFullYear(expires.getFullYear() + 1);
  document.cookie = `${TIME_FORMAT_COOKIE_KEY}=${encodeURIComponent(format)}; path=/; expires=${expires.toUTCString()}`;
};

// Convert a local datetime-local input (YYYY-MM-DDTHH:MM) into UTC ISO string
export const localInputToUtcIso = (localInput: string | null | undefined): string | null => {
  if (!localInput) return null;
  const d = new Date(localInput);
  if (isNaN(d.getTime())) return null;
  return d.toISOString();
};

// Format an ISO string for display in the user timezone (using browser locale)
export const formatIsoForUser = (iso: string | null | undefined, withTime: boolean = true, timeOnly: boolean = false): string => {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '';
  const hourFormat = getUserHourFormat();

  let options: Intl.DateTimeFormatOptions;
  if (timeOnly) {
    options = {
      hour: '2-digit',
      minute: '2-digit',
      hour12: hourFormat === '12',
    };
  } else if (withTime) {
    options = {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: hourFormat === '12',
    };
  } else {
    options = { year: 'numeric', month: 'short', day: '2-digit' };
  }

  return d.toLocaleString(undefined, options);
};

const pad = (n: number) => String(n).padStart(2, '0');

const toLocalInputString = (d: Date): string => {
  const year = d.getFullYear();
  const month = pad(d.getMonth() + 1);
  const day = pad(d.getDate());
  const hour = pad(d.getHours());
  const minute = pad(d.getMinutes());
  return `${year}-${month}-${day}T${hour}:${minute}`;
};

export const getTodayEndLocalInput = (): string => {
  const now = new Date();
  now.setHours(23, 59, 0, 0);
  return toLocalInputString(now);
};

export const getTomorrowEndLocalInput = (): string => {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  d.setHours(23, 59, 0, 0);
  return toLocalInputString(d);
};

// weekday: 0 (Sunday) .. 6 (Saturday)
export const getNextWeekdayEndLocalInput = (weekday: number): string => {
  const d = new Date();
  const current = d.getDay();
  let diff = weekday - current;
  if (diff <= 0) diff += 7; // next occurrence
  d.setDate(d.getDate() + diff);
  d.setHours(23, 59, 0, 0);
  return toLocalInputString(d);
};
