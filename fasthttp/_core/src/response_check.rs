use once_cell::sync::Lazy;
use pyo3::prelude::*;
use std::collections::HashSet;

use crate::xss::detect_xss;

static DANGEROUS_CONTENT_TYPES: Lazy<HashSet<&'static str>> =
    Lazy::new(|| HashSet::from(["text/html", "application/xhtml+xml"]));

/// Check response body size against max_size_mb. Returns (ok, reason_or_None).
#[pyfunction]
pub fn check_response_size(size_bytes: usize, max_size_mb: usize) -> (bool, Option<String>) {
    let max_bytes = max_size_mb * 1024 * 1024;
    if size_bytes > max_bytes {
        return (
            false,
            Some(format!(
                "Response too large: {} bytes (max: {})",
                size_bytes, max_bytes
            )),
        );
    }
    (true, None)
}

/// Validate content-type against dangerous types and optional allowlist.
/// Returns (ok, reason_or_None).
#[pyfunction]
pub fn check_content_type(
    content_type: &str,
    expected_type: Option<&str>,
    block_dangerous: bool,
    allowed_types: Option<Vec<String>>,
) -> (bool, Option<String>) {
    if content_type.is_empty() {
        return (true, None);
    }

    let ct_lower = content_type
        .to_lowercase()
        .split(';')
        .next()
        .unwrap_or("")
        .trim()
        .to_string();

    if block_dangerous
        && DANGEROUS_CONTENT_TYPES.contains(ct_lower.as_str())
        && expected_type.is_some()
        && expected_type.map(|e| e.to_lowercase()).as_deref() != Some(&ct_lower)
    {
        return (
            false,
            Some(format!(
                "Unexpected content type: expected {}, got {}",
                expected_type.unwrap_or(""),
                ct_lower
            )),
        );
    }

    if let Some(allowed) = allowed_types {
        let allowed_lower: HashSet<String> = allowed.iter().map(|s| s.to_lowercase()).collect();
        if !allowed_lower.contains(&ct_lower) {
            return (false, Some(format!("Content type {} not allowed", ct_lower)));
        }
    }

    (true, None)
}

/// Full response validation: size check → content-type check → XSS scan.
/// Returns (ok, reason_or_None).
#[pyfunction]
pub fn validate_response(
    content: &[u8],
    content_type: Option<&str>,
    max_size_mb: usize,
    block_dangerous_content: bool,
    allowed_types: Option<Vec<String>>,
) -> (bool, Option<String>) {
    let (ok, reason) = check_response_size(content.len(), max_size_mb);
    if !ok {
        return (false, reason);
    }

    if let Some(ct) = content_type {
        if !ct.is_empty() {
            let (ok, reason) =
                check_content_type(ct, None, block_dangerous_content, allowed_types);
            if !ok {
                return (false, reason);
            }
        }
    }

    // Skip XSS scan for markup content types — scripts/events are expected there.
    // XSS detection is only meaningful for non-markup API responses (e.g. JSON).
    let is_markup = content_type.map_or(false, |ct| {
        let ct_lower = ct.to_lowercase();
        ct_lower.contains("html")
            || ct_lower.contains("xml")
            || ct_lower.contains("rss")
            || ct_lower.contains("atom")
    });

    if !is_markup && content.contains(&b'<') && content.contains(&b'>') {
        if let Ok(text) = std::str::from_utf8(content) {
            let (found, reason) = detect_xss(text);
            if found {
                return (false, reason);
            }
        } else {
            let text = String::from_utf8_lossy(content);
            let (found, reason) = detect_xss(&text);
            if found {
                return (false, reason);
            }
        }
    }

    (true, None)
}
