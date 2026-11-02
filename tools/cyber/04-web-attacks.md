@part cyber-web-attacks | Web attacks and the OWASP Top 10 | appsec
## The browser security model you must know first

Most web attacks make sense once you know three browser rules.

- **Origin** = scheme + host + port. `https://shop.com` and `https://shop.com:8443` and `http://shop.com` are three different origins. The **same-origin policy (SOP)** stops a script from one origin reading responses from another.
- **Cookies are sent automatically** with every request to the site that set them, whichever page triggered the request. That convenience is what makes CSRF possible.
- **The browser runs whatever script the page contains**, with the page's full privileges. That is what makes XSS dangerous.

### Cookie attributes

| Attribute | Effect | Protects against |
|---|---|---|
| `HttpOnly` | JavaScript cannot read the cookie | theft of the session by XSS |
| `Secure` | sent only over HTTPS | sniffing on plain HTTP |
| `SameSite=Lax` / `Strict` | not sent on most cross-site requests | CSRF |
| `Path`, `Domain`, `Max-Age` | limit where and how long it lives | wide exposure, long-lived sessions |

```http A well-protected session cookie
Set-Cookie: SESSION=9f2c...e1; Path=/; Secure; HttpOnly; SameSite=Lax; Max-Age=1800
```

### CORS is not a security feature for your server

**CORS** (cross-origin resource sharing) is a way for a server to tell the browser "this other origin may read my responses". It relaxes SOP. It does not stop anyone from calling your API with `curl`. Typical mistakes: `Access-Control-Allow-Origin: *` on an API that returns private data, and echoing back whatever `Origin` arrives together with `Access-Control-Allow-Credentials: true`. Allow-list exact origins.

### Security headers worth knowing

| Header | Purpose |
|---|---|
| `Content-Security-Policy` | which scripts, styles and frames the page may load (the strongest XSS mitigation after output encoding) |
| `Strict-Transport-Security` | HTTPS only (HSTS) |
| `X-Content-Type-Options: nosniff` | the browser must trust the declared content type |
| `X-Frame-Options: DENY` or CSP `frame-ancestors 'none'` | no framing, which stops clickjacking |
| `Referrer-Policy` | how much of the URL is sent to other sites |
| `Permissions-Policy` | switch off camera, microphone, geolocation if unused |

## The OWASP Top 10 at a glance

**OWASP** (Open Worldwide Application Security Project) publishes the Top 10, a consensus list of the most serious web application risks. It is the vocabulary of AppSec interviews. The most widely used edition is **2021**:

| # | 2021 category | One-line meaning |
|---|---|---|
| A01 | **Broken Access Control** | users can do or see what they should not (IDOR, missing checks) |
| A02 | **Cryptographic Failures** | missing or weak protection of sensitive data in transit or at rest |
| A03 | **Injection** | untrusted input is run as part of a command or query (SQL, OS, LDAP, XSS) |
| A04 | **Insecure Design** | the flaw is in the design, not just the code |
| A05 | **Security Misconfiguration** | defaults, open cloud storage, verbose errors, missing headers |
| A06 | **Vulnerable and Outdated Components** | libraries with known CVEs |
| A07 | **Identification and Authentication Failures** | weak passwords, bad sessions, no brute-force protection |
| A08 | **Software and Data Integrity Failures** | unsigned updates, insecure deserialization, tampered pipelines |
| A09 | **Security Logging and Monitoring Failures** | attacks happen and nobody notices |
| A10 | **Server-Side Request Forgery (SSRF)** | the server is tricked into requesting internal or attacker-chosen URLs |

!note The 2025 edition :: A new edition was announced as a release candidate in November 2025. As reported, Broken Access Control stays first (and now includes SSRF), Security Misconfiguration moves up to second, and two categories are new: Software Supply Chain Failures and Mishandling of Exceptional Conditions. The ideas in this part are unchanged; only the grouping moved. Check owasp.org/Top10 for the final list and its numbering.

!cheat OWASP quick map ::
- **Input becomes code** → Injection (SQL, OS command, XSS). Fix: parameterise, encode output, validate.
- **Who may do this?** → Broken Access Control. Fix: check on the server for every request.
- **Who are you?** → Authentication failures. Fix: MFA, rate limits, safe sessions.
- **Is it secret?** → Cryptographic failures. Fix: TLS, strong algorithms, no secrets in code.
- **Server fetches a URL for me** → SSRF. Fix: allow-list destinations, block internal ranges.
- **Library has a CVE** → Vulnerable components. Fix: scan dependencies, upgrade.
- **Nobody saw it** → Logging failures. Fix: log security events and alert.
!end

## Injection

**Injection** happens when untrusted data is sent to an interpreter as part of a command or query, and the interpreter cannot tell where the data ends and the instructions begin.

### SQL injection

Vulnerable code builds the query by concatenation:

```java Vulnerable
String sql = "SELECT name, role FROM users WHERE name = '" + user + "' AND pass = '" + password + "'";
ResultSet rs = connection.createStatement().executeQuery(sql);
```

If `user` is `admin' --` the database sees

```sql What the database receives
SELECT name, role FROM users WHERE name = 'admin' --' AND pass = ''
```

`--` starts a comment, so the password check disappears and the attacker logs in as admin. With `' OR '1'='1` in both fields the condition is always true and every row matches.

| Type | How the attacker learns data |
|---|---|
| **In-band (error / UNION)** | results or errors appear in the page. `UNION SELECT` appends rows from other tables |
| **Blind (boolean)** | the page behaves differently for true and false conditions |
| **Blind (time)** | `SLEEP(5)` makes the response slow when a condition is true |
| **Out-of-band** | the database sends data over DNS or HTTP to the attacker |
| **Second-order** | a payload is stored safely, then used unsafely in a later query |

**The fix is parameterised queries (prepared statements)**: the SQL text and the data travel separately, so data can never become syntax.

```java Fixed
PreparedStatement ps = connection.prepareStatement("SELECT name, role FROM users WHERE name = ? AND pass_hash = ?");
ps.setString(1, user);
ps.setString(2, hash);
```

```java Spring Data JPA and JdbcTemplate
@Query("select u from User u where u.name = :name")            // named parameter: safe
Optional<User> findByName(@Param("name") String name);

jdbcTemplate.query("select * from notes where owner = ?", mapper, owner);   // placeholder: safe

// UNSAFE even in JPA: "select u from User u where u.name = '" + name + "'"
```

Things parameters cannot do: **table names, column names and `ORDER BY` direction cannot be bound as parameters.** Map user choices to a fixed **allow-list** (`"price" → "price_cents"`). Additional layers: a database user with only the rights the app needs, no verbose database errors in responses, a WAF.

### OS command injection

```java Vulnerable and safer
Runtime.getRuntime().exec("ping -c 1 " + host);      // host = "8.8.8.8; cat /etc/passwd" runs two commands
new ProcessBuilder("ping", "-c", "1", host).start(); // arguments are not parsed by a shell, and host is still validated
```

Best: do not call the shell at all (use a library), allow-list the input (`InetAddress` parsing, regex for hostnames) and run with a low-privilege account. Related interpreters with the same flaw: LDAP, XPath, NoSQL (`{"$ne": null}` in a Mongo login), expression languages and template engines (server-side template injection).

!cheat Injection cheat codes ::
- **Cause:** data and code mixed in one string. **Cure:** keep them apart (parameters).
- **Escaping by hand fails.** Use the framework's parameter binding.
- **Cannot bind a table, column or ORDER BY** → allow-list.
- **`' --`** ends a SQL statement early. **`; cmd`** or `| cmd` chains an OS command.
- Defence in depth: least-privilege DB account, generic error messages, input validation, WAF.
!end

## Cross-site scripting (XSS)

In **XSS**, the attacker gets their own script to run in the victim's browser **as part of your site**. It can read the page, make requests as the user, show a fake login form or steal tokens that are not `HttpOnly`.

| Type | Where the payload lives | Example |
|---|---|---|
| **Reflected** | in the request (URL or form) and echoed in the response | a search page printing `?q=<script>...` |
| **Stored (persistent)** | saved in the database and shown to other users | a comment, profile name or support ticket |
| **DOM-based** | the page's own JavaScript writes untrusted data into the DOM (`innerHTML`) | `element.innerHTML = location.hash` |

Stored XSS in an admin-facing screen (a support ticket the admin opens) is the worst case.

### Defence, in order of importance

1. **Encode output for its context.** The same text needs HTML-escaping in a body (`<` becomes `&lt;`), different escaping in an attribute, in JavaScript and in a URL. Template engines such as **Thymeleaf (`th:text`) and React (`{value}`) escape by default**. The danger is in the escape hatches: `th:utext`, `dangerouslySetInnerHTML`, `innerHTML`, `document.write`.
2. **Validate and sanitise input** on arrival. If you must allow HTML (a rich-text editor), pass it through a maintained sanitiser (OWASP Java HTML Sanitizer, DOMPurify) with an allow-list.
3. **Content Security Policy** blocks inline scripts and unknown sources, which turns many XSS bugs into harmless text: `Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none'`.
4. **`HttpOnly` cookies** so a script cannot read the session.

```text What escaping does
Input:    <script>alert(1)</script>
In HTML:  &lt;script&gt;alert(1)&lt;/script&gt;      shown as text, never executed
```

!warning alert(1) is only a proof :: A real XSS payload will not pop a dialog. It sends cookies, keystrokes or API calls to the attacker. The dialog is just the cheapest way to prove that script ran.

## Cross-site request forgery (CSRF) and clickjacking

**CSRF** tricks a logged-in user's browser into sending a state-changing request to your site, for example by loading an attacker's page that auto-submits `POST /transfer?to=attacker&amount=5000`. The browser attaches the session cookie, so the server thinks it is the user.

Defences:

- **SameSite cookies** (`Lax` or `Strict`). Most browsers now treat cookies as `Lax` by default.
- **Anti-CSRF tokens**: a random, per-session value in every state-changing form or header, which the attacker's page cannot read (SOP). Spring Security enables this by default for browser apps.
- **Never change state with GET.** Require POST, PUT, PATCH or DELETE.
- For sensitive actions, re-authenticate or confirm.
- APIs that use an `Authorization: Bearer` header (not cookies) are not CSRF-prone, because the browser does not add that header by itself.

**Clickjacking** loads your site in an invisible frame over a decoy button so the user clicks something they cannot see. Defence: `frame-ancestors 'none'` (CSP) or `X-Frame-Options: DENY`.

## Broken access control

This is the number one category because it is easy to get wrong: authentication was done, but **the check "may this user do this to this object?"** was missing, or was done only in the UI.

| Flaw | Example | Fix |
|---|---|---|
| **IDOR** (insecure direct object reference) / BOLA | `GET /api/invoices/1042` returns any user's invoice if you change the number | verify ownership on the server: `invoice.owner == currentUser` |
| **Missing function-level check** | a normal user calls `POST /admin/users/5/delete` | authorise every endpoint (`@PreAuthorize("hasRole('ADMIN')")`) |
| **Privilege escalation via mass assignment** | request JSON includes `"role":"ADMIN"` and the entity binds it | bind to a DTO with only the allowed fields |
| **Forced browsing** | `/admin`, `/backup.zip`, `/.git/` guessed in the URL | deny by default and do not deploy them |
| **Path traversal** | `?file=../../etc/passwd` | resolve, normalise and check the path stays under the base directory |
| **Hidden != protected** | an admin button is hidden in the UI but the API works | the server is the only authority |
| **Tampering with JWT/cookie claims** | changing `"role":"user"` in an unsigned or weakly verified token | verify signatures, take roles from the server |

```java Ownership check and a safe file path
Invoice invoice = repo.findById(id).orElseThrow(NotFound::new);
if (!invoice.getOwnerId().equals(currentUser.getId())) throw new AccessDeniedException("not yours");

Path base = Path.of("/srv/uploads").toRealPath();
Path file = base.resolve(requestedName).normalize();
if (!file.startsWith(base)) throw new SecurityException("path traversal");
```

!tip Return 404 or 403? :: For objects the user must not know about, a 404 reveals less than a 403. Either way, log the attempt: repeated denied attempts are a sign of someone probing for IDORs.

## Other classic web flaws

### Server-side request forgery (SSRF)

The application fetches a URL that the user supplies (an image importer, a webhook tester). The attacker supplies an **internal** address instead: `http://localhost:8080/admin` or the cloud metadata service `http://169.254.169.254/latest/meta-data/`, which can return temporary cloud credentials. Defences: allow-list destination hosts, resolve the name and **block private, loopback and link-local ranges** (re-check after redirects, because DNS can change), disable redirects, require **IMDSv2** on AWS, and give the instance role minimal permissions.

### Insecure deserialization and XXE

- **Java deserialization** (`ObjectInputStream.readObject`) of untrusted bytes can run attacker-chosen "gadget chains" and lead to remote code execution. Never deserialise untrusted native Java objects. Use JSON with explicit DTOs and a library with polymorphic typing turned off, or an allow-list filter.
- **XXE** (XML external entity): an XML parser that resolves entities can read local files or make requests. Disable DTDs and external entities in the parser factory (`disallow-doctype-decl`).

### File upload

Dangers: an executable uploaded to a web-served folder, a huge file, an HTML file served from your domain (stored XSS), a filename with `../`. Defences: allow-list extension **and** verify the content type, generate your own random filename, store outside the web root or in object storage, cap the size, scan for malware, serve with `Content-Disposition: attachment` and `nosniff`.

### Open redirect and others

- **Open redirect**: `/login?next=https://evil.com` sends users to a phishing site after login. Allow only relative paths or an allow-list of hosts.
- **Business logic flaws** are not in any scanner's signature list: negative quantities, applying a coupon twice, skipping a payment step, racing two requests to spend one balance twice. Threat model the flow and enforce rules on the server.
- **Security misconfiguration**: default credentials, directory listing, debug mode, `/actuator` endpoints exposed, verbose stack traces, S3 buckets open to the world.
- **Vulnerable components**: a library with a known CVE. The Log4Shell flaw (CVE-2021-44228) showed how one logging dependency could expose a huge part of the internet.

!interview How do you prevent SQL injection? :: "Parameterised queries or an ORM's bound parameters everywhere, never string concatenation. Allow-list anything that cannot be a parameter, such as column names. Run the application with a database account that has only the privileges it needs, return generic error messages, and add a WAF and static analysis as extra layers."

!keypoints SQL injection is fixed with parameterised queries, not with escaping ;; XSS is fixed by context-aware output encoding, backed by a CSP and HttpOnly cookies ;; CSRF is fixed with SameSite cookies and anti-CSRF tokens ;; Access control must be checked on the server for every request and object ;; SSRF turns your server into a proxy for the attacker, so allow-list destinations ;; The OWASP Top 10 is a map of categories, learn the idea behind each one

?? Why does `' OR '1'='1` bypass a login that concatenates strings?
=> It closes the original string literal and adds a condition that is always true, so the WHERE clause matches every row.
?? What is the difference between stored and reflected XSS?
=> Reflected XSS comes from the current request and appears in its own response. Stored XSS is saved by the application and runs for every user who views it, so it is usually worse.
?? Name two defences that reduce the damage of an XSS bug even when encoding is missed.
=> A Content Security Policy that blocks inline scripts, and HttpOnly cookies so the session cannot be read by script.
?? A report page uses `GET /api/orders/{id}`. A user changes the id and sees someone else's order. What is the flaw and the fix?
=> It is an IDOR (broken access control). The server must verify that the order belongs to the logged-in user (or that the user has a role that allows it).
?? Why can a CSRF attack not read the response?
=> The same-origin policy stops the attacker's page from reading cross-origin responses. CSRF only needs the request to be sent and to take effect.
?? A feature fetches a user-supplied image URL. How do you stop SSRF?
=> Allow-list hosts or schemes, resolve and block private and link-local ranges, disable redirects, use short timeouts, and limit the instance's cloud permissions.
