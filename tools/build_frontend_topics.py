"""
Writes the pages of the frontend stage (HTML/CSS, JavaScript, TypeScript, React, testing).

These pages are NOT extracted from the user's PDFs: no PDF covers them. Java_FullStack_12Week_Plan.xlsx lists
"Rendering, hooks, performance, state management, TypeScript" for week 10, so the content was written for this
site. Every page says so at the top. Replace a page by extracting a PDF into the same topic id.

Usage: python -I tools/build_frontend_topics.py
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "content" / "roadmaps" / "interview-prep" / "topics"
SOURCE = {"document": "Written for this site (not from your PDFs)"}
NOTICE = {"type": "callout", "variant": "note", "title": "Not from your PDFs",
          "text": "Your PDFs do not cover this topic, so this page was written for the site. Your 12-week plan lists "
                  "React, hooks, rendering, performance, state management and TypeScript. Check it against the "
                  "official documentation, or give me a PDF to replace it."}


def code(language, text, title=None, walkthrough=None):
    block = {"type": "code", "language": language, "code": text.strip("\n")}
    if title:
        block["title"] = title
    if walkthrough:
        block["walkthrough"] = walkthrough
    return block


def note(variant, title, text):
    return {"type": "callout", "variant": variant, "title": title, "text": text}


def interview(text):
    return note("interview", "Interview angle", text)


def keypoints(*points):
    return note("keypoints", "Key points", "\n".join(f"- {p}" for p in points))


def table(headers, rows, caption=None):
    block = {"type": "table", "headers": headers, "rows": rows}
    if caption:
        block["caption"] = caption
    return block


def diagram(title, source, caption=None, components=None):
    block = {"type": "diagram", "format": "mermaid", "title": title, "code": source.strip("\n")}
    if caption:
        block["caption"] = caption
    if components:
        block["components"] = components
    return block


def practice(*pairs):
    return {"id": "practice", "type": "practice", "title": "Practice questions",
            "blocks": [{"type": "questions", "items": [{"question": q, "answer": a} for q, a in pairs]}]}


def section(sid, kind, title, *blocks):
    return {"id": sid, "type": kind, "title": title, "blocks": list(blocks)}


TOPICS = {}

# ------------------------------------------------------------------ HTML and CSS
TOPICS["frontend-html-css"] = [
    section("intro", "introduction", "Why a backend developer needs this", NOTICE,
            "A React component ends up as HTML and CSS in the browser. You do not need to be a designer, but you need "
            "to read and write semantic markup, build forms that work, and lay out a page with Flexbox and Grid."),
    section("html", "concept", "Semantic HTML and forms",
            "Choose elements for their meaning, not their looks. `button` is focusable and keyboard-operable for free; "
            "a clickable `div` is neither. Screen readers and search engines rely on `header`, `nav`, `main`, "
            "`section`, `article` and heading levels.",
            code("html", """
<form action="/api/login" method="post">
  <label for="email">Email</label>
  <input id="email" name="email" type="email" required autocomplete="username" />

  <label for="password">Password</label>
  <input id="password" name="password" type="password" required minlength="8" />

  <button type="submit">Sign in</button>
</form>
""", "A form that works before any JavaScript"),
            "`label for` links the label to the input, which also makes the label clickable. Browser validation "
            "(`required`, `type=\"email\"`) is a convenience for the user only: **the server must validate again**, "
            "because anyone can send a request without your form."),
    section("box", "concept", "The box model",
            "Every element is a box: content, then padding, then border, then margin. By default `width` sets the "
            "content only, so padding makes the box wider than you asked for. Almost every project starts with "
            "`box-sizing: border-box`, which makes `width` include padding and border.",
            code("css", """
*, *::before, *::after { box-sizing: border-box; }

.card {
  width: 320px;       /* the whole box, padding and border included */
  padding: 16px;
  border: 1px solid #ccc;
  margin-bottom: 24px;
}
""")),
    section("layout", "concept", "Flexbox and Grid",
            table(["", "Flexbox", "Grid"], [
                ["Dimension", "One: a row or a column", "Two: rows and columns together"],
                ["Size comes from", "The content, then distributed", "The layout you define"],
                ["Use for", "Toolbars, nav bars, centring, lists of chips", "Page layouts, card galleries, dashboards"],
            ]),
            code("css", """
/* toolbar: push the last item to the far right */
.toolbar { display: flex; align-items: center; gap: 8px; }
.toolbar .spacer { margin-left: auto; }

/* gallery: as many 240px+ columns as fit, no media queries needed */
.gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }

/* page: fixed sidebar, flexible content, single column on phones */
.page { display: grid; grid-template-columns: 240px 1fr; }
@media (max-width: 768px) { .page { grid-template-columns: 1fr; } }
""")),
    section("notes", "notes", "Important notes",
            note("warning", "Gotcha", "A selector's specificity decides which rule wins, not just its order. "
                 "`#id` beats `.class` beats `element`. Reaching for `!important` usually means a specificity problem."),
            keypoints("Use semantic elements: `button` for actions, `a` for navigation, `label` for every input.",
                      "Browser validation helps the user; only the server's validation protects you.",
                      "Set `box-sizing: border-box` globally.",
                      "Flexbox for one direction, Grid for two.")),
    practice(("Why is a `button` better than a clickable `div`?",
              "It is focusable, works with Enter and Space, and is announced as a button by screen readers, all without extra code."),
             ("What does `box-sizing: border-box` change?",
              "`width` and `height` include padding and border, so adding padding does not make the box bigger."),
             ("You need a responsive card gallery. Flexbox or Grid?",
              "Grid, with `repeat(auto-fill, minmax(240px, 1fr))`: it is a two-dimensional layout and needs no media queries.")),
]

# ------------------------------------------------------------------ JavaScript
TOPICS["frontend-javascript"] = [
    section("intro", "introduction", "JavaScript through Java eyes", NOTICE,
            "JavaScript looks like Java and behaves differently. These differences cause most of the bugs Java "
            "developers write in it.",
            table(["Topic", "Java", "JavaScript"], [
                ["Types", "Static, checked at compile time", "Dynamic, checked at run time"],
                ["Objects", "Instances of classes", "Key-value bags linked by prototypes; `class` is syntax on top"],
                ["Threads", "Many threads, shared memory", "One thread per page, an event loop"],
                ["Functions", "Methods, lambdas for functional interfaces", "First-class values, closures everywhere"],
                ["Equality", "`==` identity, `equals()` value", "`===` strict, `==` coerces types (avoid it)"],
                ["Missing value", "`null`", "`undefined` and `null`"],
            ])),
    section("basics", "concept", "Modern syntax you will read every day",
            code("javascript", """
const user = { id: 7, name: 'Asha', role: 'admin' };   // const: the binding cannot change
let count = 0;                                         // let: block scoped. Never use var.

// destructuring and renaming
const { name, role: userRole } = user;

// spread creates a NEW object or array: this is how React state is updated
const renamed = { ...user, name: 'Ravi' };
const more = [...[1, 2], 3];

// arrow functions and array methods, like Java streams but eager
const admins = users.filter((u) => u.role === 'admin').map((u) => u.name);
const total = items.reduce((sum, i) => sum + i.price, 0);

// optional chaining and nullish coalescing
const city = user.address?.city ?? 'Unknown';   // ?? only falls back on null or undefined

// template literals
const url = `/api/users/${user.id}`;
"""),
            note("warning", "Gotcha", "`||` falls back on any falsy value, including `0` and `''`. "
                 "`count || 10` gives 10 when count is 0; `count ?? 10` gives 0. Falsy values are `false`, `0`, `''`, "
                 "`null`, `undefined` and `NaN`.")),
    section("closures", "concept", "Closures and this",
            "A **closure** is a function that keeps access to the variables of the scope that created it, even after "
            "that scope has returned. React hooks depend on this completely.",
            code("javascript", """
function counter() {
  let n = 0;                 // lives on as long as the returned function does
  return () => ++n;
}
const next = counter();
next(); // 1
next(); // 2
""", "A closure", [
                {"lines": "2", "title": "Local variable", "text": "`n` belongs to this call of `counter`."},
                {"lines": "3", "title": "Captured", "text": "The returned arrow function captures `n`, so it survives after `counter` returns."},
                {"lines": "6-7", "title": "State without a class", "text": "Each call updates the same captured `n`."},
            ]),
            "`this` is decided by **how a function is called**, not where it is defined. Arrow functions have no "
            "`this` of their own and use the enclosing one, which is why callbacks use them."),
    section("async", "architecture", "The event loop, promises and async/await",
            "The page has one thread. Slow work (network, timers) happens outside it and queues a callback for later. "
            "If your code blocks that thread, the page freezes: no clicks, no scrolling.",
            diagram("The event loop", """
flowchart LR
  A[Call stack<br/>runs your code] -->|fetch, setTimeout| B[Browser APIs<br/>do the slow work]
  B -->|promise settled| C[Microtask queue<br/>promise callbacks]
  B -->|timer fired, click| D[Task queue<br/>timers and events]
  C -->|runs first, all of them| A
  D -->|one, when the stack is empty| A
""", "When the stack is empty, all microtasks run, then one task, then the browser may repaint."),
            code("javascript", """
console.log('1');
setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => console.log('3'));
console.log('4');
// prints 1 4 3 2: microtasks run before the next task, even with a 0 ms timer
""", "The classic ordering question"),
            code("javascript", """
async function loadUser(id) {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);   // fetch does NOT reject on 404 or 500
  return res.json();
}

// run in parallel, like CompletableFuture.allOf; fails if any one fails
const [user, orders] = await Promise.all([loadUser(7), loadOrders(7)]);
""", "async and await"),
            note("warning", "Gotcha", "`fetch` only rejects on network failure. A 404 or 500 resolves normally, so always check `res.ok`.")),
    section("notes", "notes", "Important notes",
            interview("**Explain the event loop.** JavaScript runs on one thread with a call stack. Async operations run in the browser and queue callbacks. "
                      "When the stack empties, the loop runs all microtasks (promise callbacks), then one task (timer, event), and the browser can repaint. "
                      "This is why long synchronous work freezes the page."),
            keypoints("Use `const` by default, `let` when needed, never `var`.", "Use `===`, never `==`.",
                      "Closures keep access to their creating scope; hooks rely on them.",
                      "Microtasks run before the next task.", "`fetch` resolves on HTTP errors: check `res.ok`.")),
    practice(("What does `[] == false` give, and what should you do about it?",
              "`true`, through type coercion. Always use `===`, which never coerces."),
             ("What is the output order of `setTimeout(f, 0)` and `Promise.resolve().then(g)`?",
              "`g` then `f`: promise callbacks are microtasks, which run before the next task."),
             ("Why does `count || 10` misbehave when count is 0?",
              "`||` treats 0 as falsy and returns 10. Use `??`, which only falls back on null or undefined."),
             ("How do you run two requests in parallel and wait for both?",
              "`await Promise.all([a(), b()])`. It rejects as soon as either rejects; use `Promise.allSettled` to get every outcome.")),
]

# ------------------------------------------------------------------ TypeScript
TOPICS["frontend-typescript"] = [
    section("intro", "introduction", "What TypeScript is", NOTICE,
            "TypeScript is JavaScript plus a compile-time type checker. The types are erased: nothing about them exists "
            "at run time, much like Java generics. **A value from your API is whatever the server sent**, whatever "
            "type you wrote for it."),
    section("structural", "concept", "Structural typing: the big difference from Java",
            "Java is nominal: a class matches an interface only if it says `implements`. TypeScript is structural: "
            "anything with the right shape matches.",
            code("typescript", """
interface User { id: number; name: string; }

function greet(user: User) { return `Hello ${user.name}`; }

const person = { id: 1, name: 'Asha', age: 30 };
greet(person);   // fine: person has the shape of User, no "implements" needed
""")),
    section("types", "concept", "The types you use daily",
            code("typescript", """
// union and literal types: better than enums for most cases
type Status = 'idle' | 'loading' | 'success' | 'error';

// optional and readonly
interface Book {
  readonly id: number;
  title: string;
  subtitle?: string;        // string | undefined
}

// generics, like Java
function first<T>(items: T[]): T | undefined { return items[0]; }

// utility types derive new types from existing ones
type BookDraft = Omit<Book, 'id'>;        // for a create request
type BookPatch = Partial<BookDraft>;      // for a PATCH request
type BooksById = Record<number, Book>;
""")),
    section("narrowing", "concept", "Narrowing and discriminated unions",
            "The compiler follows your checks. A **discriminated union** makes impossible states impossible to write, "
            "and it is the most useful pattern in React code.",
            code("typescript", """
type Result<T> =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ok'; data: T };

function render(r: Result<Book[]>) {
  switch (r.status) {
    case 'loading': return 'Loading';
    case 'error':   return r.message;          // message exists only here
    case 'ok':      return r.data.length;      // data exists only here
  }
}
""", "One type instead of three flags")),
    section("notes", "notes", "Important notes",
            note("warning", "Gotcha", "`any` switches the checker off and spreads silently. Use `unknown` for values you have not checked: "
                 "the compiler then forces you to narrow before use. `response.json()` returns `any`, so annotating it does not validate it. "
                 "Use a schema library such as Zod where bad data would hurt."),
            interview("**How is TypeScript's type system different from Java's?** It is structural rather than nominal, types are fully erased at run time so there is no `instanceof` for interfaces, "
                      "and it has unions, literal types and flow-based narrowing, which let you model states precisely."),
            keypoints("Types are erased: they do not validate API responses.", "Structural typing: shape matters, not name.",
                      "Prefer unions of string literals and discriminated unions.", "Prefer `unknown` to `any`.",
                      "`Omit`, `Pick`, `Partial` and `Record` derive request types from one model.")),
    practice(("Why can't you use `instanceof` with a TypeScript interface?",
              "Interfaces are erased at compile time, so nothing exists at run time to check against."),
             ("What is the difference between `any` and `unknown`?",
              "`any` disables checking. `unknown` accepts anything but must be narrowed before use, so it stays safe."),
             ("Why prefer a discriminated union over `isLoading`, `error` and `data` fields?",
              "Three independent fields allow nonsense combinations such as loading with an error. A union allows only the real states, and the compiler checks each case.")),
]

# ------------------------------------------------------------------ React fundamentals
TOPICS["frontend-react-fundamentals"] = [
    section("intro", "introduction", "The idea", NOTICE,
            "React's core idea fits in one line: **UI = f(state)**. You describe what the screen should look like for "
            "the current state, and React works out the DOM changes. You never tell it \"add this row\"."),
    section("components", "concept", "Components, JSX and props",
            "A component is a function that returns JSX. JSX compiles to function calls, so it is JavaScript, not a "
            "template language: `{}` holds any expression. Props are the function's read-only arguments.",
            code("tsx", """
interface Book { id: number; title: string; available: boolean; }

function BookRow({ book, onBorrow }: { book: Book; onBorrow: (id: number) => void }) {
  return (
    <li>
      {book.title}
      {book.available
        ? <button onClick={() => onBorrow(book.id)}>Borrow</button>
        : <span>On loan</span>}
    </li>
  );
}

function BookList({ books, onBorrow }: { books: Book[]; onBorrow: (id: number) => void }) {
  if (books.length === 0) return <p>No books yet.</p>;
  return (
    <ul>
      {books.map((b) => <BookRow key={b.id} book={b} onBorrow={onBorrow} />)}
    </ul>
  );
}
""", "Props down, events up", [
                {"lines": "3", "title": "Props", "text": "A component receives data and callbacks as read-only props."},
                {"lines": "7-9", "title": "Conditional rendering", "text": "JSX holds expressions, so a ternary picks what to show."},
                {"lines": "8", "title": "Events go up", "text": "The child does not change the data. It calls the callback, and the owner of the state decides."},
                {"lines": "19", "title": "Lists need keys", "text": "`key` tells React which row is which between renders. Use a stable id."},
            ]),
            diagram("One-way data flow", """
flowchart TD
  P[Parent owns the state] -->|props: data and callbacks| C[Child renders them]
  C -->|calls the callback on a click| P
  P -->|state changes, parent re-renders| P
""", "Data flows down through props; events flow up through callbacks.")),
    section("state", "concept", "State and re-rendering",
            "State is memory that survives between renders. Calling the setter schedules a new render, and React calls "
            "your function again with the new value.",
            code("tsx", """
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount((c) => c + 1)}>Clicked {count} times</button>;
}
"""),
            "State is treated as immutable: create a new object or array. React compares by reference, so mutating in "
            "place and setting the same reference causes no re-render.",
            code("tsx", """
// wrong: same array reference, React sees no change
items.push(newItem);
setItems(items);

// right: a new array
setItems([...items, newItem]);
setItems(items.filter((i) => i.id !== id));
setItems(items.map((i) => (i.id === id ? { ...i, done: true } : i)));
""")),
    section("notes", "notes", "Important notes",
            note("warning", "Gotcha", "Do not use the array index as `key` when a list can be reordered or filtered. React will reuse the wrong component instance, "
                 "and state such as input text ends up on the wrong row."),
            interview("**What is the virtual DOM?** React keeps a lightweight description of the UI. On each render it compares the new tree with the old one (reconciliation) and applies only the differences to the real DOM. "
                      "The benefit is mainly the programming model, describing the result instead of the steps, not raw speed."),
            keypoints("UI is a function of state.", "Props are read-only; events go up through callbacks.",
                      "Never mutate state: create new objects and arrays.", "List keys must be stable ids, not indexes.")),
    practice(("Why doesn't `items.push(x); setItems(items)` re-render?",
              "It is the same array reference, and React skips the update when the value is identical. Create a new array."),
             ("Why is an array index a bad `key`?",
              "When items are inserted, removed or reordered, the index maps to a different item, so React reuses the wrong instance and its state."),
             ("Where should state live if two sibling components need it?",
              "In their closest common parent, passed down as props. This is called lifting state up.")),
]

# ------------------------------------------------------------------ Hooks
TOPICS["frontend-react-hooks"] = [
    section("intro", "introduction", "What hooks are", NOTICE,
            "Hooks are functions that let a component keep state and run side effects. React identifies each hook by "
            "**its call order**, so there are two rules: call them only at the top level of a component or custom hook, "
            "and never inside conditions or loops."),
    section("hooks", "concept", "The hooks you need",
            table(["Hook", "Purpose", "Causes a re-render?"], [
                ["`useState`", "A value that survives renders", "Yes, when set to a different value"],
                ["`useEffect`", "Sync with something outside React: network, timers, subscriptions", "Only if it sets state"],
                ["`useRef`", "A mutable box, or a reference to a DOM node", "No"],
                ["`useMemo`", "Cache a calculated value between renders", "No"],
                ["`useCallback`", "Cache a function between renders", "No"],
                ["`useContext`", "Read a value from a provider above", "Yes, when the value changes"],
                ["`useReducer`", "State with several related transitions", "Yes, on dispatch"],
            ])),
    section("effect", "concept", "useEffect properly",
            diagram("Effect lifecycle", """
flowchart TD
  A[Component renders] --> B[React updates the DOM]
  B --> C[Browser paints]
  C --> D{Did a dependency change?}
  D -->|first render or yes| E[Run cleanup of the previous effect]
  E --> F[Run the effect]
  D -->|no| G[Skip]
  H[Component removed] --> I[Run cleanup]
""", "Effects run after paint. Cleanup runs before the next run and on removal."),
            code("tsx", """
function UserProfile({ id }: { id: number }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`/api/users/${id}`, { signal: controller.signal })
      .then((res) => res.json())
      .then(setUser)
      .catch((e) => { if (e.name !== 'AbortError') console.error(e); });
    return () => controller.abort();
  }, [id]);

  return user ? <h1>{user.name}</h1> : <p>Loading</p>;
}
""", "Fetching with cleanup", [
                {"lines": "5-6", "title": "Cancellable request", "text": "The controller lets the cleanup cancel this request."},
                {"lines": "10", "title": "Cleanup", "text": "If `id` changes quickly, the old request is cancelled, so a slow old response cannot overwrite the new one. This bug is called a race condition."},
                {"lines": "11", "title": "Dependencies", "text": "The effect reruns when `id` changes. List everything from the component that the effect uses."},
            ]),
            note("warning", "You might not need an effect", "Do not use an effect to compute a value from props or state: calculate it during render. "
                 "`const fullName = first + ' ' + last` needs no state and no effect. Effects are for synchronising with things outside React."),
            note("note", "Strict Mode", "In development, `StrictMode` runs each effect, its cleanup and the effect again on mount, to expose missing cleanups. Two requests in development are expected, not a bug.")),
    section("closure", "concept", "The stale closure",
            "Each render has its own props and state values. A function created during a render closes over that "
            "render's values forever.",
            code("tsx", """
function Timer() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setCount(count + 1);        // bug: count is always 0 here, so it sticks at 1
    }, 1000);
    return () => clearInterval(id);
  }, []);

  // fix: the updater form always receives the latest value
  // setCount((c) => c + 1);

  return <p>{count}</p>;
}
""")),
    section("custom", "code", "Custom hooks",
            "A custom hook is a function starting with `use` that calls other hooks. It shares logic, not state: each "
            "component that calls it gets its own copy.",
            code("tsx", """
function useFetch<T>(url: string) {
  const [state, setState] = useState<Result<T>>({ status: 'loading' });

  useEffect(() => {
    const controller = new AbortController();
    setState({ status: 'loading' });
    fetch(url, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => setState({ status: 'ok', data }))
      .catch((e) => {
        if (e.name !== 'AbortError') setState({ status: 'error', message: e.message });
      });
    return () => controller.abort();
  }, [url]);

  return state;
}
""", "useFetch.ts")),
    section("notes", "notes", "Important notes",
            interview("**Why can't hooks be called conditionally?** React stores hook state in a list per component and matches it by call position. A conditional call shifts the positions, so hooks read each other's state."),
            keypoints("Call hooks at the top level only.", "Effects synchronise with the outside world; do not use them to derive values.",
                      "Always return a cleanup for subscriptions, timers and requests.", "List every dependency the effect uses.",
                      "Use the updater form `setX((x) => ...)` when the new value depends on the old one.")),
    practice(("Why does a request fire twice in development?",
              "StrictMode mounts, cleans up and remounts in development to reveal missing cleanups. It does not happen in production."),
             ("What is the difference between `useRef` and `useState`?",
              "Changing a ref does not re-render and takes effect immediately. Setting state schedules a re-render."),
             ("What is a stale closure, and how do you fix one?",
              "A function keeps the values from the render that created it. Fix it by listing the dependency or using the updater form of the setter."),
             ("How does a custom hook differ from a shared service in Spring?",
              "A Spring singleton shares one instance and its state. A custom hook shares only the logic: each component gets separate state.")),
]

# ------------------------------------------------------------------ State management
TOPICS["frontend-react-state"] = [
    section("intro", "introduction", "Kinds of state", NOTICE,
            "Most state-management pain comes from treating all state alike. Sort it first, and the tool usually "
            "chooses itself.",
            table(["Kind", "Example", "Where it belongs"], [
                ["Local UI", "Is this dropdown open, input text", "`useState` in the component"],
                ["Shared UI", "Selected filter used by two siblings", "Lift to the common parent"],
                ["App-wide, rarely changes", "Theme, current user, locale", "Context"],
                ["Server data", "Books list from your API", "A data library such as TanStack Query"],
                ["URL", "Page number, search term, selected tab", "The router's URL"],
                ["Complex client state", "A multi-step editor, a cart", "`useReducer` or a store such as Redux Toolkit or Zustand"],
            ])),
    section("decide", "visual", "Choosing a tool",
            diagram("Where should this state live?", """
flowchart TD
  A{Does it come from the server?} -->|yes| B[TanStack Query]
  A -->|no| C{Should a link or refresh keep it?}
  C -->|yes| D[URL]
  C -->|no| E{Used by one component?}
  E -->|yes| F[useState]
  E -->|no| G{Used by nearby components?}
  G -->|yes| H[Lift to the common parent]
  G -->|no| I{Changes rarely?}
  I -->|yes| J[Context]
  I -->|no| K[Redux Toolkit or Zustand]
""")),
    section("context", "concept", "Context",
            "Context passes a value to any depth without threading props. It is not a state manager: every consumer "
            "re-renders when the value changes, so it suits rarely changing values.",
            code("tsx", """
const AuthContext = createContext<{ user: User | null } | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const value = useMemo(() => ({ user, setUser }), [user]);   // a new object each render would re-render all consumers
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
""")),
    section("reducer", "concept", "useReducer",
            "When several values change together, a reducer puts every transition in one pure function, which is easy "
            "to test without rendering.",
            code("tsx", """
type Action =
  | { type: 'add'; item: Item }
  | { type: 'remove'; id: number }
  | { type: 'clear' };

function cartReducer(state: Item[], action: Action): Item[] {
  switch (action.type) {
    case 'add':    return [...state, action.item];
    case 'remove': return state.filter((i) => i.id !== action.id);
    case 'clear':  return [];
  }
}

const [cart, dispatch] = useReducer(cartReducer, []);
dispatch({ type: 'add', item });
""")),
    section("server", "concept", "Server state is different",
            "Data from your API is a cache of something you do not own: it can go stale and needs loading states, "
            "retries and invalidation. Libraries handle this, and most of what people once kept in Redux disappears.",
            code("tsx", """
function Books() {
  const queryClient = useQueryClient();
  const { data, isPending, error } = useQuery({
    queryKey: ['books'],
    queryFn: () => fetch('/api/books').then((r) => r.json()),
  });

  const borrow = useMutation({
    mutationFn: (id: number) => fetch(`/api/books/${id}/borrow`, { method: 'POST' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['books'] }),   // refetch
  });

  if (isPending) return <p>Loading</p>;
  if (error) return <p>Could not load books</p>;
  return <BookList books={data} onBorrow={(id) => borrow.mutate(id)} />;
}
""")),
    section("notes", "notes", "Important notes",
            note("warning", "Gotcha", "Do not copy props or server data into state. Two copies drift apart. Derive what you can during render, and keep one source of truth."),
            interview("**When would you use Redux?** Only for complex client state shared widely, with many transitions you want to trace. Most apps need local state, Context for rare globals, and a query library for server data."),
            keypoints("Sort state by kind before choosing a tool.", "Server state belongs in a query library.",
                      "Context suits rarely changing values, because all consumers re-render.", "Keep one source of truth, and derive the rest.")),
    practice(("Why is Context a poor fit for a frequently changing value?",
              "Every consumer re-renders whenever the value changes, even those using only part of it."),
             ("Where should a search term live if users share links to results?",
              "In the URL query string, so a link or a refresh restores it."),
             ("What problem does a query library solve that `useEffect` plus `useState` does not?",
              "Caching, deduplicating requests, background refetching, retries and invalidation after mutations.")),
]

# ------------------------------------------------------------------ Rendering and performance
TOPICS["frontend-react-performance"] = [
    section("intro", "introduction", "How rendering works", NOTICE,
            "\"Rendering\" means React calling your component function. It does not mean updating the DOM. React then "
            "compares the result and touches only what changed, so a render with no changes is usually cheap.",
            diagram("From state change to screen", """
flowchart LR
  A[setState] --> B[Render phase<br/>call the components, compare trees]
  B --> C[Commit phase<br/>apply DOM changes]
  C --> D[Browser paints]
  D --> E[Effects run]
""", "The render phase can be repeated or discarded, so it must have no side effects."),
            "A component re-renders when **its state changes, its parent re-renders, or a context it uses changes**. "
            "Props changing is not the trigger: by default a child re-renders whenever its parent does, even with "
            "identical props."),
    section("tools", "concept", "memo, useMemo and useCallback",
            code("tsx", """
const BookRow = memo(function BookRow({ book, onBorrow }: Props) {
  return <li>{book.title} <button onClick={() => onBorrow(book.id)}>Borrow</button></li>;
});

function Library({ books, filter }: { books: Book[]; filter: string }) {
  // skip an expensive calculation when its inputs did not change
  const visible = useMemo(() => books.filter((b) => b.title.includes(filter)), [books, filter]);

  // keep the same function, otherwise memo above sees a new prop on every render
  const onBorrow = useCallback((id: number) => api.borrow(id), []);

  return <ul>{visible.map((b) => <BookRow key={b.id} book={b} onBorrow={onBorrow} />)}</ul>;
}
""", "Together they let a row skip re-rendering", [
                {"lines": "1", "title": "memo", "text": "Skips re-rendering when all props are shallowly equal."},
                {"lines": "8", "title": "useMemo", "text": "Caches a calculated value until its dependencies change."},
                {"lines": "11", "title": "useCallback", "text": "A new arrow function on each render would defeat `memo`, so the function is kept stable."},
            ]),
            note("tip", "Measure first", "Use the React DevTools Profiler to find what is slow before adding these. They have a cost and do nothing unless the child is memoised or the calculation is expensive. "
                 "The React Compiler can add this memoisation automatically in projects that enable it.")),
    section("fixes", "example", "Fixes that usually matter more",
            table(["Problem", "Fix"], [
                ["Typing in an input re-renders a whole page", "Move the state down into the component that uses it"],
                ["A list of thousands of rows", "Virtualise it (TanStack Virtual, react-window): render only visible rows"],
                ["A large initial bundle", "Split routes with `lazy` and `Suspense`"],
                ["Typing lags behind a heavy filtered list", "`useDeferredValue` or `useTransition` to mark the update as low priority"],
                ["Rows lose state or remount", "Use stable keys; do not define components inside components"],
            ]),
            code("tsx", """
const Reports = lazy(() => import('./Reports'));     // separate bundle, loaded on demand

<Suspense fallback={<p>Loading</p>}>
  <Reports />
</Suspense>

// typing stays responsive; the list catches up when the browser is free
const deferred = useDeferredValue(query);
const results = useMemo(() => search(items, deferred), [items, deferred]);
""")),
    section("notes", "notes", "Important notes",
            note("warning", "Gotcha", "Defining a component inside another component creates a new type on every render, so React unmounts and remounts it and its state is lost. Define components at the top level."),
            interview("**A page is slow. What do you do?** Reproduce it in a production build, record with the React DevTools Profiler, and find which components render and why. "
                      "Then move state down first, virtualise long lists, split bundles, and add `memo` only where the profile shows a benefit."),
            keypoints("Render means calling the function, not updating the DOM.", "A parent re-rendering re-renders its children by default.",
                      "Moving state down is usually the best fix.", "`memo` needs stable props, hence `useCallback` and `useMemo`.",
                      "Measure with the Profiler, in a production build.")),
    practice(("Does a child re-render if its props did not change?",
              "Yes, when its parent re-renders, unless it is wrapped in `memo`."),
             ("Why doesn't `memo` help when you pass `onClick={() => ...}`?",
              "A new function is created on every render, so the prop always differs. Use `useCallback`."),
             ("You must show 50,000 rows. What do you do?",
              "Virtualise: render only the visible rows and reuse them while scrolling."),
             ("Why must rendering have no side effects?",
              "React may call a component several times or discard a render, so side effects could run repeatedly or for output never shown.")),
]

# ------------------------------------------------------------------ React with Spring Boot
TOPICS["frontend-react-spring"] = [
    section("intro", "introduction", "Connecting the two halves", NOTICE,
            "This page ties React to the Spring Boot API from your guides: routing, calling the API, CORS, JWT handling "
            "and forms.",
            diagram("A full-stack request", """
sequenceDiagram
  participant B as Browser (React)
  participant S as Spring Boot API
  participant D as Database
  B->>S: POST /api/auth/login (email, password)
  S->>D: find user, check password hash
  S-->>B: access token, refresh token in HttpOnly cookie
  B->>S: GET /api/books with Authorization Bearer token
  S->>S: security filter chain validates the token
  S->>D: query
  S-->>B: 200 with JSON
  B->>B: setState, React re-renders
""")),
    section("routing", "concept", "Client-side routing",
            code("tsx", """
function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<RequireAuth />}>
        <Route path="/books" element={<Books />} />
        <Route path="/books/:id" element={<BookDetail />} />
      </Route>
    </Routes>
  );
}

function BookDetail() {
  const { id } = useParams();
  // ...
}
""", "React Router"),
            note("warning", "Gotcha", "Hiding a route in React is not security: anyone can call your API directly. Authorisation must be enforced in Spring. "
                 "Also, when Spring serves the built app, unknown paths like `/books/7` must return `index.html`, or a page refresh gives a 404.")),
    section("api", "code", "An API client",
            "Put HTTP in one place, so the token, error handling and base URL are not repeated in every component.",
            code("typescript", """
const BASE = import.meta.env.VITE_API_URL ?? '';

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (res.status === 401) { onUnauthorized(); throw new Error('Unauthorized'); }
  if (!res.ok) {
    const problem = await res.json().catch(() => null);   // Spring ProblemDetail, if any
    throw new Error(problem?.detail ?? `HTTP ${res.status}`);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}
""", "api.ts")),
    section("cors", "concept", "CORS, and why you often avoid it",
            "The browser blocks JavaScript from reading responses from a different origin unless the server allows it. "
            "CORS is enforced by the browser: `curl` and Postman ignore it.",
            code("java", """
@Bean
CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://app.example.com"));   // never "*" with credentials
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE"));
    config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
    config.setAllowCredentials(true);
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", config);
    return source;
}
""", "Spring: enable with http.cors(withDefaults())"),
            "In development, skip CORS with a Vite proxy, so the browser sees a single origin:",
            code("javascript", """
// vite.config.js
export default { server: { proxy: { '/api': 'http://localhost:8080' } } };
""")),
    section("tokens", "concept", "Where to keep the token",
            table(["Storage", "XSS can steal it?", "CSRF risk?", "Notes"], [
                ["`localStorage`", "Yes", "No", "Simple, but any injected script can read it"],
                ["Memory (a variable)", "Harder", "No", "Lost on refresh, so pair it with a refresh cookie"],
                ["`HttpOnly` cookie", "No", "Yes, needs SameSite or a CSRF token", "JavaScript cannot read it"],
            ], "A common pattern: a short-lived access token in memory, and a refresh token in an HttpOnly cookie.")),
    section("forms", "code", "Forms and validation errors",
            "Show Spring's validation errors next to the fields. Client checks give fast feedback; the server has the "
            "final word.",
            code("tsx", """
function NewBook() {
  const [title, setTitle] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  async function onSubmit(e: FormEvent) {
    e.preventDefault();                     // stop the full-page form post
    const res = await fetch('/api/books', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
    if (res.status === 400) {
      setErrors((await res.json()).errors ?? {});   // the shape your @ControllerAdvice returns
      return;
    }
    // success: navigate, or invalidate the books query
  }

  return (
    <form onSubmit={onSubmit}>
      <input value={title} onChange={(e) => setTitle(e.target.value)} aria-invalid={!!errors.title} />
      {errors.title && <p role="alert">{errors.title}</p>}
      <button>Save</button>
    </form>
  );
}
""")),
    section("notes", "notes", "Important notes",
            interview("**Your React app gets a CORS error from Spring. Walk through it.** The browser sends a preflight `OPTIONS` for non-simple requests, and the response must allow the origin, method and headers. "
                      "With Spring Security, enable `http.cors(...)` so the preflight is handled before authentication; otherwise it gets a 401. In development, a Vite proxy avoids the issue."),
            keypoints("Security lives in Spring; hiding UI is only cosmetic.", "Keep HTTP in one API client.",
                      "CORS is enforced by the browser.", "Choose token storage knowing the XSS and CSRF trade-offs.",
                      "Serve `index.html` for unknown paths so client routes survive a refresh.")),
    practice(("Why does a request work in Postman but fail with CORS in the browser?",
              "CORS is enforced by browsers only. Postman does not apply the same-origin policy."),
             ("Why does `/books/7` give a 404 on refresh in production?",
              "The server looks for that path and finds nothing. It must fall back to `index.html` so the client router can handle it."),
             ("Is a `RequireAuth` route enough to protect admin data?",
              "No. It only hides the screen. The API must check authorisation on every request."),
             ("What is the XSS risk of `localStorage` for tokens?",
              "Any script running on your page, including an injected one, can read and send the token.")),
]

# ------------------------------------------------------------------ Testing
TOPICS["frontend-testing"] = [
    section("intro", "introduction", "What to test", NOTICE,
            "Test what the user sees and does, not implementation details. A test that survives a refactor is worth "
            "more than one that checks internal state. Your Spring guides cover JUnit, Mockito and Testcontainers; "
            "these are the equivalents for the frontend.",
            table(["Level", "Tool", "Java equivalent", "Tests"], [
                ["Unit", "Vitest or Jest", "JUnit", "Pure functions, reducers, hooks"],
                ["Component", "React Testing Library", "`@WebMvcTest`, roughly", "A component in a simulated DOM"],
                ["API mocking", "MSW (Mock Service Worker)", "WireMock", "Network calls intercepted"],
                ["End to end", "Playwright or Cypress", "Selenium", "The real app in a real browser"],
            ])),
    section("component", "code", "A component test",
            code("tsx", """
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('borrowing a book calls back with its id', async () => {
  const onBorrow = vi.fn();
  render(<BookRow book={{ id: 7, title: 'Dune', available: true }} onBorrow={onBorrow} />);

  await userEvent.click(screen.getByRole('button', { name: 'Borrow' }));

  expect(onBorrow).toHaveBeenCalledWith(7);
});

test('shows on loan when not available', () => {
  render(<BookRow book={{ id: 7, title: 'Dune', available: false }} onBorrow={vi.fn()} />);

  expect(screen.getByText('On loan')).toBeInTheDocument();
  expect(screen.queryByRole('button')).not.toBeInTheDocument();
});
""", "BookRow.test.tsx", [
                {"lines": "5", "title": "A mock", "text": "`vi.fn()` plays the role of a Mockito mock."},
                {"lines": "8", "title": "Find by role", "text": "Query as a user would: by role and name. This also checks accessibility."},
                {"lines": "10", "title": "Assert the result", "text": "Check what happened, not the component's internal state."},
                {"lines": "17", "title": "queryBy for absence", "text": "`getBy` throws when nothing matches; `queryBy` returns null, so it can assert absence."},
            ])),
    section("async", "code", "Async behaviour and API mocking",
            code("tsx", """
const server = setupServer(
  http.get('/api/books', () => HttpResponse.json([{ id: 1, title: 'Dune', available: true }])),
);
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('loads and shows books', async () => {
  render(<Books />);
  expect(screen.getByText('Loading')).toBeInTheDocument();
  expect(await screen.findByText('Dune')).toBeInTheDocument();     // findBy waits
});

test('shows an error when the API fails', async () => {
  server.use(http.get('/api/books', () => new HttpResponse(null, { status: 500 })));
  render(<Books />);
  expect(await screen.findByText('Could not load books')).toBeInTheDocument();
});
""", "MSW intercepts fetch, so the component is unchanged")),
    section("notes", "notes", "Important notes",
            note("warning", "Gotcha", "`getBy` fails immediately if the element is not there yet. After async work use `await findBy...`, which retries for a short time."),
            interview("**How do you test a React component?** With React Testing Library: render it, interact as a user through roles and text, and assert what appears. Mock the network with MSW rather than mocking `fetch` or your hooks, so the test stays close to reality."),
            keypoints("Test behaviour, not implementation.", "Prefer queries by role, then label, then text.",
                      "Use `findBy` after async work, and `queryBy` to assert absence.", "Mock at the network with MSW.",
                      "Keep a few end-to-end tests for critical journeys.")),
    practice(("What is the difference between `getBy`, `queryBy` and `findBy`?",
              "`getBy` throws if missing, `queryBy` returns null if missing, and `findBy` returns a promise that retries until the element appears."),
             ("Why query by role rather than by CSS class?",
              "Roles reflect what the user perceives and survive styling changes, and they catch missing accessibility."),
             ("Why mock with MSW instead of mocking your API module?",
              "The real fetch code and error handling still run, so the test covers more and needs no change when you refactor the client.")),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for topic_id, sections in TOPICS.items():
        (OUT / f"{topic_id}.json").write_text(
            json.dumps({"source": SOURCE, "sections": sections}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(topic_id, len(sections), "sections")


if __name__ == "__main__":
    main()
