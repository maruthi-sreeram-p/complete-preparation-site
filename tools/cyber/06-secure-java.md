@part cyber-secure-java | Secure coding in Java and Spring | appsec
## Security belongs in the whole lifecycle

Fixing a flaw in design costs a whiteboard conversation. Fixing it in production costs an incident. A **secure software development lifecycle (SSDLC)** moves security checks **left**, toward the beginning.

| Phase | Security activity | Example output |
|---|---|---|
| Requirements | decide what must be protected and which rules apply | "passwords must be hashed", "audit every admin action" |
| Design | threat model (STRIDE), pick safe patterns | data flow diagram, trust boundaries |
| Coding | secure coding standard, code review, IDE and pre-commit checks | review checklist, secret scanner |
| Build and test | SAST, dependency scan, security unit tests, DAST | scan reports as pipeline gates |
| Release and operate | hardening, secrets management, logging, patching | monitored, patched production |

A developer's three habits that prevent most bugs: **never trust input, keep data and code separate, and deny by default.**

## Validate input at the boundary

**Input validation** checks that data is the type, size, range and format you expect **before** your logic uses it. It is a defence in depth layer. It does not replace parameterised queries or output encoding.

- **Allow-list over block-list:** accept the characters and values you expect (`^[A-Za-z0-9_]{3,30}$`), not "everything except `<`".
- **Validate on the server.** Client-side checks are only for convenience.
- **Check type, length, range and format, and business rules** (quantity between 1 and 100, end date after start date).
- **Canonicalise first, then validate** (decode, normalise paths and Unicode), otherwise `%2e%2e/` slips past a check for `../`.
- **Limit sizes:** request bodies, upload sizes, page sizes, JSON depth, number of items. Unbounded input is a denial-of-service risk.
- **Use DTOs, not entities,** for request bodies so clients cannot set fields such as `role` or `id` (mass assignment).

```java Bean Validation on a DTO
public record RegisterRequest(
        @NotBlank @Pattern(regexp = "^[A-Za-z0-9_]{3,30}$") String username,
        @NotBlank @Email @Size(max = 254) String email,
        @NotBlank @Size(min = 12, max = 128) String password) {}

@PostMapping("/register")
ResponseEntity<Void> register(@Valid @RequestBody RegisterRequest request) { /* ... */ }
```

!warning Regex denial of service (ReDoS) :: A pattern such as `(a+)+$` can take exponential time on an input like `aaaaaaaaaaaaaaaaaaaaaaaa!`. One request can pin a CPU core. Keep patterns simple, avoid nested quantifiers, bound the input length first, and consider a library with linear-time matching.

!cheat Validation cheat codes ::
- **Allow-list, server-side, at every trust boundary.**
- **Reject, do not "fix".** Silently stripping bad characters invites bypasses (`....//`).
- **Canonicalise before checking.** Decode once, normalise paths, then validate.
- **Bound everything:** length, size, count, depth, rate.
- **Validation is not encoding.** Still parameterise queries and encode output.
!end

## Handle errors and output safely

- **Never return stack traces, SQL or internal paths to clients.** Return a generic message plus a correlation ID, and log the details privately.
- **Fail closed:** an exception in a permission check must end in "denied".
- Return the **right `Content-Type`** (`application/json`), and set `X-Content-Type-Options: nosniff`.

```java One central error handler
@RestControllerAdvice
class ApiErrors {
    private static final Logger log = LoggerFactory.getLogger(ApiErrors.class);

    @ExceptionHandler(AccessDeniedException.class)
    ProblemDetail denied(AccessDeniedException e) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.FORBIDDEN, "Not allowed");
    }

    @ExceptionHandler(Exception.class)
    ProblemDetail unexpected(Exception e) {
        String id = UUID.randomUUID().toString();
        log.error("Unhandled error {}", id, e);                       // details stay in the log
        return ProblemDetail.forStatusAndDetail(HttpStatus.INTERNAL_SERVER_ERROR, "Something went wrong. Reference " + id);
    }
}
```

## Secrets: passwords, keys and tokens

A **secret** is anything that grants access: database passwords, API keys, signing keys, tokens. The rules:

1. **Never commit secrets to Git.** Git history is forever, so deleting the file later does not help. If one leaks, **rotate it immediately** (issue a new one and revoke the old one), then clean up.
2. **Load secrets at runtime** from environment variables or a secret manager (AWS Secrets Manager, HashiCorp Vault, Kubernetes secrets with encryption), not from `application.properties` in the repository.
3. **Use different secrets per environment** and give each the minimum permissions.
4. **Rotate regularly** and support rotation without a redeploy where possible.
5. **Add scanning:** a pre-commit hook and a pipeline step with a tool such as gitleaks or trufflehog, and enable your Git host's secret scanning.

```yaml application.yml: placeholders only, values come from the environment
spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USER}
    password: ${DB_PASSWORD}
server:
  servlet:
    session:
      cookie:
        http-only: true
        secure: true
        same-site: lax
```

!tip After a leaked key :: Treat it as public the moment it was pushed, even if the repository is private and even if you deleted the commit. Rotate first, investigate access logs second, rewrite history third (history rewriting does not un-leak anything).

## Dependencies and the supply chain

A typical Spring Boot application is 80 to 90 percent other people's code. Your risk includes every library.

- **Software composition analysis (SCA):** OWASP Dependency-Check, GitHub Dependabot, Snyk, `mvn versions:display-dependency-updates`. They compare your dependency tree against CVE databases.
- **Keep an inventory (SBOM):** a bill of materials in CycloneDX or SPDX format lists every component, so when the next Log4Shell appears you can answer "are we affected?" in minutes.
- **Use the Spring Boot BOM** so versions are consistent, and update regularly. Small frequent upgrades are safer than one huge one.
- **Remove unused dependencies**, pin versions, use only trusted repositories, and verify checksums or signatures where the tooling supports it.
- **Watch for typosquatting** (a package with a name one letter off) and abandoned libraries.
- **Build integrity:** reproducible builds, signed artifacts and a locked-down CI system, because an attacker who controls the build controls what you ship.

## Java pitfalls that become vulnerabilities

| Pitfall | Why it matters | Safer approach |
|---|---|---|
| `java.util.Random` / `Math.random()` for tokens | predictable | `SecureRandom` |
| `String.equals` on secrets or MACs | timing leak | `MessageDigest.isEqual` (constant time) |
| `ObjectInputStream.readObject` on input | remote code execution gadgets | JSON with DTOs, allow-list filters |
| XML parsers with default settings | XXE | disable DTDs and external entities |
| `Runtime.exec("cmd " + input)` | command injection | `ProcessBuilder` with a fixed argument list, or no shell at all |
| `int total = qty * priceCents` | integer overflow wraps negative | `Math.multiplyExact`, `long`, `BigDecimal` for money |
| Jackson default typing enabled | deserialisation to attacker-chosen classes | do not enable it for untrusted input |
| Spring Expression Language built from input | expression injection | never evaluate user data as SpEL |
| Logging raw user input | log forging with `\r\n`, secrets in logs | sanitise newlines, never log passwords or tokens |
| Catching and swallowing exceptions | hides attacks and leaves half-finished state | log, and fail closed |
| Reflection and `setAccessible(true)` on untrusted names | bypasses access rules | allow-list of classes and methods |
| Time-of-check to time-of-use (TOCTOU) | the state changes between check and action | atomic operations, DB constraints, transactions |
| Public Actuator or H2 console in production | secrets and database access | disable or protect, expose only `health` |

**Spring4Shell (CVE-2022-22965)** is a good case study: data binding that could reach class loader properties on certain JDK and server combinations allowed remote code execution. The lessons: bind to DTOs, patch quickly, and know your dependencies.

!interview Money and integers :: "Why not use `double` for prices? Floating point cannot represent most decimals exactly, so totals drift. I store money as integer cents in a `long`, or use `BigDecimal` with explicit scale and rounding, and use `Math.addExact` and `multiplyExact` so an overflow throws instead of wrapping. I also take prices from the server, never from the request."

## Logging and monitoring in the application

- Log **security events**: logins (success and failure), logouts, password changes, MFA events, permission denials, input validation failures, admin actions, and changes to sensitive data. Include time, user id, source IP, action and outcome.
- **Never log** passwords, tokens, full card numbers, secrets or sensitive personal data. Mask what you must keep.
- **Neutralise log injection**: a username like `bob\nINFO admin logged in` can forge a line. Encode or strip CR and LF before logging, or use structured JSON logging.
- Send logs off the machine to a central store (an attacker who owns the host can erase local logs) and **alert** on patterns such as many failures, impossible travel or a new admin.

```java Structured, safe security logging
log.warn("event=login_failed user={} ip={} reason={}", clean(username), request.getRemoteAddr(), "bad_credentials");

static String clean(String s) { return s == null ? "" : s.replaceAll("[\\r\\n\\t]", "_"); }
```

## Static analysis, testing and review

| Tool type | What it does | Examples |
|---|---|---|
| **SAST** (static application security testing) | scans source or bytecode for dangerous patterns | SpotBugs with the FindSecBugs plugin, SonarQube, CodeQL, Semgrep |
| **SCA** | known vulnerable dependencies | OWASP Dependency-Check, Dependabot, Snyk |
| **Secret scanning** | keys committed to Git | gitleaks, trufflehog |
| **DAST** (dynamic) | attacks the running app from outside | OWASP ZAP, Burp Suite |
| **IAST / RASP** | instrumentation inside the running app | commercial agents |
| **Fuzzing** | random and malformed inputs | Jazzer for Java |

Scanners produce **false positives** (reports that are not real) and **false negatives** (misses). Always triage: reproduce, trace the code path, then fix or document why it is not exploitable.

### A review checklist you can paste into pull requests

1. Does any user input reach a query, command, file path, URL, template or log? How is it bound or validated?
2. Is every endpoint authenticated, and does it check **who owns the object**?
3. Are secrets absent from code, config and logs?
4. Are errors generic to the client and detailed only in logs?
5. Are new dependencies needed, maintained and free of known CVEs?
6. Does any new data need encryption, retention limits or masking?
7. Are there tests for the unhappy paths (anonymous, wrong user, bad input)?

### Find the bugs

```java Review this controller
@GetMapping("/files")
public byte[] get(@RequestParam String name) throws IOException {
    return Files.readAllBytes(Path.of("/data/uploads/" + name));         // (1)
}

@PostMapping("/users/{id}")
public User update(@PathVariable long id, @RequestBody User u) {        // (2)
    return repo.save(u);
}

@GetMapping("/search")
public List<Item> search(@RequestParam String q) {
    return jdbc.query("select * from items where title like '%" + q + "%'", mapper);   // (3)
}

log.info("Login attempt: " + username + " password=" + password);       // (4)
String token = Long.toHexString(new Random().nextLong());               // (5)
```

1. **Path traversal:** `name=../../etc/passwd`. Resolve, normalise and check `startsWith(base)`.
2. **Mass assignment and missing ownership check:** the body may contain `role` or another user's `id`. Use a DTO and verify `id` belongs to the caller.
3. **SQL injection:** use `like ?` with `"%" + q + "%"` as the bound parameter.
4. **Secret in the log:** never log the password.
5. **Predictable token:** use `SecureRandom` and at least 128 bits.

!keypoints Validate with allow-lists on the server and bound every size ;; Never return stack traces, and fail closed ;; Keep secrets out of Git and rotate any that leak ;; Scan dependencies and keep an SBOM ;; Use SecureRandom, constant-time comparison and exact arithmetic ;; Log security events, never secrets, and neutralise log injection

?? Why is a block list of dangerous characters a weak validation strategy?
=> Attackers find encodings and alternative syntax that the list missed. An allow-list defines exactly what is acceptable, so everything else is rejected.
?? You accidentally pushed an AWS access key to a private repository and removed it in the next commit. What do you do?
=> Treat it as compromised: deactivate and rotate the key at once, review access logs for misuse, then remove it from history and add secret scanning so it cannot happen again.
?? Why should money not be stored in a double?
=> Binary floating point cannot represent most decimal fractions exactly, so sums drift. Use integer minor units (cents) or BigDecimal.
?? Give two ways to find vulnerable dependencies in a Maven project.
=> OWASP Dependency-Check (or a pipeline SCA tool such as Snyk), and GitHub Dependabot alerts. An SBOM helps answer which services contain an affected library.
?? What is log injection and how do you prevent it?
=> Attacker-controlled text with line breaks creates fake log entries. Strip or encode CR and LF before writing, or use structured logging.
?? What is the difference between SAST and DAST?
=> SAST analyses source or bytecode without running the app. DAST attacks a running instance from the outside, as an attacker would.
