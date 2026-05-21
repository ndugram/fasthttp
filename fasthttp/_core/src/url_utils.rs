use md5;
use once_cell::sync::Lazy;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use regex::Regex;
use url::Url;
use std::collections::HashMap;

static CSS_RE: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r#"(?i)<link[^>]+rel=["']stylesheet["'][^>]+href=["']([^"']+)["']"#).unwrap()
});

static JS_RE: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r#"(?i)<script[^>]+src=["']([^"']+)["']"#).unwrap()
});

pub(crate) fn urljoin(base: &str, path: &str) -> String {
    match Url::parse(base) {
        Ok(base_url) => match base_url.join(path) {
            Ok(joined) => joined.to_string(),
            Err(_) => path.to_string(),
        },
        Err(_) => path.to_string(),
    }
}

/// Ensure URL has an explicit https:// or http:// scheme.
#[pyfunction]
pub fn check_https_url(url: &str) -> String {
    let url = url.trim();
    if url.starts_with("https://") || url.starts_with("http://") {
        return url.to_string();
    }
    format!("https://{url}")
}

/// Join a path prefix with a URL fragment, normalising slashes.
#[pyfunction]
pub fn join_prefix(prefix: &str, url: &str) -> String {
    let mut prefix = prefix.trim().to_string();
    let mut url = url.trim().to_string();

    if prefix.is_empty() {
        return url;
    }

    if !prefix.starts_with('/') {
        prefix = format!("/{prefix}");
    }
    if prefix != "/" && prefix.ends_with('/') {
        prefix.pop();
    }

    if !url.starts_with('/') {
        url = format!("/{url}");
    }

    if url == "/" {
        return if prefix.is_empty() {
            "/".to_string()
        } else {
            prefix
        };
    }

    format!("{prefix}{url}")
}

/// Resolve a route URL against an optional base_url and prefix.
#[pyfunction]
pub fn resolve_url(url: &str, base_url: Option<&str>, prefix: &str) -> PyResult<String> {
    let url = url.trim();

    if url.starts_with("https://") || url.starts_with("http://") {
        return Ok(url.to_string());
    }

    let Some(base) = base_url else {
        if url.starts_with('/') {
            return Err(PyValueError::new_err(format!(
                "Relative URL requires base_url. Got url={url:?} without base_url."
            )));
        }
        return Ok(check_https_url(url));
    };

    let base = check_https_url(base);
    let base_with_slash = format!("{}/", base.trim_end_matches('/'));
    let joined = join_prefix(prefix, url);
    let path = joined.trim_start_matches('/');

    Ok(urljoin(&base_with_slash, path))
}

/// Resolve a URL against an optional base URL (no prefix logic).
#[pyfunction]
pub fn apply_base_url(url: &str, base_url: Option<&str>) -> String {
    let url = url.trim();

    if url.starts_with("https://") || url.starts_with("http://") {
        return url.to_string();
    }

    match base_url {
        Some(base) if !base.is_empty() => check_https_url(&format!(
            "{}/{}",
            base.trim_end_matches('/'),
            url.trim_start_matches('/')
        )),
        _ => check_https_url(url),
    }
}

/// Extract CSS and JS asset URLs from an HTML string.
#[pyfunction]
pub fn extract_assets(html: &str, base_url: &str) -> HashMap<String, Vec<String>> {
    let css: Vec<String> = CSS_RE
        .captures_iter(html)
        .filter_map(|cap| cap.get(1))
        .map(|m| urljoin(base_url, m.as_str()))
        .collect();

    let js: Vec<String> = JS_RE
        .captures_iter(html)
        .filter_map(|cap| cap.get(1))
        .map(|m| urljoin(base_url, m.as_str()))
        .collect();

    HashMap::from([("css".to_string(), css), ("js".to_string(), js)])
}

/// Generate a cache key: MD5( "METHOD:url:sorted_params_json" ).
#[pyfunction]
pub fn cache_key(method: &str, url: &str, params_json: &str) -> String {
    let raw = format!("{method}:{url}:{params_json}");
    format!("{:x}", md5::compute(raw.as_bytes()))
}
