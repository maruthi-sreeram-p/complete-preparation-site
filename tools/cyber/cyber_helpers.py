"""Names available inside the `!py` checks of tools/cyber/mcq/*.txt (see build_cyber.py and build_gate.py).

Small reference implementations, so a question about a hash length, a JWT, a CIDR block, a CVSS score or an SQL injection is
checked by running it and not by trusting the answer key.
"""
import base64
import binascii
import fnmatch
import collections
import hashlib
import hmac
import ipaddress
import itertools
import json
import math
import re
import sqlite3
import string
import struct
import urllib.parse
from math import ceil, floor, gcd, log2  # noqa: F401


def num(text):
    """The number in an option such as '1,024', '3/4', '2.5 s' or '40%' (the first token)."""
    token = str(text).split()[0].replace(",", "").replace("−", "-").rstrip("%")
    return float(token) if "." in token else int(token)


def close(a, b, tol=1e-4):
    return abs(float(a) - float(b)) < tol


# ---------------------------------------------------------------- hashing and encoding
def digest(name, data):
    """Hex digest of text or bytes with any hashlib algorithm: digest('sha256', 'abc')."""
    return hashlib.new(name, data.encode() if isinstance(data, str) else data).hexdigest()


def digest_bits(name):
    return hashlib.new(name).digest_size * 8


def hmac_hex(key, message, name="sha256"):
    return hmac.new(key.encode(), message.encode(), name).hexdigest()


def pbkdf2_hex(password, salt, iterations, name="sha256"):
    return hashlib.pbkdf2_hmac(name, password.encode(), salt.encode(), iterations).hex()


def b64e(text):
    return base64.b64encode(text.encode()).decode()


def b64d(text):
    return base64.b64decode(text + "=" * (-len(text) % 4)).decode()


def b64url_d(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4)).decode()


def b64url_e(data):
    raw = data if isinstance(data, bytes) else data.encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def hex_of(text):
    return text.encode().hex()


def url_encode(text, safe=""):
    return urllib.parse.quote(text, safe=safe)


def url_decode(text):
    return urllib.parse.unquote(text)


def html_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#x27;")


def crc32_hex(text):
    return format(binascii.crc32(text.encode()) & 0xFFFFFFFF, "08x")


# ---------------------------------------------------------------- classical and toy ciphers
def caesar(text, shift):
    out = []
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            out.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            out.append(ch)
    return "".join(out)


def xor_hex(a_hex, b_hex):
    return bytes(x ^ y for x, y in zip(bytes.fromhex(a_hex), bytes.fromhex(b_hex))).hex()


def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x, y = egcd(b, a % b)
    return g, y, x - (a // b) * y


def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("no inverse")
    return x % m


def rsa_toy(p, q, e):
    """-> (n, phi, d) for a textbook RSA key."""
    n, phi = p * q, (p - 1) * (q - 1)
    return n, phi, modinv(e, phi)


def dh_shared(p, g, a, b):
    """Diffie-Hellman: both sides must arrive at the same secret; -> (A, B, secret)."""
    big_a, big_b = pow(g, a, p), pow(g, b, p)
    assert pow(big_b, a, p) == pow(big_a, b, p)
    return big_a, big_b, pow(big_b, a, p)


# ---------------------------------------------------------------- passwords and one-time codes
def entropy_bits(alphabet_size, length):
    """Bits of entropy of a random secret: length * log2(alphabet)."""
    return length * log2(alphabet_size)


def crack_seconds(alphabet_size, length, guesses_per_second):
    """Time to try every candidate; on average half of that."""
    return alphabet_size ** length / guesses_per_second


def hotp(secret, counter, digits=6):
    mac = hmac.new(secret.encode(), struct.pack(">Q", counter), "sha1").digest()
    offset = mac[-1] & 0x0F
    code = (struct.unpack(">I", mac[offset:offset + 4])[0] & 0x7FFFFFFF) % 10 ** digits
    return str(code).zfill(digits)


def totp(secret, unix_time, step=30, digits=6):
    return hotp(secret, int(unix_time) // step, digits)


# ---------------------------------------------------------------- JWT
def jwt_make(header, payload, key, alg="HS256"):
    """A signed HS256 token; header and payload are dicts."""
    part = lambda d: b64url_e(json.dumps(d, separators=(",", ":")))  # noqa: E731
    signing_input = f"{part(header)}.{part(payload)}"
    sig = hmac.new(key.encode(), signing_input.encode(), "sha256").digest()
    return f"{signing_input}.{b64url_e(sig)}"


def jwt_parts(token):
    """-> (header dict, payload dict, signature string) without verifying anything."""
    h, p, s = token.split(".")
    return json.loads(b64url_d(h)), json.loads(b64url_d(p)), s


def jwt_valid(token, key):
    h, p, s = token.split(".")
    expected = b64url_e(hmac.new(key.encode(), f"{h}.{p}".encode(), "sha256").digest())
    return hmac.compare_digest(expected, s)


# ---------------------------------------------------------------- networks
def cidr(block):
    return ipaddress.ip_network(block, strict=False)


def usable_hosts(block):
    n = cidr(block)
    return max(n.num_addresses - 2, 0) if n.prefixlen < 31 else n.num_addresses


def in_net(ip, block):
    return ipaddress.ip_address(ip) in cidr(block)


def is_private(ip):
    return ipaddress.ip_address(ip).is_private


# ---------------------------------------------------------------- SQL injection lab (SQLite)
def users_db():
    con = sqlite3.connect(":memory:")
    con.executescript("""
        create table users(id integer primary key, name text, pass text, role text);
        insert into users values (1, 'alice', 'pw1', 'user'), (2, 'bob', 'pw2', 'user'), (3, 'admin', 's3cret', 'admin');
        create table notes(id integer primary key, owner text, body text);
        insert into notes values (1, 'alice', 'a1'), (2, 'bob', 'b1'), (3, 'bob', 'b2');
    """)
    return con


def sql_rows(sql, params=()):
    """Run `sql` against the users/notes lab database -> list of rows."""
    return users_db().execute(sql, params).fetchall()


def vulnerable_login(user, password):
    """What `"... WHERE name='" + user + "' AND pass='" + password + "'"` returns: the matching rows."""
    return sql_rows(f"select name, role from users where name = '{user}' and pass = '{password}'")


def safe_login(user, password):
    return sql_rows("select name, role from users where name = ? and pass = ?", (user, password))


# ---------------------------------------------------------------- CVSS v3.1 base score
_AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
_AC = {"L": 0.77, "H": 0.44}
_UI = {"N": 0.85, "R": 0.62}
_CIA = {"H": 0.56, "L": 0.22, "N": 0.0}


def _roundup(x):
    i = round(x * 100000)
    return i / 100000.0 if i % 10000 == 0 else (floor(i / 10000) + 1) / 10.0


def cvss31(vector):
    """Base score of e.g. 'AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H' (9.8)."""
    m = dict(p.split(":") for p in vector.replace("CVSS:3.1/", "").split("/"))
    changed = m["S"] == "C"
    pr = {"N": 0.85, "L": 0.68 if changed else 0.62, "H": 0.5 if changed else 0.27}[m["PR"]]
    iss = 1 - (1 - _CIA[m["C"]]) * (1 - _CIA[m["I"]]) * (1 - _CIA[m["A"]])
    impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15 if changed else 6.42 * iss
    exploit = 8.22 * _AV[m["AV"]] * _AC[m["AC"]] * pr * _UI[m["UI"]]
    if impact <= 0:
        return 0.0
    return _roundup(min((impact + exploit) * (1.08 if changed else 1), 10))


def cvss_rating(score):
    return "None" if score == 0 else "Low" if score < 4 else "Medium" if score < 7 else "High" if score < 9 else "Critical"


# ---------------------------------------------------------------- logs and text
def count_matches(text, pattern):
    return len(re.findall(pattern, text))


def top_ip(log):
    """The most frequent IPv4 address in a log text."""
    return collections.Counter(re.findall(r"\d{1,3}(?:\.\d{1,3}){3}", log)).most_common(1)[0][0]


def chmod_octal(symbolic):
    """'rwxr-x---' -> '750'."""
    bits = [1 if c != "-" else 0 for c in symbolic]
    return "".join(str(bits[i] * 4 + bits[i + 1] * 2 + bits[i + 2]) for i in range(0, 9, 3))


def chmod_symbolic(octal):
    return "".join("".join(c if int(d) & b else "-" for b, c in ((4, "r"), (2, "w"), (1, "x"))) for d in octal)


def umask_mode(umask, base=0o666):
    """Permissions of a new file (base 666) or directory (base 777) under a umask, as an octal string."""
    return format(base & ~int(umask, 8), "03o")


def combos(n, k):
    return math.comb(n, k)


def permutations_count(n, k):
    return math.perm(n, k)


# ---------------------------------------------------------------- cloud policy evaluation
def iam_allowed(statements, action, resource):
    """AWS-style evaluation of policy statements: an explicit Deny wins, then any Allow, otherwise implicit deny."""
    allowed = False
    for st in statements:
        actions = st["Action"] if isinstance(st["Action"], list) else [st["Action"]]
        resources = st["Resource"] if isinstance(st["Resource"], list) else [st["Resource"]]
        if any(fnmatch.fnmatchcase(action, a) for a in actions) and any(fnmatch.fnmatchcase(resource, r) for r in resources):
            if st["Effect"] == "Deny":
                return False
            allowed = True
    return allowed


def sg_allows(rules, port, source_ip):
    """Security group: allow-only rules [(from_port, to_port, cidr), ...]; anything not matched is denied."""
    return any(lo <= port <= hi and in_net(source_ip, block) for lo, hi, block in rules)


def nacl_decision(rules, port):
    """Network ACL: rules [(number, from_port, to_port, 'allow'|'deny'), ...] are checked in number order, first match wins; default deny."""
    for _number, lo, hi, verdict in sorted(rules):
        if lo <= port <= hi:
            return verdict
    return "deny"
