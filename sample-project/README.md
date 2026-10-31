# Notes — a full-stack sample

A small notes app built to put the JavaTrail guide's CRUD chapter into practice: **Spring Boot 4** API + **React 19 / TypeScript** frontend. Sign up, then create, search, page through, edit and delete your own notes.

It is deliberately small, but it covers what a real feature needs: authentication, ownership, validation, concurrent edits, pagination, error handling, tests and a container setup.

## Run it

**Development** (H2 file database, hot reload). Needs Java 21 and Node 22.

```bash
cd backend && ./mvnw spring-boot:run          # API on :8080
cd frontend && npm install && npm run dev     # app on http://localhost:5174
```

If something else already uses port 8080, run the API elsewhere and point the dev proxy at it:

```bash
cd backend && ./mvnw spring-boot:run -Dspring-boot.run.arguments=--server.port=8081
cd frontend && API_URL=http://localhost:8081 npm run dev
```

**Containers** (Postgres + Nginx, like production). Copy `.env.example` to `.env`, set the two secrets, then:

```bash
docker compose up --build        # http://localhost:8088
```

**Tests**

```bash
cd backend && ./mvnw test        # 18 tests: real HTTP through Spring Security, H2 in-memory
cd frontend && npm test          # 38 tests: whole app in jsdom, network mocked with MSW
```

## How it fits together

```
browser ──► Nginx (static files, /api proxy) ──► Spring Boot ──► Postgres
            same origin: no CORS, the cookie just works
```

| Concern | Decision | Why |
|---|---|---|
| Login | JWT in an **HttpOnly, SameSite=Strict** cookie | JavaScript (and so XSS) cannot read it; the browser sends it by itself |
| CSRF | token protection **off** | every request is same-site JSON and the cookie is `SameSite=Strict`; revisit if you ever allow cross-site calls |
| Passwords | BCrypt; login does a dummy hash for unknown emails | no timing or message difference reveals which emails exist |
| Other people's notes | **404**, not 403 | does not confirm that an id exists |
| Concurrent edits | JPA `@Version`, and the client **must** send the version it loaded → **409** | two tabs cannot silently overwrite each other |
| Search | `like` with `%`, `_` and `\` escaped | typing `100%` finds "100%", not everything |
| Lists | page size capped at 100, sort order fixed on the server | a client cannot ask for the whole table or an arbitrary sort |
| Errors | RFC 9457 `ProblemDetail`, with a `errors` map per field | the form puts each message next to its field |
| Schema | Flyway migrations, `ddl-auto: validate` | the schema is code-reviewed, Hibernate only checks it |
| Secrets | the app **refuses to start** with the dev JWT secret under the `postgres` profile | a forgotten env var cannot ship a known key |

Frontend: TanStack Query for server state (the search term and page live in the URL, so links and refresh work), React Hook Form + Zod for forms, React Router 7 with a lazily loaded editor, and a status-0 `ApiError` so "server unreachable" reads differently from "server said no".

## Things this project does not do

- **No rate limiting** on login or register. Put it in front (Nginx `limit_req`, an API gateway) or add Bucket4j before exposing this.
- **No refresh token or revocation.** A token is valid for 8 hours; logging out only clears the cookie.
- **No email verification or password reset.**
- **Full-text search is a `like` scan.** Fine for thousands of notes per user; use Postgres `tsvector` or a search engine beyond that.
- **Plain text only.** Rendering Markdown means choosing a sanitiser first.

## Ideas for next steps

1. Add `limit_req` to Nginx, and prove it with a test.
2. Tags on notes (a many-to-many with a join table, and a migration).
3. Replace the 409 "reload" button with a side-by-side diff of the two versions.
4. Add Playwright for one end-to-end flow against the compose stack.
5. Deploy it, with `COOKIE_SECURE=true` behind HTTPS.
