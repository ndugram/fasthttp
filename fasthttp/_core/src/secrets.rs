use once_cell::sync::Lazy;
use pyo3::prelude::*;
use regex::Regex;
use std::collections::{HashMap, HashSet};

static SECRET_HEADERS_SET: Lazy<HashSet<&'static str>> = Lazy::new(|| {
    HashSet::from([
        "authorization",
        "x-api-key",
        "x-auth-token",
        "x-access-token",
        "cookie",
        "set-cookie",
        "proxy-authorization",
        "www-authenticate",
    ])
});

static SECRET_PARAM_RE: Lazy<Regex> = Lazy::new(|| {
    Regex::new(
        r"(?i)api[_-]?key|token|password|secret|auth|bearer|credential|private[_-]?key|access[_-]?key|session[_-]?id",
    )
    .unwrap()
});

static MASK_BEARER_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)(Bearer\s+)[a-zA-Z0-9\-_.~+/]+=*").unwrap());
static MASK_BASIC_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)(Basic\s+)[a-zA-Z0-9+/]+=*").unwrap());
static MASK_TOKEN_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)(token[=:]\s*)[^\s&]+").unwrap());
static MASK_APIKEY_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)(api[_-]?key[=:]\s*)[^\s&]+").unwrap());
static MASK_PASSWORD_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)(password[=:]\s*)[^\s&]+").unwrap());
static MASK_SECRET_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)(secret[=:]\s*)[^\s&]+").unwrap());

const COOKIE_SENSITIVE: &[&str] = &["session", "token", "id", "key", "auth"];

/// Mask sensitive cookie name=value pairs, leaving non-sensitive ones unchanged.
#[pyfunction]
pub fn mask_cookie(cookie: &str) -> String {
    let parts: Vec<&str> = cookie.split(';').collect();
    let masked: Vec<String> = parts
        .iter()
        .map(|part| {
            if let Some(eq_pos) = part.find('=') {
                let name = part[..eq_pos].trim();
                let name_lower = name.to_lowercase();
                if COOKIE_SENSITIVE.iter().any(|p| name_lower.contains(p)) {
                    format!("{}=*****", name)
                } else {
                    part.to_string()
                }
            } else {
                part.to_string()
            }
        })
        .collect();
    masked.join("; ")
}

/// Mask secret HTTP headers (Authorization, Cookie, etc.) for safe logging.
#[pyfunction]
pub fn mask_headers(headers: HashMap<String, String>) -> HashMap<String, String> {
    headers
        .into_iter()
        .map(|(key, value)| {
            let key_lower = key.to_lowercase();
            let masked = if SECRET_HEADERS_SET.contains(key_lower.as_str()) {
                if key_lower == "cookie" || key_lower == "set-cookie" {
                    mask_cookie(&value)
                } else {
                    "*****".to_string()
                }
            } else {
                value
            };
            (key, masked)
        })
        .collect()
}

/// Apply regex-based secret masking to a log message string.
#[pyfunction]
pub fn mask_log_message(message: &str) -> String {
    let r = MASK_BEARER_RE.replace_all(message, "${1}*****");
    let r = MASK_BASIC_RE.replace_all(r.as_ref(), "${1}*****");
    let r = MASK_TOKEN_RE.replace_all(r.as_ref(), "${1}*****");
    let r = MASK_APIKEY_RE.replace_all(r.as_ref(), "${1}*****");
    let r = MASK_PASSWORD_RE.replace_all(r.as_ref(), "${1}*****");
    let r = MASK_SECRET_RE.replace_all(r.as_ref(), "${1}*****");
    r.into_owned()
}

/// Return True if the key name matches known secret parameter patterns.
#[pyfunction]
pub fn should_mask_value(key: &str) -> bool {
    SECRET_PARAM_RE.is_match(key)
}
