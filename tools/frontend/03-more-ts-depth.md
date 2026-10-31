@more
## Advanced types you'll actually meet

You don't need type gymnastics to do daily work, but you'll read these in library code and error messages.

### Type guards

A function can teach the compiler what a check proves.

```ts A user-defined type guard
interface Dog { kind: 'dog'; bark(): string; }
interface Cat { kind: 'cat'; meow(): string; }
type Pet = Dog | Cat;

function isDog(p: Pet): p is Dog {
  return p.kind === 'dog';
}

function speak(p: Pet) {
  return isDog(p) ? p.bark() : p.meow();
}
```

`filter` also narrows with a guard:

```ts Removing nulls from an array
const raw: (string | null)[] = ['a', null, 'b'];
const clean = raw.filter((x): x is string => x !== null);   // string[]
```

Be careful: the compiler trusts a guard without checking it, so a wrong guard gives you confident wrong types.

### Mapped types

These transform every property of a type. It's how `Partial` is built.

```ts Mapped types
type MyPartial<T> = { [K in keyof T]?: T[K] };
type Flags<T> = { [K in keyof T]: boolean };

interface Order { id: string; total: number; }
type OrderErrors = { [K in keyof Order]?: string };
// { id?: string; total?: string }: a field-error map that always matches the form
```

### Conditional types and infer

```ts Types that compute
type IsString<T> = T extends string ? true : false;
type A = IsString<'x'>;      // true
type B = IsString<number>;   // false

type ElementOf<T> = T extends (infer U)[] ? U : never;
type C = ElementOf<string[]>;  // string

type Unwrapped = Awaited<Promise<number>>;   // number
```

### Template literal types

```ts Strongly typed strings
type Size = 'sm' | 'lg';
type Side = 'left' | 'right';
type ClassName = `${Size}-${Side}`;   // 'sm-left' | 'sm-right' | 'lg-left' | 'lg-right'

type Route = `/orders/${string}`;
const ok: Route = '/orders/42';
```

### satisfies

`satisfies` checks a value against a type, while keeping its specific inferred type.

```ts satisfies keeps the detail
type Theme = Record<string, string>;

const a: Theme = { primary: '#000' };
a.primary;                   // string
a.missing;                   // allowed, unsound without noUncheckedIndexedAccess

const b = { primary: '#000' } satisfies Theme;
b.primary;                   // fine
// b.missing;                // compile error: this key doesn't exist
```

### Function overloads and generics with constraints

```ts Constraints
function byId<T extends { id: string }>(items: T[]): Map<string, T> {
  return new Map(items.map((x) => [x.id, x]));
}
```

### Reading long error messages

TypeScript errors can run many lines. Read from the **bottom up**, since the last line usually states the real mismatch. For example: "Type 'unknown' is not assignable to type 'number'" at the end of a long form error tells you exactly which field differs.

### Don't overdo it

| Reasonable | Probably too much |
|---|---|
| Unions, generics with one or two parameters | Recursive conditional types in app code |
| `Pick`, `Omit`, `Partial` | Types nobody on the team can read |
| A type guard at a boundary | `as` everywhere to silence errors |

`as` tells the compiler to trust you, and it's the usual way that types and reality drift apart. Use it rarely, and never `as any`.

!keypoints Guards teach narrowing, but aren't checked ;; Mapped types transform every field ;; satisfies keeps specific types ;; Read long errors from the bottom

?? Why might a type guard be dangerous?
=> The compiler trusts it. If its logic is wrong, your types are wrong with no warning.
?? What does `as const` differ from `satisfies` in?
=> `as const` makes literal, readonly types. `satisfies` checks against a type without widening.
?? Where do you start with a long TypeScript error?
=> At the bottom line, which usually names the real mismatch.

## Modelling a real API in TypeScript

### A worked example: paged orders

```ts Types for a Spring Data response
interface Page<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  number: number;
  size: number;
}

type OrderStatus = 'PENDING' | 'PAID' | 'SHIPPED' | 'CANCELLED';

interface OrderDto {
  id: string;
  total: string;        // BigDecimal sent as a string, to keep exact money
  status: OrderStatus;
  createdAt: string;    // an ISO instant from the server
}
```

### DTOs and view models

The server's shape isn't always what your screen needs. Convert once at the edge, rather than parsing dates in every component.

```ts A mapper at the boundary
interface OrderView {
  id: string;
  total: string;
  status: OrderStatus;
  createdAt: Date;
  canCancel: boolean;
}

const inr = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' });

function toView(dto: OrderDto): OrderView {
  return {
    id: dto.id,
    total: inr.format(Number(dto.total)),
    status: dto.status,
    createdAt: new Date(dto.createdAt),
    canCancel: dto.status === 'PENDING',
  };
}
```

```tsx Use it with a query's select
const { data } = useQuery({
  queryKey: ['orders', page],
  queryFn: () => api.get<Page<OrderDto>>(`/orders?page=${page}`),
  select: (p) => ({ ...p, content: p.content.map(toView) }),
});
```

### Exhaustive mapping

`Record` makes the compiler enforce completeness. Add a new status, and the build fails here until you handle it, a benefit Java gets from `switch` on sealed types.

```ts A label for every status
const STATUS_LABEL: Record<OrderStatus, string> = {
  PENDING: 'Awaiting payment',
  PAID: 'Paid',
  SHIPPED: 'On the way',
  CANCELLED: 'Cancelled',
};
```

### Branded types

Structural typing means that a `userId` string can be passed where an `orderId` string belongs. A brand prevents this.

```ts Stop mixing up IDs
type OrderId = string & { readonly __brand: 'OrderId' };
type UserId = string & { readonly __brand: 'UserId' };

declare function getOrder(id: OrderId): void;
declare const user: UserId;
// getOrder(user);             // compile error
```

It exists only at compile time. Use it where mix-ups would be costly.

### Environment variables

```ts Validate configuration at start-up
const Env = z.object({
  VITE_API_URL: z.url(),
  VITE_SENTRY_DSN: z.string().optional(),
});
export const env = Env.parse(import.meta.env);
```

A clear start-up failure beats a mysterious runtime bug.

### Moving JavaScript to TypeScript

1. Add `tsconfig.json` with `allowJs: true`, so that both work together.
2. Rename files one at a time, starting with small utility modules with no dependencies.
3. Add types at boundaries first: API responses, then props.
4. Allow `any` temporarily, marked with a comment.
5. Turn on `strict`, then fix what appears, in stages.

Don't rewrite everything at once. A gradual path keeps features shipping, the same way you'd migrate a legacy Java module.

!keypoints Convert DTOs at the edge ;; Record forces handling every case ;; Brands stop ID mix-ups ;; Migrate gradually

?? Why convert API data in one place?
=> Components then get ready-to-use values, and date or money parsing isn't repeated or missed.
?? You add a new OrderStatus. How can the compiler find what needs updating?
=> Exhaustive `Record<OrderStatus, ...>` maps and never-checks produce errors until each case is handled.
?? Why send BigDecimal as a string?
=> Converting to a JavaScript number can lose precision. A string keeps the exact value.
