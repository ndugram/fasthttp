use pyo3::prelude::*;
use url::Url;

/// Pure URL-side redirect safety check (no DNS resolution).
/// redirect_count is already incremented before calling.
/// Returns (allowed: bool, reason: str | None).
#[pyfunction]
pub fn check_redirect_url(
    original_url: &str,
    redirect_url: &str,
    redirect_count: usize,
    max_hops: usize,
    block_file: bool,
    block_javascript: bool,
    allow_http_downgrade: bool,
) -> (bool, Option<String>) {
    if redirect_count > max_hops {
        return (
            false,
            Some(format!("Too many redirects (max: {})", max_hops)),
        );
    }

    let scheme = match Url::parse(redirect_url) {
        Ok(u) => u.scheme().to_lowercase(),
        Err(_) => {
            return (
                false,
                Some(format!("Invalid redirect URL: {}", redirect_url)),
            )
        }
    };

    if block_file && scheme == "file" {
        return (
            false,
            Some("Redirect to file:// protocol is blocked".to_string()),
        );
    }

    if block_javascript && (scheme == "javascript" || scheme == "data") {
        return (
            false,
            Some(format!("Redirect to {}:// protocol is blocked", scheme)),
        );
    }

    // Match Python's check_redirect behavior exactly (allow_http_downgrade=True blocks downgrades)
    if allow_http_downgrade && scheme == "http" {
        if let Ok(orig) = Url::parse(original_url) {
            if orig.scheme().to_lowercase() == "https" {
                return (
                    false,
                    Some("HTTP downgrade not allowed (HTTPS -> HTTP)".to_string()),
                );
            }
        }
    }

    (true, None)
}
