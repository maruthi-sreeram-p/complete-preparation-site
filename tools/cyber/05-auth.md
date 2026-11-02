@part cyber-auth | Authentication, sessions and access control | appsec
## Authentication: proving who you are

Three classic factor types:

| Factor | Meaning | Examples | Weakness |
|---|---|---|---|
| **Knowledge** | something you know | password, PIN | guessed, phished, reused, leaked |
| **Possession** | something you have | phone, hardware key, smart card | stolen or lost |
| **Inherence** | something you are | fingerprint, face | cannot be changed if copied, false matches |

**Multi-factor authentication (MFA)** needs two or more *different* factors. A password plus a security question is **not** MFA, because both are knowledge.

| MFA method | Strength | Notes |
|---|---|---|
| SMS code | weak | SIM-swap and interception; better than nothing |
| **TOTP** app (Google Authenticator, Authy) | good | 6-digit code from a shared secret and the clock, changes every 30 seconds |
| Push approval | medium | vulnerable to **MFA fatigue** (the attacker spams requests until the user taps Approve). Use number matching |
| **FIDO2 / WebAuthn / passkeys** | strongest | public-key credential bound to the real website's origin, so a phishing site cannot use it |

**TOTP in one line:** `code = HOTP(secret, floor(time / 30))`, where HOTP is an HMAC-SHA-1 of the counter reduced to 6 digits. The RFC test secret `12345678901234567890` with counter 0 gives `755224`.

!cheat Authentication cheat codes ::
- **MFA means different factor types.** Password + OTP yes; password + security question no.
- **Phishing-resistant:** WebAuthn / passkeys. TOTP codes can be phished in real time; WebAuthn cannot.
- **Account recovery is part of authentication.** If "forgot password" only needs an e-mail link, the mailbox is the real password.
- **Do not reveal which part was wrong.** One generic message: "Invalid username or password".
- **Never store the password** you can read. Store a slow salted hash (Argon2id, bcrypt).
!end

### Attacks on login and the defences

| Attack | Defence |
|---|---|
| **Brute force** one account | throttle (increasing delay), temporary lock, CAPTCHA after repeated failures |
| **Credential stuffing** (leaked pairs from other sites) | MFA, breached-password check, per-IP and per-device rate limits, bot detection |
| **Password spraying** (one password, many accounts) | alert on many accounts failing from one source, ban common passwords |
| **Account enumeration** (error messages or timing differ for known and unknown users) | identical messages and response times for all outcomes, also on sign-up and reset |
| **Phishing** | WebAuthn, awareness, domain-bound credentials |
| **Session theft** (XSS, malware) | HttpOnly and Secure cookies, short lifetimes, re-authentication for sensitive actions |

**Permanent account lockout can itself be abused** to lock real users out (a denial of service). Prefer delays and temporary locks with alerts.

### A safe password reset

1. Ask for the e-mail address and always answer "if the account exists, we sent a link".
2. Send a **random, single-use token** (at least 128 bits), stored hashed, **expiring** within minutes.
3. On use, require a new password, invalidate the token and **all existing sessions**, and notify the user.
4. Do not use security questions (answers are often guessable or public) and never put the token in a place that is logged or sent to third parties (watch the `Referer` header).

## Sessions: staying logged in

HTTP is stateless, so after login the server gives the browser a **session ID** (or a token) that proves each later request belongs to the same login.

A secure session ID is:

- **random and long** (at least 128 bits from a secure generator), never a counter, timestamp or hash of the username,
- sent in a cookie with `HttpOnly; Secure; SameSite`,
- **regenerated at login**, which stops **session fixation** (the attacker plants a known ID before login and then uses it after the victim logs in),
- **expired** after idle time and a maximum lifetime, and **destroyed on the server at logout** (just deleting the cookie in the browser is not logout),
- tied to nothing secret in the URL: session IDs in URLs leak through logs, `Referer` and sharing.

Server-side sessions (an ID that points to data in memory or Redis) are easy to revoke. Stateless tokens (JWT) are easy to scale but hard to revoke.

## JSON Web Tokens (JWT)

A JWT has three Base64URL parts separated by dots: `header.payload.signature`.

```text A decoded token
header   {"alg":"HS256","typ":"JWT"}
payload  {"sub":"alice","role":"user","exp":1893456000}
signature = HMAC_SHA256(base64url(header) + "." + base64url(payload), secret)
```

- **The payload is only encoded, not encrypted.** Anyone who has the token can read it. Never put passwords, personal data or secrets in it.
- **The signature protects integrity.** If the payload changes, the signature no longer matches, as long as the server actually verifies it.
- **HS256** uses one shared secret. **RS256 / ES256** use a private key to sign and a public key to verify, so many services can verify without being able to issue tokens.
- Standard claims: `iss` (issuer), `sub` (subject), `aud` (audience), `exp` (expiry), `nbf` (not before), `iat` (issued at), `jti` (id).

### Classic JWT mistakes

| Mistake | What goes wrong | Fix |
|---|---|---|
| Trusting `alg: none` | the attacker removes the signature and sets `alg` to `none`; a weak library accepts it | the server fixes the accepted algorithm and rejects `none` |
| **Algorithm confusion** | the attacker signs with HS256 using the RSA **public** key as the secret; a server that lets the token choose its algorithm verifies it | pin the algorithm, use separate key types |
| Weak HMAC secret | `secret` or a dictionary word is cracked offline in seconds | at least 256 random bits |
| Not checking `exp`, `aud`, `iss` | stolen or foreign tokens work forever or on other services | validate all registered claims |
| Storing in `localStorage` | any XSS reads it | an `HttpOnly` cookie, or keep tokens in memory with short lifetimes |
| Long-lived access tokens | no revocation, so a stolen token stays valid | access tokens of 5 to 15 minutes plus **refresh tokens** that are rotated and revocable |
| Trusting the payload for authorisation without checking the user still exists | deleted or demoted users keep access until expiry | short expiry, or check a server-side status for sensitive actions |

!tip Decode, never trust :: Pasting a token into a debugger shows you the payload, but that proves nothing. Only a successful signature verification with the expected key, algorithm, issuer and audience means the token is genuine.

## OAuth 2.0, OpenID Connect and SSO

**OAuth 2.0** is a framework for **delegated authorisation**: a user lets an application access their data at another service without giving that application their password.

| Role | Example |
|---|---|
| **Resource owner** | the user |
| **Client** | the app that wants access (your web app) |
| **Authorization server** | issues tokens (Google, Okta, Keycloak) |
| **Resource server** | the API that holds the data |

**Authorization Code flow with PKCE** is the recommended flow for web, mobile and single-page apps:

1. The client sends the user to the authorisation server with `client_id`, `redirect_uri`, `scope`, a random **`state`** and a **PKCE code challenge** (the hash of a secret `code_verifier`).
2. The user logs in and consents. The server redirects back with a short-lived **authorization code** and the same `state`.
3. The client checks `state` (this blocks CSRF on the callback), then exchanges the code plus the `code_verifier` for an **access token** (and a refresh token).
4. The client calls the API with `Authorization: Bearer <access token>`.

Security rules: register **exact** redirect URIs (no wildcards, or codes leak to an attacker's URL), always use `state`, always use PKCE for public clients, and do not use the old **implicit flow** (tokens in the URL fragment). The **client credentials** flow is for machine-to-machine calls with no user.

**OpenID Connect (OIDC)** is a layer on OAuth 2.0 that adds **authentication**: an **ID token** (a JWT) says who the user is. Rule of thumb: *OAuth answers "what may this app do?" and OIDC answers "who logged in?"*. Never use a plain OAuth access token as proof of identity.

**SAML** is an older XML-based SSO standard still common in enterprises. **SSO** means one login for many applications, so MFA at the identity provider protects all of them, and so does a compromise of it.

## Authorisation: deciding what you may do

| Model | Idea | Example |
|---|---|---|
| **ACL** | a list on each object saying who may do what | file permissions |
| **RBAC** | permissions belong to roles, users get roles | `ROLE_ADMIN`, `ROLE_SUPPORT` |
| **ABAC** | rules over attributes of user, object and context | "doctors may read records of patients in their own hospital during working hours" |
| **ReBAC** | permissions follow relationships | "editors of the folder can edit its documents" |

- **Vertical escalation:** a normal user acts as an admin. **Horizontal escalation:** a user accesses another user's data (IDOR).
- **Deny by default.** Every endpoint is forbidden until a rule allows it.
- Enforce authorisation in **one central place** (filters, method annotations, a policy service) so that new endpoints cannot forget it.
- **401 Unauthorized** means "not authenticated"; **403 Forbidden** means "authenticated but not allowed".
- Re-check authorisation on **every** request and for **every** object, including in batch endpoints, exports, search results and background jobs.

## Spring Security in practice

Spring Security is a chain of servlet filters in front of your controllers. You declare rules in a `SecurityFilterChain` bean. **Rules are evaluated in order and the first matching one wins**, so put specific rules first and `anyRequest()` last.

```java A stateless REST API that accepts JWTs from an identity provider
@Configuration
@EnableMethodSecurity
class SecurityConfig {

    @Bean
    SecurityFilterChain api(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(a -> a
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated())                       // deny by default
            .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(csrf -> csrf.disable());   // acceptable ONLY because no cookies authenticate these calls
        return http.build();
    }

    @Bean
    PasswordEncoder passwordEncoder() {
        return PasswordEncoderFactories.createDelegatingPasswordEncoder();   // bcrypt by default, upgradable
    }
}

@Service
class InvoiceService {
    @PreAuthorize("hasRole('ADMIN') or #ownerId == authentication.name")
    public List<Invoice> invoicesOf(String ownerId) { /* ... */ }
}
```

- Keep **CSRF protection on** for any app where the browser authenticates by cookie or session (the default). Turn it off only for stateless token APIs.
- Configure **CORS** with exact origins; do not enable all origins together with credentials.
- Use `hasRole("ADMIN")` (Spring adds the `ROLE_` prefix) or `hasAuthority("ROLE_ADMIN")`. Mixing the two is a common bug.
- Add the **security headers** (Spring Security sets several by default).
- Test it: write tests that call endpoints as anonymous, as a normal user and as an admin, and assert 401, 403 and 200.

!interview Session versus JWT :: "Server sessions are simple and easy to revoke, but need shared storage when you scale out. JWTs are stateless and good for service-to-service calls, but cannot be revoked before expiry unless you add a deny list. For a browser app I would use a server session or a short-lived token in an HttpOnly cookie, plus CSRF protection. For APIs consumed by many services I would use short-lived signed JWTs from an identity provider and verify issuer, audience, expiry and algorithm."

!keypoints MFA needs different factor types and WebAuthn is phishing-resistant ;; Use generic error messages and throttling to stop enumeration and brute force ;; Regenerate the session ID at login and destroy it on the server at logout ;; A JWT payload is readable by everyone, so only a verified signature makes it trustworthy ;; Use the authorization code flow with PKCE, exact redirect URIs and a state value ;; Deny by default and check authorisation on every request

?? Why is a password plus a security question not MFA?
=> Both are knowledge factors. MFA needs factors of different types, for example knowledge plus possession.
?? What is session fixation and how is it prevented?
=> The attacker gives the victim a known session ID before login and reuses it afterwards. The server prevents it by issuing a new session ID when the user authenticates.
?? Why is `alg: none` dangerous in a JWT library?
=> A token with no signature is accepted as valid if the library lets the token decide the algorithm. The server must pin the allowed algorithms.
?? What does PKCE protect against?
=> An attacker who steals the authorization code cannot exchange it, because the exchange also needs the secret code verifier that only the real client holds.
?? What is the difference between OAuth 2.0 and OpenID Connect?
=> OAuth 2.0 delegates access to resources (authorisation). OpenID Connect adds an ID token that tells the application who the user is (authentication).
?? Why can disabling CSRF protection be correct for a JWT API but wrong for a form-based site?
=> CSRF relies on the browser sending credentials automatically. Cookie sessions are sent automatically, whereas a bearer token must be added explicitly by code, which a forged page cannot do.
