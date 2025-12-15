---
applyTo: '**/backend/**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

## Project Overview

You are building **only the backend** for a price‑tracking application that scrapes product prices from **amazon.com** and notifies users when prices fall below their desired threshold. The backend exposes a REST API, manages scraping jobs, persists historical price data, manages users and configurations, and sends email notifications.

The system must be designed to be **maintainable, extensible, resilient to scraping failures, and scalable under concurrent load**, while remaining simple enough to run locally with SQLite.

### In Scope

* REST API design and implementation
* Amazon product scraping logic
* Concurrent job scheduling and execution
* SQLite persistence layer
* Email/password authentication
* User & product tracking configuration management
* Email notification when price thresholds are met

### Out of Scope

* Frontend or UI
* Third‑party auth providers (OAuth, SSO, etc.)
* Payment, subscriptions, or billing
* CAPTCHA‑bypass or scraping evasion services

---

## Technology Stack

* **Python 3.13+**
* **UV** (package manager & virtual environment)
* **FastAPI** (API framework)
* **requests** (HTTP client)
* **BeautifulSoup4** (HTML parsing)
* **SQLite** (database)

Do not introduce additional frameworks unless explicitly instructed.

---

## Architectural Principles

1. **Separation of concerns**

   * API layer
   * Authentication & authorization
   * Scraping layer
   * Scheduling & workers
   * Persistence layer
   * Notification layer

2. **Scalability by design**

   * Code must support concurrent scraping jobs
   * Scheduler and workers must be separable into different processes later

3. **Fail gracefully**

   * Scraping failures must not crash the system
   * Partial failures must not corrupt state

4. **Idempotency & auditability**

   * Never overwrite historical data
   * Re‑runs must not duplicate logical records

5. **Config‑driven behavior**

   * All scrape intervals, thresholds, and enable/disable flags must be data‑driven

---

## Scheduling & Concurrency Strategy

* Do **not** rely on system cron
* Implement an internal scheduler
* Scheduler must:

  * Periodically scan for due jobs
  * Dispatch jobs concurrently (async tasks or worker pool)
  * Enforce minimum scrape intervals
  * Track last run timestamps

Concurrency requirements:

* Scraping jobs must be isolated
* Failures in one job must not affect others
* Design must allow future split into API + worker services

---

## Database Design Guidelines

### Core Tables

* users
* auth_tokens (if applicable)
* products
* tracking_configs
* price_history
* scrape_runs
* notifications_sent

### Rules

* Foreign keys enforced
* Timestamps stored in UTC
* Never overwrite historical records
* SQLite access via a controlled connection manager

---

## Email Notifications

* Send email only when price crosses from above → below desired threshold
* Deduplicate notifications per user/product/price
* Email sending must be isolated from scraping logic
* Email failures must not interrupt job execution

---

## Error Handling & Logging

* Catch and classify all scraping errors
* Persist scrape status: SUCCESS / FAILED / BLOCKED
* Log actionable errors only

Do not expose internal stack traces through the API.

---

## Performance & Scaling Constraints

* Correctness over raw speed
* Avoid unnecessary re‑scraping
* Enforce global and per‑user scrape limits
* Code must remain safe under concurrent execution

---

## Security & Compliance Notes

* No plaintext secrets in code
* Sanitize all user input (especially URLs)
* Keep scraping logic modular to allow provider replacement

---

## Development Expectations

* Explicit, readable code preferred
* Docstrings for all public functions
* Async allowed where it improves concurrency
* Functions must remain small and testable

---

## Deliverables Expected From You

* Production‑ready FastAPI backend
* SQLite schema initialization
* Concurrent scheduler + workers
* Secure authentication implementation
* Email notification system
* README for local execution

---

## Assumptions

* Single‑node deployment initially
* SQLite used locally, replaceable later
* Email provider configured via environment

If any assumption is invalid, pause and request clarification before proceeding.

