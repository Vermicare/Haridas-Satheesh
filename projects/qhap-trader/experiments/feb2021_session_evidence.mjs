#!/usr/bin/env node
// QHAP-TRADER: calendar-evidence inventory only. NOT a trading-session authorization.
// Sources: NSE circular NSE/CMTR/46623 dated 2020-12-11
// https://archives.nseindia.com/content/circulars/CMTR46623.pdf
// SEBI statement dated 2021-02-25 documenting NSE 2021-02-24 technical halt
// https://www.sebi.gov.in/media/press-releases/feb-2021/trading-halt-at-nse-on-february-24-2021_49287.html
// Neither source authenticates third-party minute bars, individual weekday sessions,
// corporate actions, entitlements, or historical intraday execution.
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

export const provenance = Object.freeze({
  calendar: { issuer: 'NSE', circular: 'NSE/CMTR/46623', published: '2020-12-11',
    url: 'https://archives.nseindia.com/content/circulars/CMTR46623.pdf',
    scope: 'Scheduled capital-market holidays only; no scheduled February 2021 weekday holiday' },
  exception: { issuer: 'SEBI', published: '2021-02-25', date: '2021-02-24',
    url: 'https://www.sebi.gov.in/media/press-releases/feb-2021/trading-halt-at-nse-on-february-24-2021_49287.html',
    scope: 'Exceptional technical interruption; not a verified continuous session' }
});

export function classifyFeb2021Date(date) {
  if (typeof date !== 'string' || !/^2021-02-(0[1-9]|1[0-9]|2[0-8])$/.test(date)) {
    return { date, status: 'UNKNOWN', replayAllowed: false, reason: 'OUT_OF_SCOPE_OR_INVALID' };
  }
  const weekday = new Date(date + 'T00:00:00Z').getUTCDay();
  if (weekday === 0 || weekday === 6) {
    return { date, status: 'CLOSED_WEEKEND', replayAllowed: false, reason: 'WEEKEND' };
  }
  if (date === '2021-02-24') {
    return { date, status: 'EXCEPTIONAL_HALT', replayAllowed: false, reason: 'SEBI_DOCUMENTED_INTERRUPTION' };
  }
  return { date, status: 'PROVISIONAL_WEEKDAY', replayAllowed: false,
    reason: 'SCHEDULE_ONLY_NOT_AUTHENTICATED_SESSION' };
}

export const feb2021 = Object.freeze(Array.from({ length: 28 }, (_, i) =>
  classifyFeb2021Date('2021-02-' + String(i + 1).padStart(2, '0'))));

export function assertManifest() {
  assert.equal(feb2021.length, 28);
  assert.equal(new Set(feb2021.map(x => x.date)).size, 28);
  const counts = Object.fromEntries(['CLOSED_WEEKEND', 'EXCEPTIONAL_HALT', 'PROVISIONAL_WEEKDAY']
    .map(status => [status, feb2021.filter(x => x.status === status).length]));
  assert.deepEqual(counts, { CLOSED_WEEKEND: 8, EXCEPTIONAL_HALT: 1, PROVISIONAL_WEEKDAY: 19 });
  assert.equal(feb2021.every(x => x.replayAllowed === false), true);
  assert.equal(classifyFeb2021Date('2021-02-29').status, 'UNKNOWN');
  assert.equal(classifyFeb2021Date('2021-03-01').replayAllowed, false);
  assert.equal(classifyFeb2021Date('2021-02-24').status, 'EXCEPTIONAL_HALT');
  assert.equal(classifyFeb2021Date('2021-02-23').status, 'PROVISIONAL_WEEKDAY');
  return { count: 28, counts, authorizedSessions: 0 };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const result = assertManifest();
  console.log(JSON.stringify({ provenance, verification: result, dates: feb2021 }, null, 2));
}
