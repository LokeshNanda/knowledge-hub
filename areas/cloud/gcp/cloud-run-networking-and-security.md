---
title: "Cloud Run Networking & Security: Ingress, Egress, Service Identity"
area: cloud/gcp
tags: [gcp, cloud-run, vpc, ingress, egress, iam, oidc, service-account]
source: "Cloud Run deep-dive study session (own notes)"
created: 2026-07-13
updated: 2026-07-13
status: seed
---

# Cloud Run Networking & Security: Ingress, Egress, Service Identity

## TL;DR
Three independent controls turn a public-by-default Cloud Run URL into an enterprise-grade private service: **ingress** settings decide who can reach it (public / internal / via load balancer), **egress** configuration decides which private networks it can reach (VPC connector vs the newer Direct VPC Egress), and **service identity** (a dedicated service account + IAM-verified OIDC tokens) decides who is *authorized* even after a packet arrives. Network position is never treated as proof of identity.

## How it works
**Ingress — "who can call me":**
- `All` — default; the `*.run.app` URL is on the public internet.
- `Internal` — only VPC traffic in the same project/perimeter and other Cloud Run services; everything else gets 403.
- `Internal + Cloud Load Balancing` — additionally admits an Application Load Balancer, the pattern for putting Cloud Armor (WAF) or custom routing in front: the ALB becomes the only door.

**Egress — "who can I call":** by default a Cloud Run container sees only the public internet; private IPs like a Cloud SQL instance at `172.16.0.5` are invisible. Two bridges exist:

| | Serverless VPC Access Connector (old) | Direct VPC Egress (new) |
|---|---|---|
| Mechanism | Hidden bridge VMs doing NAT into your VPC | Virtual NIC attached to each instance, inside your subnet |
| Idle cost | Bridge VMs billed 24/7 even at scale-to-zero | None — pay only for traffic |
| Throughput | Bottlenecked by connector size | No bridge bottleneck |
| Catch | Static-IP support | Consumes subnet IPs quickly as instances scale |

**Identity & auth:** every revision runs *as* a service account. Callers authenticate with IAM-signed identity, not network location:
1. The calling workload (e.g. a VM) asks its local metadata server for an **OIDC ID token** for its own service account.
2. It calls Cloud Run with `Authorization: Bearer <token>`.
3. Cloud Run verifies the token and checks the caller's service account holds **`roles/run.invoker`** on the service; otherwise 403.

**Reference architecture** (private, rarely-used, near-zero idle cost — e.g. a monthly payroll API):

```text
Legacy VM [vm-sa@...] ── OIDC token from metadata server
        │  Authorization: Bearer <token>
        v
Cloud Run service        ingress: Internal   auth: run.invoker required
        │
        v  Direct VPC Egress
Cloud SQL (private IP 172.16.0.5, no public IP)
```

## Why it's designed this way
- Splitting ingress, egress, and IAM into orthogonal controls means each threat is handled where it's cheapest: volumetric/public exposure at ingress, data-path reachability at egress, and authorization by cryptographic identity.
- **Direct VPC Egress replaces the connector** because bridge VMs contradicted the serverless cost model — an always-on charge under a scale-to-zero service. Attaching NICs directly removes both the cost and the throughput choke, trading it for subnet IP consumption.
- **Token-based auth even inside the VPC** is deliberate zero-trust: "on the network" is spoofable and coarse; a signed OIDC token names exactly which workload is calling.

## Gotchas & edge cases
- The **default service account** for revisions is the Compute Engine default SA, which historically carries Editor-level access — a hijacked container inherits all of it. Always create a per-service SA with only the roles it needs (`cloudsql.client`, `pubsub.publisher`, …).
- Ingress `Internal` still requires IAM auth for real security — the two layers are independent, and each alone is weaker.
- Direct VPC Egress can quietly exhaust a small subnet's IP range under burst scaling; size the subnet for max instances.
- Want Cloud Armor? That requires the ALB pattern — WAF rules cannot be attached to the bare `run.app` endpoint.

## Where it shows up
- The standard "design a private internal API on serverless" interview scenario — the payroll architecture above covers ingress, egress, and auth in one answer.
- Cost reviews: finding VPC connectors billing 24/7 under services that scale to zero.
- Security audits: services still running as the default compute SA.

## Related notes
- [Cloud Run fundamentals](./cloud-run-fundamentals.md) — the Service/Revision model that these settings attach to.
- [Cloud Run request lifecycle & scaling](./cloud-run-request-lifecycle-and-scaling.md) — the public request path (GFE, Activator) that ingress settings gate.

## Open questions
- How VPC Service Controls perimeters compose with ingress=Internal for data-exfiltration protection.
- Whether Direct VPC Egress supports static egress IPs yet (the connector's remaining advantage).
