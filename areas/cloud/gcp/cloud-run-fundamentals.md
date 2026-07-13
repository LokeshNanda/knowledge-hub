---
title: "Cloud Run Fundamentals: Serverless Containers, Services, Revisions"
area: cloud/gcp
tags: [gcp, cloud-run, serverless, containers, knative, deployment-model]
source: "Cloud Run deep-dive study session (own notes)"
created: 2026-07-13
updated: 2026-07-13
status: seed
---

# Cloud Run Fundamentals: Serverless Containers, Services, Revisions

## TL;DR
Cloud Run runs any OCI container as a serverless workload: bring an image that listens for HTTP on `$PORT`, and Google handles scaling — including down to zero. It sits between Cloud Functions (zero ops, but locked runtimes) and GKE (any binary, but you pay for and manage idle nodes). Deployments are organized as **Service → Revision → Instance**, where revisions are immutable snapshots, making rollbacks and canary traffic splits trivial.

## How it works
**The contract.** Cloud Run is language-agnostic; it only demands four things of your container:
1. Packaged as a standard OCI image.
2. Starts an HTTP server on the port given in the `$PORT` env var (default 8080).
3. Stateless — local disk and memory can vanish after any request.
4. Boots fast enough to serve within seconds, or deployment health checks fail.

**The compute spectrum** (constraints decrease going down, ops burden increases):

```text
Cloud Functions   — code only, fixed runtimes, no custom system libs
CLOUD RUN         — any container + HTTP listener, serverless ops   <-- sweet spot
GKE               — full orchestration, you shape the cluster
Compute Engine    — raw VMs, full ops
```

**Resource hierarchy.**
- **Service** — the stable, managed endpoint (`https://<name>-xyz.a.run.app`). Owns IAM, custom domains, and the traffic-split rules deciding which revision serves requests.
- **Revision** — created on *every* deploy; strictly **immutable**. A revision freezes the image digest, env vars, and CPU/RAM limits together. Changing even one env var mints a new revision. Rollback = repoint traffic at an old revision, instantaneous.
- **Instance** — the ephemeral micro-VM actually running your container. Created on demand, destroyed when idle; not SSH-able. You control scaling *rules*, never individual instances.
- **Job** (sibling resource) — runs a container to completion with no HTTP listener; for migrations and batch work.

Deploys are effectively automatic blue/green: new traffic shifts to the new revision while in-flight requests on the old revision finish gracefully before it scales down.

## Why it's designed this way
- **Container-as-contract** dodges both failure modes of the older extremes: FaaS runtime lock-in (no Fortran, no `lib-obscure.so`) and Kubernetes' pay-for-idle-nodes economics. Anything you can containerize runs, yet the bill is $0 when idle.
- **Immutable revisions** trade a tiny bit of deploy friction ("why didn't my env var update in place?") for exact reproducibility, instant rollback, and safe percentage-based canaries — the same reasoning as immutable infrastructure generally.
- **Knative heritage:** Cloud Run is Google's managed implementation of the open-sourced Knative Serving API. Deployment YAML is (mostly) portable to any Knative installation — GKE, OpenShift, even other clouds — so lock-in lives at the operational layer, not the API.

## Gotchas & edge cases
- Updating configuration **never** mutates the running revision — a new revision is always created. If you script deploys, don't assume revision names are stable.
- Statelessness is a hard assumption: anything written to the writable filesystem lives in instance memory and dies with the instance.
- The default choice of Service vs Job matters: a Service that does batch work "after responding" fights the platform (see CPU throttling in the scaling note).

## Where it shows up
- Classic fit: an occasional workload with exotic dependencies — e.g. a legacy Fortran binary needing a 10-year-old system library, triggered by file uploads. Cloud Functions can't host the runtime; GKE bills for idle nodes; Cloud Run runs it on demand for effectively $0 between uploads.
- Interview framing: "compare FaaS vs serverless containers vs Kubernetes" — the contract + hierarchy above is the answer skeleton.

## Related notes
- [Cloud Run request lifecycle & scaling](./cloud-run-request-lifecycle-and-scaling.md) — what happens between a user's request and your container, and how instance counts are decided.
- [Cloud Run networking & security](./cloud-run-networking-and-security.md) — ingress/egress control and service identity.

## Open questions
- How the container health-check / startup-probe configuration interacts with "fast startup" in practice (startup CPU boost?).
- Exact portability limits of Cloud Run YAML vs upstream Knative ("mostly works" — what breaks?).
