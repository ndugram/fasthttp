use once_cell::sync::Lazy;
use pyo3::prelude::*;
use std::collections::{HashMap, HashSet};

static DANGEROUS_RESPONSE_HEADERS: Lazy<HashSet<&'static str>> = Lazy::new(|| {
    HashSet::from([
        "x-accel-redirect",
        "x-sendfile",
        "x-accel-limit-rate",
        "x-ratelimit-limit",
        "x-ratelimit-remaining",
        "refresh",
        "content-security-policy",
        "content-security-policy-report-only",
    ])
});

static BLOCKED_REQUEST_HEADERS: Lazy<HashSet<&'static str>> = Lazy::new(|| {
    HashSet::from([
        "host",
        "content-length",
        "transfer-encoding",
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "upgrade",
    ])
});

#[inline]
fn has_crlf(s: &str) -> bool {
    s.contains('\r') || s.contains('\n')
}

fn sanitize_name(name: &str) -> Option<String> {
    let cleaned: String = name.trim().chars().filter(|&c| c != '\r' && c != '\n').collect();
    if cleaned.is_empty() || BLOCKED_REQUEST_HEADERS.contains(cleaned.to_lowercase().as_str()) {
        None
    } else {
        Some(cleaned)
    }
}

fn sanitize_value(value: &str) -> Option<String> {
    let cleaned: String = value.trim().chars().filter(|&c| c != '\r' && c != '\n').collect();
    if cleaned.is_empty() { None } else { Some(cleaned) }
}

fn check_cookie_security(cookie: &str) -> (bool, Option<String>) {
    let lower = cookie.to_lowercase();
    let parts: Vec<&str> = lower.split(';').collect();
    let has_secure = parts.iter().any(|p| p.trim() == "secure");
    let has_samesite = parts.iter().any(|p| p.trim().starts_with("samesite"));
    if has_samesite {
        for part in &parts {
            if part.contains("samesite=none") && !has_secure {
                return (
                    false,
                    Some("Cookie with SameSite=None without Secure flag".to_string()),
                );
            }
        }
    }
    (true, None)
}

/// Remove CRLF injection and blocked headers from request headers dict.
#[pyfunction]
pub fn sanitize_request_headers(headers: HashMap<String, String>) -> HashMap<String, String> {
    headers
        .into_iter()
        .filter_map(|(key, value)| {
            let k = sanitize_name(&key)?;
            let v = sanitize_value(&value)?;
            Some((k, v))
        })
        .collect()
}

/// Check response headers for dangerous headers, CRLF, and cookie security.
/// Returns (ok: bool, error: str | None).
#[pyfunction]
pub fn check_response_headers(headers: HashMap<String, String>) -> (bool, Option<String>) {
    for (key, value) in &headers {
        let key_lower = key.to_lowercase();
        if DANGEROUS_RESPONSE_HEADERS.contains(key_lower.as_str()) {
            return (false, Some(format!("Dangerous header detected: {}", key)));
        }
        if has_crlf(value) {
            return (false, Some(format!("CRLF injection detected in header: {}", key)));
        }
        if key_lower == "set-cookie" {
            let check = check_cookie_security(value);
            if !check.0 {
                return check;
            }
        }
    }
    (true, None)
}
