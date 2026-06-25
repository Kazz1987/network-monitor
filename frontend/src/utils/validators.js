const PRIVATE_IPV4_RANGES = [
  /^10\./,
  /^172\.(1[6-9]|2\d|3[0-1])\./,
  /^192\.168\./,
  /^127\./,
  /^169\.254\./,
];

const IPV4_RE = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
const HOSTNAME_RE = /^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$/;
// JS `\w` is ASCII-only even with the `u` flag (unlike Python's `re.UNICODE`),
// so Unicode property escapes are used to keep parity with the backend's name validator.
const NAME_RE = /^[\p{L}\p{N}_\s.\-]{1,100}$/u;
const SAFE_TARGET_RE = /^[A-Za-z0-9.:-]+$/;

export function isValidIPv4(value) {
  const match = IPV4_RE.exec(value);
  if (!match) return false;
  return match.slice(1).every((octet) => Number(octet) >= 0 && Number(octet) <= 255);
}

export function isPrivateIPv4(value) {
  return PRIVATE_IPV4_RANGES.some((pattern) => pattern.test(value));
}

export function isValidHostname(value) {
  return HOSTNAME_RE.test(value);
}

function parseIPv6Group(part) {
  if (!/^[0-9a-fA-F]{1,4}$/.test(part)) return NaN;
  return parseInt(part, 16);
}

/** Expands an IPv6 literal (with optional embedded IPv4 tail) into 8 16-bit groups, or null if invalid. */
export function parseIPv6(value) {
  let str = value.trim();

  const ipv4TailMatch = str.match(/(^|:)(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$/);
  if (ipv4TailMatch) {
    const ipv4 = ipv4TailMatch[2];
    if (!isValidIPv4(ipv4)) return null;
    const octets = ipv4.split(".").map(Number);
    const hi = ((octets[0] << 8) | octets[1]).toString(16);
    const lo = ((octets[2] << 8) | octets[3]).toString(16);
    str = str.slice(0, str.length - ipv4.length) + hi + ":" + lo;
  }

  if (!/^[0-9a-fA-F:]+$/.test(str)) return null;

  const doubleColonCount = (str.match(/::/g) || []).length;
  if (doubleColonCount > 1) return null;

  let groups;
  if (doubleColonCount === 1) {
    const [left, right] = str.split("::");
    const leftParts = left ? left.split(":") : [];
    const rightParts = right ? right.split(":") : [];
    const missing = 8 - leftParts.length - rightParts.length;
    if (missing < 0) return null;
    groups = [...leftParts, ...Array(missing).fill("0"), ...rightParts];
  } else {
    groups = str.split(":");
  }

  if (groups.length !== 8) return null;
  const parsed = groups.map(parseIPv6Group);
  if (parsed.some((g) => Number.isNaN(g))) return null;
  return parsed;
}

export function isValidIPv6(value) {
  return parseIPv6(value) !== null;
}

/** Mirrors the backend's ipaddress-based private/reserved checks for IPv6. */
export function isPrivateOrReservedIPv6(groups) {
  const isAllZero = (slice) => slice.every((g) => g === 0);

  if (isAllZero(groups)) return true; // :: (unspecified)
  if (isAllZero(groups.slice(0, 7)) && groups[7] === 1) return true; // ::1 (loopback)
  if ((groups[0] & 0xfe00) === 0xfc00) return true; // fc00::/7 (unique local)
  if (groups[0] >= 0xfe80 && groups[0] <= 0xfebf) return true; // fe80::/10 (link-local)
  if ((groups[0] & 0xff00) === 0xff00) return true; // ff00::/8 (multicast)

  // IPv4-mapped (::ffff:a.b.c.d) and IPv4-compatible (::a.b.c.d) - check the embedded address.
  const isIPv4Mapped = isAllZero(groups.slice(0, 4)) && groups[4] === 0 && groups[5] === 0xffff;
  const isIPv4Compatible = isAllZero(groups.slice(0, 5)) && groups[5] === 0;
  if (isIPv4Mapped || isIPv4Compatible) {
    const a = (groups[6] >> 8) & 0xff;
    const b = groups[6] & 0xff;
    const c = (groups[7] >> 8) & 0xff;
    const d = groups[7] & 0xff;
    const embedded = `${a}.${b}.${c}.${d}`;
    return isPrivateIPv4(embedded);
  }

  return false;
}

/** Validates a host target: rejects unsafe characters, private IPv4/IPv6 ranges, and malformed hostnames/IPs. */
export function validateTarget(value) {
  const trimmed = (value ?? "").trim();
  if (!trimmed) {
    return { valid: false, message: "ターゲットを入力してください" };
  }
  if (!SAFE_TARGET_RE.test(trimmed)) {
    return { valid: false, message: "使用できない文字が含まれています" };
  }

  if (trimmed.includes(":")) {
    const groups = parseIPv6(trimmed);
    if (groups === null) {
      return { valid: false, message: "IPv6アドレスの形式が不正です" };
    }
    if (isPrivateOrReservedIPv6(groups)) {
      return { valid: false, message: "プライベート/予約済みIPアドレスは登録できません" };
    }
    return { valid: true, value: trimmed };
  }

  if (isValidIPv4(trimmed)) {
    if (isPrivateIPv4(trimmed)) {
      return { valid: false, message: "プライベートIPアドレスは登録できません" };
    }
    return { valid: true, value: trimmed };
  }
  if (isValidHostname(trimmed)) {
    return { valid: true, value: trimmed };
  }
  return { valid: false, message: "IPアドレスまたはホスト名の形式が不正です" };
}

export function validateName(value) {
  const trimmed = (value ?? "").trim();
  if (!trimmed) {
    return { valid: false, message: "名前を入力してください" };
  }
  if (!NAME_RE.test(trimmed)) {
    return { valid: false, message: "名前に使用できない文字が含まれています" };
  }
  return { valid: true, value: trimmed };
}

/** Escapes HTML-significant characters to prevent XSS when rendering user-supplied text. */
export function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export function validateInterval(value, min = 10, max = 3600) {
  const num = Number(value);
  if (!Number.isInteger(num) || num < min || num > max) {
    return { valid: false, message: `${min}〜${max}秒の範囲で入力してください` };
  }
  return { valid: true, value: num };
}
