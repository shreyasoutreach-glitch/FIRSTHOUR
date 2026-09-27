"""RazorpayX live integration.

No simulated success lives here. If credentials/account_number are missing, the
adapter fails closed. Read/sync uses the public Razorpay REST API and maps
RazorpayX payouts into FIRST HOUR's canonical payout/contact/fund-account rows.
Queued payouts can be cancelled through the documented payout cancellation API.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
import os
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://api.razorpay.com/v1"


class RazorpayXNotConfigured(RuntimeError):
    pass


class RazorpayXAPIError(RuntimeError):
    def __init__(self, status: int, detail: str):
        super().__init__(f"Razorpay API {status}: {detail}")
        self.status = status
        self.detail = detail


def configured() -> bool:
    return bool(
        os.environ.get("RAZORPAY_KEY_ID")
        and os.environ.get("RAZORPAY_KEY_SECRET")
        and os.environ.get("RAZORPAY_ACCOUNT_NUMBER")
    )


def _credentials() -> tuple[str, str, str]:
    key_id = os.environ.get("RAZORPAY_KEY_ID", "")
    secret = os.environ.get("RAZORPAY_KEY_SECRET", "")
    account = os.environ.get("RAZORPAY_ACCOUNT_NUMBER", "")
    if not key_id or not secret or not account:
        raise RazorpayXNotConfigured(
            "RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET and RAZORPAY_ACCOUNT_NUMBER are required"
        )
    return key_id, secret, account


def _request(method: str, path: str, *, query: dict | None = None, body: dict | None = None) -> dict:
    key_id, secret, _ = _credentials()
    url = f"{BASE_URL}{path}"
    if query:
        url += "?" + urlencode(query)
    auth = base64.b64encode(f"{key_id}:{secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
        "User-Agent": "FIRST-HOUR/1.0",
    }
    payload = None
    if body is not None:
        payload = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"

    try:
        with urlopen(Request(url, data=payload, headers=headers, method=method), timeout=20) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RazorpayXAPIError(exc.code, detail) from exc
    except URLError as exc:
        raise RazorpayXAPIError(503, str(exc.reason)) from exc


def fetch_payout(payout_id: str) -> dict:
    return _request("GET", f"/payouts/{payout_id}")


def fetch_payouts(*, count: int = 100, skip: int = 0) -> list[dict]:
    _, _, account = _credentials()
    response = _request(
        "GET",
        "/payouts",
        query={"account_number": account, "count": min(max(count, 1), 100), "skip": max(skip, 0)},
    )
    return list(response.get("items", []))


def cancel_queued_payout(payout_id: str) -> dict:
    """Cancel a queued payout. Razorpay rejects cancellation of other states."""
    payout = fetch_payout(payout_id)
    if payout.get("status") != "queued":
        raise RazorpayXAPIError(
            409,
            json.dumps({
                "message": "Only queued RazorpayX payouts can be cancelled.",
                "payout_status": payout.get("status"),
                "payout_id": payout_id,
            }),
        )
    return _request("POST", f"/payouts/{payout_id}/cancel")


def verify_webhook_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")


def unix_to_datetime(value) -> dt.datetime:
    if not value:
        return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    return dt.datetime.fromtimestamp(int(value), tz=dt.timezone.utc).replace(tzinfo=None)


def decimal_amount(value) -> Decimal:
    return Decimal(str(value or 0))


def normalize_payout(raw: dict) -> dict:
    fund = raw.get("fund_account") or {}
    contact = fund.get("contact") or {}
    vpa = fund.get("vpa") or {}
    bank = fund.get("bank_account") or {}
    return {
        "external_id": raw.get("id", ""),
        "amount": decimal_amount(raw.get("amount")),
        "currency": raw.get("currency", "INR"),
        "purpose": raw.get("purpose", "vendor_bill"),
        "mode": raw.get("mode", ""),
        "narration": raw.get("narration", ""),
        "reference_id": raw.get("reference_id", ""),
        "status": raw.get("status", "unknown"),
        "created_at": unix_to_datetime(raw.get("created_at")),
        "contact_id": contact.get("id", raw.get("contact_id", "")),
        "contact_name": contact.get("name", "Unknown beneficiary"),
        "contact_type": contact.get("type", "vendor"),
        "phone": contact.get("contact", ""),
        "email": contact.get("email", ""),
        "fund_account_id": fund.get("id", raw.get("fund_account_id", "")),
        "account_type": fund.get("account_type", "bank_account"),
        "vpa": vpa.get("address", ""),
        "masked_bank_account": bank.get("account_number", ""),
        "masked_ifsc": bank.get("ifsc", ""),
    }
