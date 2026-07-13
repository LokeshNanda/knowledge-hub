# Cloud / GCP — map of content

## Serverless compute: Cloud Run
- [Cloud Run fundamentals](../areas/cloud/gcp/cloud-run-fundamentals.md) — serverless-container contract ($PORT, stateless, fast boot), Knative heritage, Service → immutable Revision → Instance hierarchy, Jobs, where it sits between Cloud Functions and GKE.
- [Cloud Run request lifecycle & scaling](../areas/cloud/gcp/cloud-run-request-lifecycle-and-scaling.md) — edge TLS at the GFE, private backbone, Activator queue on cold start, gVisor sandbox; concurrency-based autoscaling math, scale-to-zero vs min-instances, CPU request-only vs always-allocated trap.
- [Cloud Run networking & security](../areas/cloud/gcp/cloud-run-networking-and-security.md) — ingress All/Internal/+LB, egress via VPC connector vs Direct VPC Egress, dedicated service accounts, OIDC token + run.invoker auth; private payroll-API reference architecture.
