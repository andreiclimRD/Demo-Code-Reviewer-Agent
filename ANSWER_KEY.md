# Code Review Workshop — Violations Answer Key

Each file contains intentional breaches across **all severity levels** (Blocker, Major, Minor, Nit) and **all categories** from the rubric. Use this as the scoring guide for the AI agent's output.

---

## Python — `order_service.py`

| # | Line(s) | Severity | Category | Violation |
|---|---------|----------|----------|-----------|
| 1 | 10–11 | **Blocker** | Security | Hardcoded DB connection string with production password (`S3cret!Prod#2024`). §6: no secrets hardcoded. |
| 2 | 13 | **Blocker** | Security | Hardcoded live API key (`sk-live-...`). |
| 3 | 38–40 | **Blocker** | Security | SQL injection via string concatenation in `place_order` (product lookup). §2 Security: injection + unsanitized input. |
| 4 | 43–45 | **Blocker** | Security | SQL injection in stock UPDATE. |
| 5 | 48–50 | **Blocker** | Security | SQL injection in coupon lookup. |
| 6 | 54–56 | **Blocker** | Security | SQL injection in order INSERT. |
| 7 | 63–66 | **Blocker** | Security | SQL injection in `get_user_orders`. |
| 8 | 108–110 | **Blocker** | Correctness | `process_refund` returns `None` implicitly when order not found — callers expect `True/False`. §2 Correctness: incorrect return values. |
| 9 | 59 | **Major** | Security | Sensitive data logged — coupon code and credit card hint in log message. §2 Security: sensitive data in logs. |
| 10 | 107 | **Major** | Security | Payment token and user email logged in `process_refund`. |
| 11 | 71–82 | **Major** | Performance | `generate_sales_report` fetches ALL orders unbounded, then N+1 queries inside nested loops for items and products. §2 Performance: N+1 + unbounded result set. |
| 12 | 42 | **Major** | Correctness | Stock decremented without checking `qty <= stock` — can go negative. Off-by-one / edge case. |
| 13 | 51 | **Major** | Correctness | Coupon `discount_pct` applied without validating range (could be > 1.0 → negative total). |
| 14 | 88–93 | **Major** | Conventions | `cancel_order` silently swallows all exceptions with bare `except: pass`. §6: errors handled explicitly, never silently swallowed. |
| 15 | 36 | **Major** | Correctness | No handling when `items` list is empty — inserts an order with total = 0 silently. |
| 16 | 96–105 | **Major** | Correctness | `apply_bulk_discount` does not check if `current` is `None` (order doesn't exist) — will throw `TypeError`. |
| 17 | 118–124 | **Major** | Performance | `sync_inventory` uses blocking `time.sleep()` inside an `async` function. §2 Performance: blocking calls on hot paths. §2 Correctness: async issues. |
| 18 | — | **Major** | Tests | No tests anywhere for new logic. §6: new behavior ships with tests. |
| 19 | 22–30 | **Minor** | Readability | Large block of commented-out dead code (`_get_cursor`, `old_place_order`). §6: no dead code or commented-out blocks. |
| 20 | 33–61 | **Minor** | Readability | `place_order` does too much — validates stock, applies coupon, inserts order, logs. §6: functions do one thing. |
| 21 | 33–61 | **Minor** | Conventions | Data access (raw SQL) mixed directly into business logic. §6: data access through a dedicated layer. |
| 22 | 108–112 | **Minor** | Readability | `process_refund` missing docstring; non-obvious what happens on missing order. §6: public interfaces documented. |
| 23 | 107–108 | **Nit** | Conventions | `Calc_Tax` uses PascalCase — inconsistent with the snake_case convention of the rest of the file. §6: match existing conventions. |
| 24 | 109–111 | **Nit** | Readability | Cryptic variable names `x`, `y`, `z` in `Calc_Tax`. §2 Readability: unclear naming. |

---

## Java — `PaymentService.java`

| # | Line(s) | Severity | Category | Violation |
|---|---------|----------|----------|-----------|
| 1 | 13–16 | **Blocker** | Security | Hardcoded DB URL, username (`root`), password, and Stripe secret key. |
| 2 | 33 | **Blocker** | Security | Full card number and CVV logged in `processPayment`. §2 Security: sensitive data in logs. |
| 3 | 36–38 | **Blocker** | Security | SQL injection via string concatenation in balance SELECT. |
| 4 | 42–44 | **Blocker** | Security | SQL injection in balance UPDATE. |
| 5 | 46–48 | **Blocker** | Security | SQL injection in transaction INSERT. |
| 6 | 101–102 | **Blocker** | Security | SQL injection in `generateReport` — date parameters concatenated. |
| 7 | 116–117 | **Blocker** | Security | SQL injection + no authorization check in `deleteTransaction` — any caller can delete any transaction. §2 Security: missing authorization. |
| 8 | 40 | **Major** | Correctness | Balance check uses `>` instead of `>=` — a user with exact balance cannot pay. Off-by-one. |
| 9 | 34–55 | **Major** | Correctness | `processPayment` is not transactional — if INSERT fails after UPDATE, balance is deducted but no record is created. Data loss risk. |
| 10 | 86–89 | **Major** | Conventions | `issueRefund` silently swallows `SQLException` with empty catch. §6: never silently swallow errors. |
| 11 | 62–79 | **Major** | Performance | `getAllTransactions` has triple-nested N+1 queries: transactions → details → users. |
| 12 | 59 | **Major** | Performance | `getAllTransactions` fetches unbounded — no pagination, no LIMIT. |
| 13 | 116–119 | **Major** | Correctness | `deleteTransaction` permanently deletes data with no soft-delete or authorization check — data loss risk. |
| 14 | 130–133 | **Major** | Correctness | `convertCurrency` silently returns the input amount for unknown currency pairs instead of signaling an error. Misleading return value. |
| 15 | — | **Major** | Tests | No tests for any method. §6: new behavior ships with tests. |
| 16 | 25–30 | **Minor** | Readability | Commented-out dead code (`getPaymentsByDate`). §6: no dead code or commented-out blocks. |
| 17 | 34–55 | **Minor** | Readability | `processPayment` does too much — validates balance, updates wallet, inserts transaction, logs PII. §6: functions do one thing. |
| 18 | 34–55 | **Minor** | Conventions | Raw SQL scattered in business logic methods. §6: data access through dedicated layer. |
| 19 | 92 | **Nit** | Readability | Cryptic parameter names `amt`, `r`, `t` in `calcFees`. §2 Readability: unclear naming. |
| 20 | 93–95 | **Nit** | Readability | Unnecessary intermediate variables `x`, `y`, `z` in `calcFees`. |
| 21 | 130 | **Nit** | Readability | Hardcoded exchange rates with a "good enough for now" comment — should at least be documented as a known limitation or TODO. |

---

## C# — `InventoryService.cs`

| # | Line(s) | Severity | Category | Violation |
|---|---------|----------|----------|-----------|
| 1 | 14–15 | **Blocker** | Security | Hardcoded connection string with `sa` password and live API key. |
| 2 | 41–44 | **Blocker** | Security | SQL injection in `AddProduct` — `name` and `sku` concatenated into INSERT. |
| 3 | 46 | **Blocker** | Security | API key value logged in plain text (`apiKey={ApiKey}`). |
| 4 | 55–58 | **Blocker** | Security | SQL injection in `GetProductPrice`. |
| 5 | 67–96 | **Blocker** | Security | Multiple SQL injections in `GetFullCatalog` (categories + reviews queries). |
| 6 | 118–121 | **Blocker** | Security | SQL injection + no authorization check in `DeleteProduct`. §2 Security: missing auth. |
| 7 | 108–112 | **Blocker** | Correctness | `UpdateStock` catches all exceptions and still returns `true` — caller believes success even on failure. §6: errors never silently swallowed + §2 Correctness: misleading return value. |
| 8 | 52 | **Major** | Correctness | `GetProductPrice` is `async Task<decimal>` but contains no `await` — runs synchronously despite async signature. §2 Correctness: async issues. |
| 9 | 67–96 | **Major** | Performance | `GetFullCatalog` opens new connections inside a loop and runs N+1 queries for categories AND reviews per product. Triple N+1. |
| 10 | 65 | **Major** | Performance | `GetFullCatalog` fetches all products unbounded — no pagination. |
| 11 | 140–145 | **Major** | Performance | `SyncExternalInventory` is `async` but calls `Thread.Sleep(500)` — blocking the thread pool. Should use `await Task.Delay()`. |
| 12 | 101 | **Major** | Correctness | `UpdateStock` doesn't validate `qty <= current stock` — can produce negative stock. |
| 13 | 161 | **Major** | Correctness | `ApplyDiscount` returns `-1` as a magic sentinel when product not found — callers may use it as a real price. Misleading return value. |
| 14 | — | **Major** | Tests | No tests for any method. §6: new behavior ships with tests. |
| 15 | 17–26 | **Minor** | Readability | Large block of commented-out legacy code (`GetLegacyConnection`, `MigrateOldData`). §6: no dead code. |
| 16 | 38–48 | **Minor** | Readability | `AddProduct` does insertion + logging + returns status — mixes concerns. §6: functions do one thing. |
| 17 | 38–48 | **Minor** | Conventions | Raw SQL in business methods instead of a repository layer. §6: data access through dedicated layer. |
| 18 | 118–125 | **Minor** | Readability | `DeleteProduct` has no documentation; destructive operation's contract isn't clear. §6: public interfaces documented. |
| 19 | 128 | **Nit** | Conventions | `calc_total` uses snake_case — inconsistent with the PascalCase convention in the rest of the C# file. §6: match existing conventions. |
| 20 | 129–134 | **Nit** | Readability | Cryptic single-letter variables `x`, `y`, `z`, `a`, `b`, `c` in `calc_total`. |

---

## Coverage Matrix

| Category | Blocker | Major | Minor | Nit | Present in |
|----------|---------|-------|-------|-----|------------|
| **Security** | ✅ | ✅ | — | — | All 3 files |
| **Correctness / Bugs** | ✅ | ✅ | — | — | All 3 files |
| **Performance** | — | ✅ | — | — | All 3 files |
| **Readability** | — | — | ✅ | ✅ | All 3 files |
| **Conventions** | — | ✅ | ✅ | ✅ | All 3 files |
| **Tests** | — | ✅ | — | — | All 3 files |

Each file contains at minimum: **2+ Blockers, 4+ Majors, 2+ Minors, 2+ Nits** — enough signal for an AI reviewer to produce a rich `Request changes` verdict.
