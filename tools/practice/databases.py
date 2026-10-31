"""Practice subject: Databases. SQL questions run in the browser on this dataset (SQLite); theory questions are written."""

DATASET_SQL = """
CREATE TABLE customers (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT, country TEXT NOT NULL, signup_date TEXT NOT NULL);
INSERT INTO customers VALUES
 (1,'Asha Rao','Bengaluru','India','2024-01-15'),
 (2,'Ben Carter','Austin','USA','2024-02-03'),
 (3,'Chitra Iyer','Chennai','India','2024-02-20'),
 (4,'Diego Silva','Sao Paulo','Brazil','2024-03-11'),
 (5,'Emma Stone',NULL,'UK','2024-03-29'),
 (6,'Farhan Ali','Hyderabad','India','2024-04-18'),
 (7,'Grace Lee','Seattle','USA','2024-05-02'),
 (8,'Hiro Tanaka','Osaka','Japan','2024-05-21'),
 (9,'Isha Nair','Kochi','India','2024-06-09'),
 (10,'Jack Brown','London','UK','2024-06-30');

CREATE TABLE products (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, price REAL NOT NULL);
INSERT INTO products VALUES
 (1,'Mechanical Keyboard','Electronics',89.0),
 (2,'Wireless Mouse','Electronics',29.5),
 (3,'USB-C Hub','Electronics',45.0),
 (4,'Noise-Cancelling Headphones','Electronics',199.0),
 (5,'Java Concurrency in Practice','Books',42.0),
 (6,'Clean Code','Books',35.0),
 (7,'Designing Data-Intensive Applications','Books',55.0),
 (8,'Standing Desk','Furniture',320.0),
 (9,'Ergonomic Chair','Furniture',275.0),
 (10,'Desk Lamp','Furniture',24.0);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id),
  order_date TEXT NOT NULL, status TEXT NOT NULL);
INSERT INTO orders VALUES
 (1,1,'2024-07-03','delivered'), (2,1,'2024-08-12','delivered'), (3,2,'2024-07-15','delivered'),
 (4,3,'2024-07-21','cancelled'), (5,3,'2024-08-02','delivered'), (6,4,'2024-08-09','shipped'),
 (7,6,'2024-08-17','delivered'), (8,7,'2024-08-25','delivered'), (9,9,'2024-09-01','pending'),
 (10,1,'2024-09-05','delivered'), (11,2,'2024-09-12','delivered'), (12,6,'2024-09-20','cancelled'),
 (13,7,'2024-10-04','delivered'), (14,3,'2024-10-11','shipped');

CREATE TABLE order_items (
  order_id INTEGER NOT NULL REFERENCES orders(id), product_id INTEGER NOT NULL REFERENCES products(id),
  quantity INTEGER NOT NULL, PRIMARY KEY (order_id, product_id));
INSERT INTO order_items VALUES
 (1,1,1),(1,2,2),(2,5,1),(2,6,1),(3,4,1),(4,8,1),(5,3,2),(5,10,1),(6,9,1),(7,7,2),(7,5,1),
 (8,1,1),(8,3,1),(9,6,3),(10,4,1),(10,2,1),(11,5,2),(12,9,1),(13,8,1),(13,10,2),(14,7,1),(14,2,3);

CREATE TABLE employees (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, department TEXT NOT NULL, salary INTEGER NOT NULL,
  manager_id INTEGER REFERENCES employees(id), hire_date TEXT NOT NULL);
INSERT INTO employees VALUES
 (1,'Meera Joshi','Engineering',250000,NULL,'2019-04-01'),
 (2,'Rahul Verma','Engineering',180000,1,'2020-06-15'),
 (3,'Sneha Kulkarni','Engineering',185000,1,'2020-09-01'),
 (4,'Arjun Mehta','Engineering',120000,2,'2021-01-10'),
 (5,'Priya Nair','Engineering',185000,2,'2022-03-21'),
 (6,'Kabir Singh','Sales',150000,1,'2020-02-17'),
 (7,'Divya Reddy','Sales',90000,6,'2021-07-05'),
 (8,'Nikhil Shah','Sales',90000,6,'2022-11-14'),
 (9,'Tara Bose','HR',110000,1,'2021-05-24'),
 (10,'Vikram Das','Engineering',190000,3,'2023-01-09'),
 (11,'Anita Pillai','HR',70000,9,'2023-06-12');
"""

DESCRIPTION = """A small online shop and a company's staff. Dates are text in `YYYY-MM-DD` form (SQLite has no separate date type), so
`strftime('%Y-%m', order_date)` gives the month.

| Table | Columns |
|---|---|
| `customers` | `id`, `name`, `city` (can be NULL), `country`, `signup_date` |
| `products` | `id`, `name`, `category`, `price` |
| `orders` | `id`, `customer_id`, `order_date`, `status` (`pending`, `shipped`, `delivered`, `cancelled`) |
| `order_items` | `order_id`, `product_id`, `quantity` |
| `employees` | `id`, `name`, `department`, `salary`, `manager_id` (NULL for the top manager), `hire_date` |

The line total of an order item is `price * quantity`. This engine is SQLite, so a few functions differ from PostgreSQL or MySQL;
the SQL you write here (joins, grouping, window functions, CTEs) is standard."""


def sql(id_, title, level, prompt, solution, hint=None, ordered=False, explanation=None):
    q = {"id": id_, "type": "sql", "title": title, "level": level, "prompt": prompt, "solution": solution.strip()}
    if hint:
        q["hint"] = hint
    if ordered:
        q["ordered"] = True
    if explanation:
        q["explanation"] = explanation
    return q


def written(id_, title, level, prompt, answer, hint=None):
    q = {"id": id_, "type": "written", "title": title, "level": level, "prompt": prompt, "answer": answer}
    if hint:
        q["hint"] = hint
    return q


QUESTIONS = [
    sql("db-sql-india", "Customers from India", "Easy",
        "Return the `name` and `city` of every customer from India, ordered by name.",
        "SELECT name, city FROM customers WHERE country = 'India' ORDER BY name;", ordered=True,
        hint="Filter with `WHERE`, sort with `ORDER BY`. Text comparisons are case-sensitive for `=` in most databases."),
    sql("db-sql-top3", "The three priciest products", "Easy",
        "Return the `name` and `price` of the 3 most expensive products, the most expensive first.",
        "SELECT name, price FROM products ORDER BY price DESC LIMIT 3;", ordered=True,
        hint="`ORDER BY ... DESC` then `LIMIT` (`FETCH FIRST 3 ROWS ONLY` in standard SQL)."),
    sql("db-sql-null-city", "Customers without a city", "Easy",
        "Return the `name` of every customer whose city is not known (NULL).",
        "SELECT name FROM customers WHERE city IS NULL;",
        hint="`city = NULL` is never true: comparing with NULL gives UNKNOWN. Use `IS NULL`."),
    sql("db-sql-per-country", "Countries with several customers", "Easy",
        "For each country that has at least 2 customers, return the `country` and the number of customers. Most customers first; break ties by country name.",
        "SELECT country, COUNT(*) AS customers FROM customers GROUP BY country HAVING COUNT(*) >= 2 ORDER BY customers DESC, country;",
        ordered=True, hint="`WHERE` filters rows before grouping; `HAVING` filters groups after."),
    sql("db-sql-status-count", "Orders per status", "Easy",
        "Return each order `status` and how many orders have it. Most common status first; break ties by status name.",
        "SELECT status, COUNT(*) AS orders FROM orders GROUP BY status ORDER BY orders DESC, status;", ordered=True),
    sql("db-sql-order-totals", "Big orders", "Medium",
        "For every order whose total is above 100, return the order `id` (as `order_id`) and its `total` (sum of price times quantity). Largest total first; break ties by order id.",
        """SELECT o.id AS order_id, SUM(p.price * oi.quantity) AS total
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
GROUP BY o.id
HAVING SUM(p.price * oi.quantity) > 100
ORDER BY total DESC, order_id;""", ordered=True,
        hint="Join three tables, group by the order, and filter the groups with `HAVING` (a `WHERE` cannot see an aggregate)."),
    sql("db-sql-never-ordered", "Customers who never ordered", "Medium",
        "Return the `name` of every customer who has not placed any order, in alphabetical order.",
        """SELECT c.name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL
ORDER BY c.name;""", ordered=True,
        hint="A `LEFT JOIN` keeps customers without orders and fills the order columns with NULL. `NOT EXISTS` and `NOT IN` also work; beware `NOT IN` when the subquery can return NULL."),
    sql("db-sql-category-revenue", "Revenue by category", "Medium",
        "Looking only at orders with status `delivered`, return each product `category` and its `revenue` (sum of price times quantity), for categories with a revenue above 350. Highest revenue first.",
        """SELECT p.category, SUM(p.price * oi.quantity) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status = 'delivered'
GROUP BY p.category
HAVING SUM(p.price * oi.quantity) > 350
ORDER BY revenue DESC;""", ordered=True),
    sql("db-sql-top-spender", "The top spender", "Medium",
        "Which customer has spent the most on orders that are not cancelled? Return that customer's `name` and `total`.",
        """SELECT c.name, SUM(p.price * oi.quantity) AS total
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status <> 'cancelled'
GROUP BY c.id, c.name
ORDER BY total DESC
LIMIT 1;""",
        hint="Group by the customer (include `c.id`, two customers can share a name), sort by the sum, take one row."),
    sql("db-sql-self-join", "Earning more than the manager", "Medium",
        "Return the `name` of every employee who earns more than their own manager, in alphabetical order.",
        """SELECT e.name
FROM employees e
JOIN employees m ON m.id = e.manager_id
WHERE e.salary > m.salary
ORDER BY e.name;""", ordered=True,
        hint="Join the table to itself: one copy plays the employee, the other the manager."),
    sql("db-sql-above-avg", "Above the department average", "Medium",
        "Return the `name`, `department` and `salary` of every employee who earns more than the average salary of their own department. Order by department, then by salary highest first.",
        """SELECT e.name, e.department, e.salary
FROM employees e
WHERE e.salary > (SELECT AVG(salary) FROM employees WHERE department = e.department)
ORDER BY e.department, e.salary DESC;""", ordered=True,
        hint="A correlated subquery that refers to the outer row, or a join to a per-department average computed in a CTE."),
    sql("db-sql-second-highest", "Second highest salary", "Medium",
        "Return the second highest distinct salary as a single value.",
        "SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);",
        hint="The maximum below the maximum. Alternatives: `SELECT DISTINCT salary ... ORDER BY salary DESC LIMIT 1 OFFSET 1`, or `DENSE_RANK()`."),
    sql("db-sql-top2-per-dept", "Top two salaries per department", "Hard",
        "For each department, return the employees who have one of the two highest distinct salaries in that department (people with equal salaries share a rank, so a tie can produce more than two rows). Return `name`, `department`, `salary`, ordered by department, salary highest first, then name.",
        """WITH ranked AS (
  SELECT name, department, salary,
         DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rnk
  FROM employees
)
SELECT name, department, salary
FROM ranked
WHERE rnk <= 2
ORDER BY department, salary DESC, name;""", ordered=True,
        hint="A window function cannot be used in `WHERE` directly, so compute the rank in a CTE or subquery first. `RANK` leaves gaps after ties, `DENSE_RANK` does not."),
    sql("db-sql-running-total", "Monthly revenue with a running total", "Hard",
        "For delivered orders only, return one row per month with `month` (as `YYYY-MM`), `revenue` for that month, and `running_total`, the revenue of that month plus all earlier months. Oldest month first.",
        """WITH monthly AS (
  SELECT strftime('%Y-%m', o.order_date) AS month, SUM(p.price * oi.quantity) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.id
  JOIN products p ON p.id = oi.product_id
  WHERE o.status = 'delivered'
  GROUP BY strftime('%Y-%m', o.order_date)
)
SELECT month, revenue, SUM(revenue) OVER (ORDER BY month) AS running_total
FROM monthly
ORDER BY month;""", ordered=True,
        hint="Aggregate to one row per month first, then add `SUM(...) OVER (ORDER BY month)` on top."),
    sql("db-sql-mom-change", "Month-over-month change", "Hard",
        "Using the same monthly delivered revenue, return `month`, `revenue` and `change`: this month's revenue minus the previous month's (NULL for the first month). Oldest month first.",
        """WITH monthly AS (
  SELECT strftime('%Y-%m', o.order_date) AS month, SUM(p.price * oi.quantity) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.id
  JOIN products p ON p.id = oi.product_id
  WHERE o.status = 'delivered'
  GROUP BY strftime('%Y-%m', o.order_date)
)
SELECT month, revenue, revenue - LAG(revenue) OVER (ORDER BY month) AS change
FROM monthly
ORDER BY month;""", ordered=True,
        hint="`LAG(column) OVER (ORDER BY ...)` reads the previous row's value."),
    sql("db-sql-all-categories", "Customers who bought from every category", "Hard",
        "Return the `name` of each customer who has bought at least one product from every product category, counting only orders that are not cancelled.",
        """SELECT c.name
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status <> 'cancelled'
GROUP BY c.id, c.name
HAVING COUNT(DISTINCT p.category) = (SELECT COUNT(DISTINCT category) FROM products);""",
        hint="This is relational division: compare the number of distinct categories a customer bought with the total number of categories."),

    written("db-theory-acid", "What does ACID mean?", "Easy",
        "Explain each letter of ACID, with one example of what goes wrong without it.",
        "**Atomicity**: a transaction either happens completely or not at all. Without it, a transfer could debit one account and crash before crediting the other.\n\n"
        "**Consistency**: a transaction moves the database from one valid state to another, so constraints (keys, checks, foreign keys) always hold after commit.\n\n"
        "**Isolation**: concurrent transactions do not see each other's half-finished work. Without it, one report could read a balance in the middle of another transaction's update.\n\n"
        "**Durability**: once committed, the data survives a crash or power loss. Databases achieve it by writing the change to a write-ahead log on disk before acknowledging the commit."),
    written("db-theory-isolation", "Isolation levels and anomalies", "Medium",
        "Name the three classic read anomalies and the isolation level that prevents each. Which level does PostgreSQL use by default?",
        "- **Dirty read**: reading another transaction's uncommitted change. Prevented from READ COMMITTED upwards.\n"
        "- **Non-repeatable read**: reading the same row twice and getting different values because someone committed in between. Prevented from REPEATABLE READ.\n"
        "- **Phantom read**: running the same query twice and getting different *sets* of rows because someone inserted or deleted matching rows. Prevented by SERIALIZABLE in the SQL standard (PostgreSQL's REPEATABLE READ, which is snapshot based, also prevents it).\n\n"
        "PostgreSQL and Oracle default to **READ COMMITTED**; MySQL InnoDB defaults to **REPEATABLE READ**. Higher isolation costs more locking or more retries, so choose the lowest level that is correct for the operation.",
        hint="Think of what each level adds: first no dirty reads, then stable rows, then stable result sets."),
    written("db-theory-index", "How does an index help, and when does it not?", "Medium",
        "Explain how a B-tree index speeds up queries, and give three cases where a query cannot use an index well.",
        "A B-tree index keeps the indexed column values in sorted order in a balanced tree, so the database finds a value, a range or the first rows of an `ORDER BY` in O(log n) page reads instead of scanning the whole table. A **composite index** `(a, b)` helps queries that filter on `a`, or on `a` and `b` (the leftmost prefix), but not on `b` alone.\n\n"
        "It helps little or not at all when:\n"
        "1. The column is wrapped in a function or expression: `WHERE LOWER(email) = ...` or `WHERE price + 1 > 10` (use a functional index or rewrite).\n"
        "2. The pattern starts with a wildcard: `LIKE '%son'` cannot use the sort order.\n"
        "3. The column has low selectivity (a boolean, a status with 3 values) so the planner prefers a scan, or the query returns a large fraction of the table.\n\n"
        "Indexes are not free: each one slows `INSERT`, `UPDATE` and `DELETE` and uses disk and memory. Read the plan with `EXPLAIN` before and after adding one."),
    written("db-theory-joins", "INNER, LEFT and FULL joins", "Easy",
        "What is the difference between INNER JOIN, LEFT JOIN and FULL OUTER JOIN? What happens to rows with NULL in the join column?",
        "- **INNER JOIN** returns only the rows that have a match on both sides.\n"
        "- **LEFT JOIN** returns every row of the left table; where the right table has no match its columns are NULL. Filtering on a right-table column in the `WHERE` clause turns it back into an inner join, so put such conditions in the `ON` clause when you want to keep unmatched rows.\n"
        "- **FULL OUTER JOIN** returns every row of both tables, with NULLs where there is no match on the other side (not available in MySQL or SQLite older versions).\n\n"
        "`NULL = NULL` is not true, so rows with NULL in the join column never match each other in an equi-join."),
    written("db-theory-normal", "Normalisation", "Medium",
        "Explain 1NF, 2NF and 3NF with a short example, and say when you would denormalise on purpose.",
        "**1NF**: every column holds one atomic value and there are no repeating groups (no `phones = '123, 456'`; use a child table).\n\n"
        "**2NF**: in a table with a composite key, every non-key column depends on the *whole* key, not part of it. In `order_items(order_id, product_id, product_name, quantity)` the `product_name` depends only on `product_id`, so it moves to `products`.\n\n"
        "**3NF**: non-key columns depend on the key and *nothing but* the key. In `employees(id, department_id, department_name)`, `department_name` depends on `department_id`, so it moves to `departments`.\n\n"
        "Normalising removes update anomalies and duplicated data. You denormalise on purpose for read performance (a precomputed `order_total`, a copied `customer_name` on an invoice that must keep the historical value, a reporting table), accepting that you must keep the copies consistent."),
    written("db-theory-keyset", "Slow pagination", "Hard",
        "`SELECT ... ORDER BY id LIMIT 20 OFFSET 1000000` gets slower the deeper you page. Why, and what is the alternative?",
        "With `OFFSET n` the database must still produce and discard the first n rows before returning the next 20, so the cost grows linearly with the page number, and concurrent inserts can make rows move between pages.\n\n"
        "**Keyset (seek) pagination** remembers the last key of the previous page and asks for what comes after it: `WHERE id > :lastId ORDER BY id LIMIT 20`. With an index on `id` the database jumps straight to the start of the page in O(log n), whatever the depth. For a non-unique sort column, use a composite condition such as `(created_at, id) > (:lastCreatedAt, :lastId)`. The trade-off is that you cannot jump to an arbitrary page number, only move forward and back."),
    written("db-theory-deadlock", "Deadlocks", "Medium",
        "How does a database deadlock happen, and how do you reduce them in an application?",
        "A deadlock occurs when two transactions each hold a lock the other needs: T1 updates row A then wants row B, while T2 updated row B and wants row A. Neither can proceed. The database detects the cycle and aborts one transaction, which the application sees as an error to retry.\n\n"
        "To reduce them: **access rows in the same order** in every transaction (for example by ascending id), **keep transactions short** and avoid user interaction or remote calls inside them, **lock only what you need** (use indexes so updates do not lock whole ranges), use a lower isolation level where it is correct, and **retry** the aborted transaction a bounded number of times."),
    written("db-theory-where-having", "WHERE versus HAVING", "Easy",
        "What is the difference between WHERE and HAVING, and in which order does a SELECT logically run?",
        "`WHERE` filters individual rows **before** grouping, so it cannot use aggregate functions. `HAVING` filters groups **after** `GROUP BY`, so it can (`HAVING COUNT(*) > 5`). Where possible, filter with `WHERE`: it reduces the rows that have to be grouped.\n\n"
        "The logical order is: `FROM` and `JOIN`, then `WHERE`, `GROUP BY`, `HAVING`, `SELECT` (computing expressions and aliases), `DISTINCT`, `ORDER BY`, and finally `LIMIT`. That is why a column alias defined in `SELECT` cannot be used in `WHERE` in standard SQL (some databases allow it in `HAVING` or `ORDER BY`)."),
]

SUBJECT = {
    "id": "databases", "title": "Databases: SQL and theory", "group": "Databases", "order": 1,
    "description": "Write real SQL and run it on a practice database in your browser, then answer the theory questions interviewers ask about transactions, indexes and design.",
    "platforms": [
        {"name": "LeetCode: Database", "url": "https://leetcode.com/problemset/database/", "note": "SQL problems from easy to hard"},
        {"name": "HackerRank: SQL", "url": "https://www.hackerrank.com/domains/sql", "note": "Graded SQL challenges"},
        {"name": "GeeksforGeeks: SQL", "url": "https://www.geeksforgeeks.org/sql/sql-tutorial/", "note": "Tutorial and interview questions"},
    ],
    "dataset": {"title": "Practice database: shop and staff", "description": DESCRIPTION, "sql": DATASET_SQL.strip()},
    "questions": QUESTIONS,
}
