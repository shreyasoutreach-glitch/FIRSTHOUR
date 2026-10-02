# PRIMHORA Integrations

Reviewed against the current code and deployment topology on 2 October 2026.

## Current live topology

- UI: Vercel, canonical production domain: https://primhora.vercel.app
- API: Render, canonical service origin: https://firsthour-inei.onrender.com
- Vercel /api/* rewrite: routes to the Render API.
- Production frontend authentication: OIDC Authorization Code + PKCE when VITE_AUTH_REQUIRED=true and the client variables are configured.
- Current public deployment remains in explicitly labelled demo-capable mode. Do not use it for real customer financial data.

## Razorpay-shaped data model

PRIMHORA includes Razorpay-shaped payment vocabulary in its schema and can support a RazorpayX-shaped provider adapter.

That does not mean there is a current commercial partnership, live account connection, or production customer integration.

Provider credentials are server-side only:

- RAZORPAY_KEY_ID
- RAZORPAY_KEY_SECRET
- RAZORPAY_ACCOUNT_NUMBER
- RAZORPAY_MERCHANT_ID
- RAZORPAY_WEBHOOK_SECRET

## Webhooks

The backend exposes /api/webhooks/razorpay and verifies webhook signatures using HMAC-SHA256 before accepting a supported payload.

The current webhook configuration is not yet tenant-aware. See PRODUCTION_DISCREPANCIES.md before enabling this path for external customers.

## Evidence extraction

Text-bearing PDFs are parsed locally with pypdf.

Images and scanned PDFs can use the Gemini multimodal provider when GEMINI_API_KEY is configured.

Model output is always candidate evidence. Amounts and other financial facts must still be grounded against canonical financial-event records before being marked VERIFIED.

Without a vision key, image/scanned-PDF artifacts can be stored and hashed but are not interpreted.

## Recovery boundary

The current PRIMHORA recovery workflow is read-only.

It can propose, review, approve, dry-run, prepare and verify a recovery command and its evidence packet, but the /execute route deliberately returns HTTP 409 and performs no external financial action.

Do not describe the current build as capable of cancelling, freezing, reversing or recovering live funds.

## Production credential boundary

Never put Razorpay, Gemini, database or OIDC server secrets into frontend environment variables.

Before enabling real customer data, close the production gates in PRODUCTION_DISCREPANCIES.md:
authentication, durable evidence storage, membership provisioning, provider integration, rate limiting, observability, migrations-only schema lifecycle and deployed-browser smoke verification.
