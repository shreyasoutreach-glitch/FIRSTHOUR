# Production Discrepancy Register

Reviewed against the current PRIMHORA repository and live Render topology on 30 September 2026.

This is an engineering gap register, not a claim that every item blocks the capstone.

## Fixed in this hardening pass

| Area | Discrepancy | Action |
|---|---|---|
| Workspace | Create organization only wrote to browser sessionStorage; no backend tenant/user was created. | Added persistent workspace provisioning API for the demo environment and wired the UI to it. |
| Frontend/API wiring | The Render static frontend had no explicit production API origin in the application configuration. | Production deployment configuration will point the frontend at the Render API URL. |
| Security headers | API responses had no application-level clickjacking, MIME-sniffing, referrer or browser-feature protections. | Added security headers middleware. |
| Health disclosure | Public health/root response exposed demo mode and configured integration presence. | Reduced health response to non-sensitive status/service fields. |
| Metrics exposure | /api/metrics and /api/evaluation were authenticated inconsistently. | Added VIEW permission enforcement. |
| Evidence integrity | Evidence upload did not verify that the supplied incident belonged to the supplied merchant. | Added merchant/incident ownership validation. |
| Vision errors | Vision extraction errors could return raw exception text to clients. | Return a generic extraction failure while retaining the artifact as unverified. |
| Deployment IaC | render.yaml contained a destructive seed command and stale Vercel CORS origins, even though the live Render service had already diverged from that file. | Removed seed-from-startup and aligned the blueprint with the Render deployment shape. |

## Still not normal for a production MVP

| Area | Current state | Required before external customer data |
|---|---|---|
| Authentication | Demo bearer sessions are still enabled on the live environment. | Activate a real OIDC provider and set DEMO_MODE=false. |
| User provisioning | OIDC lookup is currently email-based and users must already be provisioned. | Add immutable IdP subject mapping plus explicit membership provisioning. |
| Workspace membership | A user currently carries one tenant_id; the new self-service workspace path is demo-only. | Introduce durable organization membership/invitation lifecycle for production. |
| Evidence storage | Uploaded evidence is stored on local service filesystem. | Move to durable object storage or a verified persistent disk with backup/retention policy. |
| Provider coverage | Generic payout CSV is real; live provider adapters are limited. | Add and test the first customer-required provider adapter and reconciliation path. |
| Webhooks | Razorpay webhook configuration is environment-wide and tied to one merchant. | Make provider credentials/webhook routing tenant-aware and operationally managed. |
| Abuse controls | No distributed request rate limiting or abuse policy is implemented. | Add edge/app rate limiting for authentication, uploads and high-cost endpoints. |
| Observability | Basic Render logs exist, but no product-level alerting, structured audit correlation, SLOs or incident runbook are established. | Add structured logs, error tracking, alert thresholds, backup/restore drills and an incident response runbook. |
| Database migrations | Alembic exists and is run on deploy, but the application still calls Base.metadata.create_all() from seed/bootstrap code. | Keep schema lifecycle solely under migrations for production paths. |
| Deployment verification | CI verifies builds and local Docker health. Live browser verification still needs to exercise the deployed first-run and investigation flows. | Run a production smoke suite against the deployed URLs after the fixes land. |
| Frontend deployment topology | Two Render frontend services currently exist. | Select one canonical production frontend and retire the duplicate after verification. |
| Recovery | Recovery commands are deliberately simulated/read-only. | Keep this boundary explicit unless a future product decision adds separately governed execution integrations. |

## Production gate

PRIMHORA should not be described as ready for real customer financial data until the authentication, durable evidence storage, membership provisioning, provider integration, observability and deployed-browser verification gates above are closed.

The purpose of this register is to prevent a green CI badge from becoming a substitute for production engineering.
