"""Webhook service - HMAC signature verification for result ingestion."""
import hmac
import hashlib
from time import time


def verify_webhook_signature(payload: str, sig_header: str, secret: str, max_age: int = 300) -> bool:
    """Verify webhook signature using HMAC-SHA256.
    
    Expected header format: t={unix_timestamp},v1={hex_signature}
    Signature: HMAC-SHA256(secret, f"{timestamp}.{payload}")
    
    Args:
        payload: Raw request body as string
        sig_header: X-Signature header value
        secret: HMAC secret
        max_age: Maximum age of request in seconds (default 300 = 5 minutes)
    
    Returns:
        True if signature is valid and timestamp is fresh, False otherwise
    """
    # Parse header
    parts = {}
    for part in sig_header.split(","):
        k, v = part.split("=", 1)
        parts[k] = v
    
    ts_str = parts.get("t")
    signature = parts.get("v1")
    
    if not ts_str or not signature:
        return False
    
    try:
        ts = int(ts_str)
    except ValueError:
        return False
    
    # Check age
    now = int(time())
    if abs(now - ts) > max_age:
        return False
    
    # Verify signature
    msg = f"{ts_str}.{payload}".encode()
    expected_sig = hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()
    
    # Timing-safe comparison
    return hmac.compare_digest(signature, expected_sig)
