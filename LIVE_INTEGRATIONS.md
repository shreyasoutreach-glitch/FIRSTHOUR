# FIRST HOUR Live Integrations

The deployed system fails closed when live provider credentials are absent. It never reports a live connection or successful recovery action from mock data.

## RazorpayX

Set these backend environment variables on Render:

- `RAZORPAY_KEY_ID`
- `RAZORPAY_KEY_SECRET`
- `RAZORPAY_ACCOUNT_NUMBER`
- `RAZORPAY_MERCHANT_ID`
- `RAZORPAY_WEBHOOK_SECRET`

With the first three configured, FIRST HOUR can fetch the RazorpayX payout ledger and normalize payouts into its canonical financial model.

With the webhook values configured, POST Razorpay payout webhooks to:

`/api/webhooks/razorpay`

Webhook signatures are verified using HMAC-SHA256 before the payload is accepted.

### Live recovery

`FREEZE_PAYOUT` can execute against a real RazorpayX payout when:

1. the command has passed FIRST HOUR's existing propose -> review -> approve state machine;
2. the target payout is actually in RazorpayX's `queued` state;
3. RazorpayX credentials are configured.

The provider operation is the documented queued-payout cancellation endpoint.

`REVERSE_PAYOUT` remains a manual recovery path for processed payouts. FIRST HOUR does not claim that a processed RazorpayX payout can be cancelled through the queued-payout API.

## Evidence extraction

Text evidence is processed deterministically.

Text-bearing PDFs are parsed with `pypdf`.

Images and scanned PDFs can use Gemini multimodal extraction when:

- `GEMINI_API_KEY` is configured.

Gemini output is treated as candidate evidence only. Amount claims are still cross-referenced against the canonical financial-event table before they can be marked VERIFIED.

Without a vision key, image/scanned-PDF artifacts are stored and hashed but are not interpreted.

## Current deployed surfaces

- API: `https://firsthour-inei.onrender.com`
- UI: `https://firsthour-ui-n4cc.onrender.com`

The UI is configured with the API's Render URL at build time. The backend CORS configuration includes the Render UI origin.

## Security boundary

Do not put Razorpay or Gemini secrets in frontend environment variables. The frontend only calls authenticated backend endpoints. Provider credentials remain server-side on Render.
