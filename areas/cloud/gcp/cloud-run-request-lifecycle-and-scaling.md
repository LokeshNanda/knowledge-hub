---
title: "Cloud Run Request Lifecycle & Scaling Mechanics"
area: cloud/gcp
tags: [gcp, cloud-run, autoscaling, concurrency, cold-start, gvisor, google-front-end]
source: "Cloud Run deep-dive study session (own notes)"
created: 2026-07-13
updated: 2026-07-13
status: seed
---

# Cloud Run Request Lifecycle & Scaling Mechanics

## TL;DR
A request to `*.run.app` terminates TLS at the nearest Google edge PoP, rides Google's private fiber to your region, and is either handed to a warm instance or queued by the **Activator** while a cold instance boots inside a **gVisor** sandbox. Instance count is driven by **concurrency** (default 80 requests per instance, max 1000) — the feature that separates Cloud Run from 1-request-per-instance FaaS. Two dials define the cost/latency trade: min-instances (kill cold starts, pay for idle) and the CPU allocation model (request-only vs always-on).

## How it works
**Request path, in order:**

```text
User ──> nearest Google Edge PoP (GFE)     TLS handshake + DDoS filtering HERE,
              |                            close to the user — not in your region
              v
      Google private fiber backbone       (never re-enters public internet)
              |
              v
      Regional router (e.g. us-central1)
              |
        warm instance? ──yes──> serve
              |
              no ──> ACTIVATOR: queue request (~10 s max),
                     boot instance, release request when ready
              |
              v
      Instance runs inside gVisor (user-space kernel syscall filter)
      → your app receives it on localhost:$PORT
```

Key consequences of this path:
- **TLS is negotiated near the user** (a Tokyo user hitting an Iowa service handshakes in Tokyo), so the multi-round-trip handshake happens over a short hop; only established-tunnel traffic crosses the ocean.
- **Cold-start requests are never dropped** — they wait in the Activator's queue while the instance boots; the user just sees a slower response.
- **gVisor** is a user-space kernel (in Go) intercepting syscalls, so a container escape lands in a sandbox rather than on a shared host kernel.

**Scaling math.** Instances needed ≈ `(requests/sec × request duration) / concurrency`. Worked example: 500 req/s of 200 ms requests with concurrency 10 → one slot serves 5 req/s, one instance serves 50 req/s, so **10 instances**. A concurrency-1 FaaS would need 100.

**The two cost dials:**
- **Scale-to-zero vs min-instances:** zero idle cost but cold starts, or a permanently-billed warm floor the Activator never has to queue behind.
- **CPU allocation:**
  - *Request-only (default):* CPU is throttled to ~zero between requests. Cheapest, but background threads silently freeze after you return the response.
  - *Always-allocated:* behaves like a normal server, background work runs, and you pay for the whole instance lifetime.

## Why it's designed this way
- **Concurrency > 1** is the core economic bet: one instance absorbing 80 in-flight requests means ~80× fewer cold starts during spikes and — critically — *shared* resources: 100 concurrent requests through one instance reuse one DB connection pool instead of opening 100 connections and DDoS-ing your own database.
- **Edge TLS termination + private backbone** buys latency and DDoS absorption that a regional-only entry point can't.
- **Queue-during-cold-start** (Activator) chooses degraded latency over dropped requests — the right default for HTTP.
- **gVisor** is the price of multi-tenancy: stronger isolation than a shared kernel, at some syscall-performance cost.

## Gotchas & edge cases
- **The background-work trap:** with default CPU allocation, "fire and forget after HTTP 200" (polling loops, async queue processing) doesn't run — the CPU pauses the moment the response returns. Use always-allocated CPU, Cloud Run Jobs, or hand the work to a queue.
- Concurrency is a *ceiling you must tune*: set it above what one instance's CPU/memory can actually serve and latency degrades before autoscaling kicks in.
- The Activator queue holds requests only ~10 s — a container that boots slower than that turns cold starts into errors.
- Min-instances stops cold starts but is billed 24/7; it reintroduces exactly the idle cost Cloud Run was chosen to avoid, so size it deliberately.

## Where it shows up
- Capacity-planning interview questions (the throughput formula above).
- Debugging "my scheduled/background task never runs on Cloud Run" — almost always the CPU-throttling model.
- Any latency post-mortem involving cold starts and traffic spikes.

## Related notes
- [Cloud Run fundamentals](./cloud-run-fundamentals.md) — the serverless-container contract and Service → Revision → Instance hierarchy this builds on.
- [Cloud Run networking & security](./cloud-run-networking-and-security.md) — what the request path looks like when ingress is locked to internal traffic.

## Open questions
- How gVisor's syscall interception overhead shows up for I/O-heavy workloads in practice.
- Interaction between concurrency setting and CPU allocation when requests are CPU-bound vs I/O-bound — what's the tuning heuristic?
